"""
Flora Collector — 分类数据迁移脚本

1. 给 kingdoms/phyla/classes/orders/families/genera 表加 chinese_name 列
2. 填充现有所有分类节点的中文名
3. 修复 (unplaced) 目下的 5 个物种到正确分类位置
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "data/flora.db"

# ════════════════════════════════════════════════════════════════
# 中文名映射表
# ════════════════════════════════════════════════════════════════

CHINESE_NAMES = {
    # 界
    "Plantae": "植物界",

    # 门
    "Tracheophyta": "维管植物门",
    "Pinophyta": "松柏门",
    "Cycadophyta": "苏铁门",
    "Ginkgophyta": "银杏门",
    "Gnetophyta": "买麻藤门",
    "Pteridophyta": "蕨类植物门",
    "Bryophyta": "苔藓植物门",
    "Magnoliophyta": "被子植物门",
    "Angiospermae": "被子植物",
    "Spermatophyta": "种子植物门",

    # 纲
    "Magnoliopsida": "木兰纲",
    "Liliopsida": "百合纲",
    "Pinopsida": "松纲",
    "Ginkgoopsida": "银杏纲",
    "Cycadopsida": "苏铁纲",
    "Gnetopsida": "买麻藤纲",
    "Polypodiopsida": "木贼纲",
    "Bryopsida": "藓纲",
    "Equisetopsida": "木贼纲",
    "Monocotyledoneae": "单子叶植物纲",
    "Dicotyledoneae": "双子叶植物纲",

    # 目 — Poales
    "Poales": "禾本目",
    "Asparagales": "天门冬目",
    "Liliales": "百合目",
    "Saxifragales": "虎耳草目",
    "Rosales": "蔷薇目",
    "Fabales": "豆目",
    "Asterales": "菊目",
    "Lamiales": "唇形目",
    "Ericales": "杜鹃花目",
    "Malpighiales": "金虎尾目",
    "Sapindales": "无患子目",
    "Malvales": "锦葵目",
    "Laurales": "樟目",
    "Brassicales": "十字花目",
    "Solanales": "茄目",
    "Caryophyllales": "石竹目",
    "Cucurbitales": "葫芦目",
    "Proteales": "山龙眼目",
    "Pinales": "松柏目",
    "Ginkgoales": "银杏目",
    "Fagales": "壳斗目",
    "Myrtales": "桃金娘目",
    "Gentianales": "龙胆目",
    "Ranunculales": "毛茛目",
    "Zingiberales": "姜目",
    "Arecales": "棕榈目",
    "Brassicales": "十字花目",
    "Celastrales": "卫矛目",
    "Cornales": "山茱萸目",
    "Crossosomatales": "十齿花目",
    "Dipsacales": "川续断目",
    "Geraniales": "牻牛儿苗目",
    "Oxalidales": "酢浆草目",
    "Santalales": "檀香目",

    # 科
    "Poaceae": "禾本科",
    "Orchidaceae": "兰科",
    "Amaryllidaceae": "石蒜科",
    "Asphodelaceae": "阿福花科",
    "Liliaceae": "百合科",
    "Paeoniaceae": "芍药科",
    "Rosaceae": "蔷薇科",
    "Moraceae": "桑科",
    "Asteraceae": "菊科",
    "Nelumbonaceae": "莲科",
    "Oleaceae": "木樨科",
    "Lamiaceae": "唇形科",
    "Plantaginaceae": "车前科",
    "Theaceae": "山茶科",
    "Ericaceae": "杜鹃花科",
    "Salicaceae": "杨柳科",
    "Violaceae": "堇菜科",
    "Sapindaceae": "无患子科",
    "Malvaceae": "锦葵科",
    "Lauraceae": "樟科",
    "Fabaceae": "豆科",
    "Brassicaceae": "十字花科",
    "Solanaceae": "茄科",
    "Convolvulaceae": "旋花科",
    "Cactaceae": "仙人掌科",
    "Cucurbitaceae": "葫芦科",
    "Ginkgoaceae": "银杏科",
    "Pinaceae": "松科",
    "Bambusoideae": "竹亚科",

    # 属
    "Bambusoideae": "竹亚科",
    "Phyllostachys": "刚竹属",
    "Oryza": "稻属",
    "Triticum": "小麦属",
    "Setaria": "狗尾草属",
    "Cymbidium": "兰属",
    "Narcissus": "水仙属",
    "Aloe": "芦荟属",
    "Lilium": "百合属",
    "Paeonia": "芍药属",
    "Prunus": "李属",
    "Rosa": "蔷薇属",
    "Malus": "苹果属",
    "Ficus": "榕属",
    "Chrysanthemum": "菊属",
    "Helianthus": "向日葵属",
    "Artemisia": "蒿属",
    "Taraxacum": "蒲公英属",
    "Nelumbo": "莲属",
    "Osmanthus": "木樨属",
    "Jasminum": "素馨属",
    "Lavandula": "薰衣草属",
    "Mentha": "薄荷属",
    "Plantago": "车前属",
    "Camellia": "山茶属",
    "Rhododendron": "杜鹃花属",
    "Salix": "柳属",
    "Populus": "杨属",
    "Viola": "堇菜属",
    "Acer": "槭属",
    "Firmiana": "梧桐属",
    "Gossypium": "棉属",
    "Camphora": "樟属",
    "Styphnolobium": "槐属",
    "Mimosa": "含羞草属",
    "Brassica": "芸薹属",
    "Capsella": "荠属",
    "Lycium": "枸杞属",
    "Solanum": "茄属",
    "Ipomoea": "番薯属",
    "Opuntia": "仙人掌属",
    "Cylindropuntia": "圆柱掌属",
    "Cucumis": "黄瓜属",
    "Citrullus": "西瓜属",
    "Ginkgo": "银杏属",
    "Pinus": "松属",
    "Sorbaria": "珍珠梅属",
    "Wisteria": "紫藤属",
    "Salvia": "鼠尾草属",
}


def add_chinese_name_columns(conn):
    """给各表添加 chinese_name 列（SQLite ALTER TABLE）"""
    tables = {
        "kingdoms": "界",
        "phyla": "门",
        "classes": "纲",
        "orders": "目",
        "families": "科",
        "genera": "属",
    }
    for table, label in tables.items():
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN chinese_name TEXT DEFAULT ''")
            print(f"  ✅ {table} 添加 chinese_name 列")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  ℹ️  {table} 已有 chinese_name 列")
            else:
                print(f"  ⚠️  {table}: {e}")


def seed_chinese_names(conn):
    """填充所有分类节点的中文名"""
    for table in ["kingdoms", "phyla", "classes", "orders", "families", "genera"]:
        rows = conn.execute(f"SELECT id, name FROM {table}").fetchall()
        updated = 0
        for rid, name in rows:
            cn = CHINESE_NAMES.get(name, "")
            if cn:
                conn.execute(
                    f"UPDATE {table} SET chinese_name=? WHERE id=?",
                    (cn, rid)
                )
                updated += 1
        conn.commit()
        total = len(rows)
        print(f"  {table}: {updated}/{total} 条已填入中文名")


def fix_unplaced_species(conn):
    """修复 (unplaced) 目下的物种到正确分类位置"""
    print("\n🔄 修复 (unplaced) 目标签物种...")

    # 获取所有 (unplaced) 订单
    unplaced_orders = conn.execute(
        "SELECT id, class_id FROM orders WHERE name='(unplaced)'"
    ).fetchall()

    if not unplaced_orders:
        print("  没有 (unplaced) 目，跳过")
        return

    for oid, class_id in unplaced_orders:
        # 找 (unplaced) 下的所有科属种
        rows = conn.execute("""
            SELECT f.id as fid, f.name as fname,
                   g.id as gid, g.name as gname,
                   s.id as sid, s.scientific_name, s.chinese_name
            FROM families f
            JOIN genera g ON g.family_id = f.id
            JOIN species s ON s.genus_id = g.id
            WHERE f.order_id = ?
        """, (oid,)).fetchall()

        for fid, fname, gid, gname, sid, sci_name, ch_name in rows:
            print(f"\n  📍 {ch_name or sci_name} ({sci_name})")

            # 用 iNaturalist 查正确的分类信息
            sci_clean = sci_name.split(" (")[0].strip()
            import urllib.request, urllib.parse, json, time
            params = urllib.parse.urlencode({
                "q": sci_clean, "rank": "species",
                "per_page": 1, "order": "desc", "order_by": "observations_count",
            })
            url = f"https://api.inaturalist.org/v1/taxa?{params}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FloraCollector/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                time.sleep(0.3)
            except Exception as e:
                print(f"    ❌ iNat 查询失败: {e}")
                continue

            results = data.get("results", [])
            if not results:
                print(f"    ⚠️ iNat 未找到")
                continue

            taxon = results[0]
            ancestors = {a["rank"]: a["name"] for a in taxon.get("ancestors", [])}
            correct_order = ancestors.get("order", "")
            correct_family = ancestors.get("family", "")
            correct_genus = ancestors.get("genus", "")
            correct_class = ancestors.get("class", "")

            print(f"    正确的目: {correct_order}, 科: {correct_family}, 属: {correct_genus}")

            if not correct_order:
                print(f"    ⚠️ 未找到正确目")
                continue

            # 找正确的 class
            class_rows = conn.execute(
                "SELECT id FROM classes WHERE name=?", (correct_class,)
            ).fetchall()
            if not class_rows:
                print(f"    ⚠️ 纲 {correct_class} 不存在，跳过")
                continue
            correct_class_id = class_rows[0][0]

            # 找/建正确的 order（确保在同一纲下）
            order_rows = conn.execute(
                "SELECT id FROM orders WHERE name=? AND class_id=?",
                (correct_order, correct_class_id)
            ).fetchall()
            if not order_rows:
                # 创建正确的 order
                conn.execute(
                    "INSERT INTO orders (name, class_id) VALUES (?, ?)",
                    (correct_order, correct_class_id)
                )
                conn.commit()
                correct_order_id = conn.execute(
                    "SELECT id FROM orders WHERE name=? AND class_id=?",
                    (correct_order, correct_class_id)
                ).fetchone()[0]
                print(f"    ✅ 创建目 {correct_order}")
            else:
                correct_order_id = order_rows[0][0]

            # 找/建正确的 family（在正确 order 下）
            family_rows = conn.execute(
                "SELECT id FROM families WHERE name=? AND order_id=?",
                (correct_family, correct_order_id)
            ).fetchall()
            if not family_rows:
                conn.execute(
                    "INSERT INTO families (name, order_id) VALUES (?, ?)",
                    (correct_family, correct_order_id)
                )
                conn.commit()
                correct_family_id = conn.execute(
                    "SELECT id FROM families WHERE name=? AND order_id=?",
                    (correct_family, correct_order_id)
                ).fetchone()[0]
                print(f"    ✅ 创建科 {correct_family}")
            else:
                correct_family_id = family_rows[0][0]

            # 找/建正确的 genus（在正确 family 下）
            genus_rows = conn.execute(
                "SELECT id FROM genera WHERE name=? AND family_id=?",
                (correct_genus, correct_family_id)
            ).fetchall()
            if not genus_rows:
                conn.execute(
                    "INSERT INTO genera (name, family_id) VALUES (?, ?)",
                    (correct_genus, correct_family_id)
                )
                conn.commit()
                correct_genus_id = conn.execute(
                    "SELECT id FROM genera WHERE name=? AND family_id=?",
                    (correct_genus, correct_family_id)
                ).fetchone()[0]
                print(f"    ✅ 创建属 {correct_genus}")
            else:
                correct_genus_id = genus_rows[0][0]

            # 更新 species 指向正确的 genus
            conn.execute(
                "UPDATE species SET genus_id=? WHERE id=?",
                (correct_genus_id, sid)
            )
            conn.commit()
            print(f"    ✅ 物种 {ch_name or sci_name} → {correct_order}/{correct_family}/{correct_genus}")

    # 清理空节点（删除不再有子节点的 (unplaced) 目）
    print("\n🧹 清理空分类节点...")
    for oid, _ in unplaced_orders:
        count = conn.execute(
            "SELECT COUNT(*) FROM families WHERE order_id=?", (oid,)
        ).fetchone()[0]
        if count == 0:
            conn.execute("DELETE FROM orders WHERE id=?", (oid,))
            conn.commit()
            print(f"  ✅ 删除空的 (unplaced) 目 id={oid}")
        else:
            remaining = conn.execute("""
                SELECT g.name, s.chinese_name
                FROM families f
                JOIN genera g ON g.family_id = f.id
                LEFT JOIN species s ON s.genus_id = g.id
                WHERE f.order_id = ?
            """, (oid,)).fetchall()
            if remaining:
                print(f"  ⚠️  (unplaced) 目 id={oid} 仍有 {len(remaining)} 条残留:")
                for gn, cn in remaining:
                    print(f"      - {gn}: {cn or '?'}")

    print("\n✅ unplaced 修复完成！")


def verify(conn):
    """验证修复结果"""
    unplaced = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE name='(unplaced)'"
    ).fetchone()[0]
    print(f"\n📊 验证结果:")
    print(f"  (unplaced) 目数量: {unplaced}")
    total_species = conn.execute("SELECT COUNT(*) FROM species").fetchone()[0]
    print(f"  总物种数: {total_species}")

    # 检查中文名覆盖率
    for table, label in [("kingdoms", "界"), ("phyla", "门"), ("classes", "纲"),
                         ("orders", "目"), ("families", "科"), ("genera", "属")]:
        total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        has_cn = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE chinese_name IS NOT NULL AND chinese_name != ''"
        ).fetchone()[0]
        print(f"   {label} ({table}): {has_cn}/{total} 有中文名")

    # 验证 all 目
    print("\n  所有目:")
    rows = conn.execute(
        "SELECT o.name, c.name, o.chinese_name FROM orders o JOIN classes c ON c.id=o.class_id ORDER BY o.name"
    ).fetchall()
    for oname, cname, cn in rows:
        marker = " ✅" if cn else ""
        print(f"    - {oname} ({cname}) = {cn or '无'}{marker}")


def main():
    print("=" * 60)
    print("🌿 Flora Collector — 分类数据迁移")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print("\n1️⃣  添加 chinese_name 列...")
    add_chinese_name_columns(conn)

    print("\n2️⃣  填充中文名...")
    seed_chinese_names(conn)

    print("\n3️⃣  修复 (unplaced) 目...")
    fix_unplaced_species(conn)

    print("\n4️⃣  验证...")
    verify(conn)

    conn.close()
    print("\n🎉 迁移完成！")


if __name__ == "__main__":
    main()
