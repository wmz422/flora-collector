"""
Flora Collector — 修复 (unplaced) 目标签物种
使用已知正确的分类映射直接修复
"""
import sqlite3
from collections import defaultdict

DB_PATH = "data/flora.db"

# 正确分类映射：学名(前缀) → {class, order, family, genus}
CORRECT_TAXONOMY = {
    "Sorbaria sorbifolia": {
        "class": "Magnoliopsida", "order": "Rosales",
        "family": "Rosaceae", "genus": "Sorbaria",
    },
    "Rosa xanthina": {
        "class": "Magnoliopsida", "order": "Rosales",
        "family": "Rosaceae", "genus": "Rosa",
    },
    "Wisteria floribunda": {
        "class": "Magnoliopsida", "order": "Fabales",
        "family": "Fabaceae", "genus": "Wisteria",
    },
    "Salvia pratensis": {
        "class": "Magnoliopsida", "order": "Lamiales",
        "family": "Lamiaceae", "genus": "Salvia",
    },
    "Pinus bungeana": {
        "class": "Pinopsida", "order": "Pinales",
        "family": "Pinaceae", "genus": "Pinus",
    },
}

# 新创建节点的中文名
CHINESE_NAMES = {
    "Sorbaria": "珍珠梅属",
    "Wisteria": "紫藤属",
    "Salvia": "鼠尾草属",
    "Rosales": "蔷薇目",
    "Fabales": "豆目",
    "Lamiales": "唇形目",
    "Pinales": "松柏目",
}


def get_or_create(conn, table, chinese_name=None, **kwargs):
    """Get or create a row, optionally setting chinese_name."""
    where = " AND ".join(f"{k}=?" for k in kwargs)
    vals = tuple(kwargs.values())
    row = conn.execute(f"SELECT id, chinese_name FROM {table} WHERE {where}", vals).fetchone()
    if row:
        # Fill in missing chinese_name
        if chinese_name and not row[1]:
            conn.execute(f"UPDATE {table} SET chinese_name=? WHERE id=?", (chinese_name, row[0]))
            conn.commit()
        return row[0]
    # Create
    cols = ["name"] + (["chinese_name"] if chinese_name else [])
    vals = [kwargs.get("name") or list(kwargs.values())[0]] + ([chinese_name] if chinese_name else [])
    extra_cols = [k for k in kwargs if k != "name"]
    for k in extra_cols:
        cols.append(k)
        vals.append(kwargs[k])
    placeholders = ", ".join("?" for _ in cols)
    conn.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", vals)
    conn.commit()
    return conn.execute(f"SELECT id FROM {table} WHERE {where}", vals[:len(kwargs)]).fetchone()[0]


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=OFF")

    # 获取 (unplaced) 下所有物种
    rows = conn.execute("""
        SELECT s.id, s.scientific_name, s.chinese_name,
               g.id as gid, g.name as gname
        FROM species s
        JOIN genera g ON s.genus_id = g.id
        JOIN families f ON g.family_id = f.id
        JOIN orders o ON f.order_id = o.id
        WHERE o.name='(unplaced)'
    """).fetchall()

    print(f"📋 找到 {len(rows)} 个物种在 (unplaced) 下\n")

    for sid, sci_name, ch_name, gid, gname in rows:
        sci_clean = sci_name.split(" (")[0].split(" f.")[0].strip()
        # Strip author names at end (e.g. "Rosa xanthina Lindl." → "Rosa xanthina")
        import re
        m = re.match(r"^([A-Z][a-z]+ [a-z-]+)", sci_clean)
        if m:
            sci_clean = m.group(1)
        print(f"📍 {ch_name or sci_clean}")

        mapping = CORRECT_TAXONOMY.get(sci_clean)
        if not mapping:
            print(f"   ⚠️ 未找到映射，跳过")
            continue

        print(f"   → {mapping['class']} / {mapping['order']} / {mapping['family']} / {mapping['genus']}")

        # 找到正确的纲
        class_row = conn.execute("SELECT id FROM classes WHERE name=?", (mapping["class"],)).fetchone()
        if not class_row:
            print(f"   ❌ 纲 {mapping['class']} 不存在")
            continue
        cid = class_row[0]

        # 找到/创建正确的目
        oid = get_or_create(conn, "orders", chinese_name=CHINESE_NAMES.get(mapping["order"]),
                            name=mapping["order"], class_id=cid)

        # 找到/创建正确的科
        fam_row = conn.execute("SELECT id FROM families WHERE name=? AND order_id=?",
                               (mapping["family"], oid)).fetchone()
        if fam_row:
            fid = fam_row[0]
        else:
            conn.execute("INSERT INTO families (name, order_id) VALUES (?, ?)",
                         (mapping["family"], oid))
            conn.commit()
            fid = conn.execute("SELECT id FROM families WHERE name=? AND order_id=?",
                               (mapping["family"], oid)).fetchone()[0]

        # 找到/创建正确的属
        gen_row = conn.execute("SELECT id FROM genera WHERE name=? AND family_id=?",
                               (mapping["genus"], fid)).fetchone()
        if gen_row:
            gid_new = gen_row[0]
        else:
            gen_cn = CHINESE_NAMES.get(mapping["genus"], "")
            conn.execute("INSERT INTO genera (name, family_id, chinese_name) VALUES (?, ?, ?)",
                         (mapping["genus"], fid, gen_cn))
            conn.commit()
            gid_new = conn.execute("SELECT id FROM genera WHERE name=? AND family_id=?",
                                   (mapping["genus"], fid)).fetchone()[0]

        # 更新物种 → 正确的属
        conn.execute("UPDATE species SET genus_id=? WHERE id=?", (gid_new, sid))
        conn.commit()
        print(f"   ✅ 迁移完成 → {mapping['order']}/{mapping['family']}/{mapping['genus']}")

        # 补充中文名到新创建的属（如果已有属但没有中文名）
        if gname != mapping["genus"] and gen_cn:
            conn.execute("UPDATE genera SET chinese_name=? WHERE id=? AND (chinese_name IS NULL OR chinese_name='')",
                         (gen_cn, gid_new))
            conn.commit()

    # 2. 清理空节点
    print("\n🧹 清理空的分类节点...")
    for table, parent_fk, parent_table in [
        ("families", "order_id", "orders"),
        ("orders", "class_id", "classes"),
    ]:
        conn.execute(f"""
            DELETE FROM {table} WHERE id IN (
                SELECT t.id FROM {table} t
                LEFT JOIN {parent_table} p ON p.id = t.{parent_fk}
                WHERE p.id IS NULL
            )
        """)
        conn.execute(f"""
            DELETE FROM {table} WHERE id IN (
                SELECT t.id FROM {table} t
                LEFT JOIN genera g ON g.family_id = t.id
                WHERE g.id IS NULL AND '{table}' = 'families'
            )
        """)
        conn.commit()

    # Actually for families the cleanup is:
    conn.execute("""
        DELETE FROM families WHERE id NOT IN (
            SELECT DISTINCT family_id FROM genera
        )
    """)
    conn.execute("""
        DELETE FROM orders WHERE id NOT IN (
            SELECT DISTINCT order_id FROM families
        )
    """)
    conn.commit()

    # 3. 验证
    print("\n📊 验证:")
    unplaced = conn.execute("SELECT COUNT(*) FROM orders WHERE name='(unplaced)'").fetchone()[0]
    print(f"  (unplaced) 目: {unplaced}")

    species_names = [
        "Sorbaria sorbifolia", "Rosa xanthina",
        "Wisteria floribunda", "Salvia pratensis", "Pinus bungeana",
    ]
    for sci in species_names:
        sci_prefix = sci.split(" (")[0]
        row = conn.execute("""
            SELECT s.chinese_name, o.name, f.name, g.name
            FROM species s
            JOIN genera g ON s.genus_id = g.id
            JOIN families f ON g.family_id = f.id
            JOIN orders o ON f.order_id = o.id
            WHERE s.scientific_name LIKE ?
        """, (sci_prefix + "%",)).fetchone()
        if row:
            marker = "✅" if row[1] != "(unplaced)" else "❌"
            print(f"  {marker} {row[0] or sci_prefix}: {row[1]} → {row[2]} → {row[3]}")

    print("\n🌳 所有目:")
    rows = conn.execute("""
        SELECT o.name, c.name, o.chinese_name
        FROM orders o JOIN classes c ON c.id=o.class_id
        ORDER BY o.name
    """).fetchall()
    for oname, cname, cn in rows:
        print(f"  {oname:25s} ({cname:15s}) = {cn or '-'}")

    conn.close()
    print("\n🎉 修复完成！")


if __name__ == "__main__":
    main()
