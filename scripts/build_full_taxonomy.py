"""
Flora Collector — 完整植物分类骨架迁移 v2
迁移现有纲到正确门 + 新增所有缺失的纲和目
"""
import sqlite3

DB_PATH = "data/flora.db"

# ======================== 完整植物分类骨架 ========================
# 格式: (门, 门_中文, [(纲, 纲_中文, [(目, 目_中文), ...]), ...])

PLANT_KINGDOM = (
    "Plantae", "植物界", [
    # ─── 非维管植物 ──────────────────────────────────
    ("Bryophyta", "苔藓植物门", [
        ("Bryopsida", "藓纲", [
            ("Bryales", "真藓目"),
            ("Dicranales", "曲尾藓目"),
            ("Hypnales", "灰藓目"),
            ("Polytrichales", "金发藓目"),
            ("Sphagnales", "泥炭藓目"),
            ("Funariales", "葫芦藓目"),
            ("Grimmiales", "紫萼藓目"),
            ("Hookeriales", "油藓目"),
            ("Pottiales", "丛藓目"),
        ]),
    ]),
    ("Marchantiophyta", "地钱门", [
        ("Marchantiopsida", "地钱纲", [
            ("Marchantiales", "地钱目"),
            ("Sphaerocarpales", "囊果苔目"),
            ("Lunulariales", "半月苔目"),
        ]),
        ("Jungermanniopsida", "叶苔纲", [
            ("Jungermanniales", "叶苔目"),
            ("Porellales", "光萼苔目"),
            ("Ptilidiales", "毛叶苔目"),
            ("Fossombroniales", "小叶苔目"),
            ("Pelliales", "溪苔目"),
        ]),
    ]),
    ("Anthocerotophyta", "角苔门", [
        ("Anthocerotopsida", "角苔纲", [
            ("Anthocerotales", "角苔目"),
            ("Notothyladales", "短角苔目"),
            ("Dendrocerotales", "树角苔目"),
        ]),
    ]),

    # ─── 石松门 ──────────────────────────────────
    ("Lycopodiophyta", "石松门", [
        ("Lycopodiopsida", "石松纲", [
            ("Lycopodiales", "石松目"),
            ("Isoetales", "水韭目"),
            ("Selaginellales", "卷柏目"),
        ]),
    ]),

    # ─── 蕨类植物门 ──────────────────────────────────
    ("Polypodiophyta", "蕨类植物门", [
        ("Equisetopsida", "木贼纲", [
            ("Equisetales", "木贼目"),
        ]),
        ("Polypodiopsida", "真蕨纲", [
            ("Ophioglossales", "瓶尔小草目"),
            ("Psilotales", "松叶蕨目"),
            ("Marattiales", "观音座莲目"),
            ("Osmundales", "紫萁目"),
            ("Hymenophyllales", "膜蕨目"),
            ("Gleicheniales", "里白目"),
            ("Schizaeales", "莎草蕨目"),
            ("Salviniales", "槐叶苹目"),
            ("Cyatheales", "桫椤目"),
            ("Polypodiales", "水龙骨目"),
        ]),
    ]),

    # ─── 苏铁门 ──────────────────────────────────
    ("Cycadophyta", "苏铁门", [
        ("Cycadopsida", "苏铁纲", [
            ("Cycadales", "苏铁目"),
        ]),
    ]),

    # ─── 银杏门 ──────────────────────────────────
    ("Ginkgophyta", "银杏门", [
        ("Ginkgoopsida", "银杏纲", [
            ("Ginkgoales", "银杏目"),
        ]),
    ]),

    # ─── 松柏门 ──────────────────────────────────
    ("Pinophyta", "松柏门", [
        ("Pinopsida", "松纲", [
            ("Pinales", "松柏目"),
            ("Araucariales", "南洋杉目"),
            ("Cupressales", "柏木目"),
        ]),
    ]),

    # ─── 买麻藤门 ──────────────────────────────────
    ("Gnetophyta", "买麻藤门", [
        ("Gnetopsida", "买麻藤纲", [
            ("Gnetales", "买麻藤目"),
            ("Ephedrales", "麻黄目"),
            ("Welwitschiales", "百岁兰目"),
        ]),
    ]),

    # ─── 被子植物门 (APG IV) ────────────────────
    ("Magnoliophyta", "被子植物门", [
        ("Magnoliopsida", "木兰纲", [
            # 基部被子植物
            ("Amborellales", "无油樟目"),
            ("Nymphaeales", "睡莲目"),
            ("Austrobaileyales", "木兰藤目"),
            ("Chloranthales", "金粟兰目"),
            ("Ceratophyllales", "金鱼藻目"),
            # 木兰类
            ("Canellales", "白桂皮目"),
            ("Piperales", "胡椒目"),
            ("Magnoliales", "木兰目"),
            ("Laurales", "樟目"),
            # 真双子叶
            ("Ranunculales", "毛茛目"),
            ("Proteales", "山龙眼目"),
            ("Trochodendrales", "昆栏树目"),
            ("Buxales", "黄杨目"),
            ("Gunnerales", "大叶草目"),
            ("Dilleniales", "五桠果目"),
            ("Saxifragales", "虎耳草目"),
            ("Vitales", "葡萄目"),
            ("Berberidopsidales", "红珊藤目"),
            ("Santalales", "檀香目"),
            ("Caryophyllales", "石竹目"),
            # 蔷薇类
            ("Zygophyllales", "蒺藜目"),
            ("Celastrales", "卫矛目"),
            ("Oxalidales", "酢浆草目"),
            ("Malpighiales", "金虎尾目"),
            ("Fabales", "豆目"),
            ("Rosales", "蔷薇目"),
            ("Cucurbitales", "葫芦目"),
            ("Fagales", "壳斗目"),
            ("Geraniales", "牻牛儿苗目"),
            ("Myrtales", "桃金娘目"),
            ("Crossosomatales", "十齿花目"),
            ("Picramniales", "苦木目"),
            ("Sapindales", "无患子目"),
            ("Huerteales", "十萼花目"),
            ("Malvales", "锦葵目"),
            ("Brassicales", "十字花目"),
            # 菊类
            ("Cornales", "山茱萸目"),
            ("Ericales", "杜鹃花目"),
            # 唇形类
            ("Boraginales", "紫草目"),
            ("Garryales", "丝缨花目"),
            ("Gentianales", "龙胆目"),
            ("Lamiales", "唇形目"),
            ("Solanales", "茄目"),
            ("Icacinales", "茶茱萸目"),
            ("Metteniusales", "水螅花目"),
            ("Vahliales", "瓦利花目"),
            # 桔梗类
            ("Apiales", "伞形目"),
            ("Aquifoliales", "冬青目"),
            ("Asterales", "菊目"),
            ("Bruniales", "布伦花目"),
            ("Dipsacales", "川续断目"),
            ("Escalloniales", "鼠刺目"),
            ("Paracryphiales", "寄生花目"),
        ]),
        ("Liliopsida", "百合纲", [
            ("Acorales", "菖蒲目"),
            ("Alismatales", "泽泻目"),
            ("Petrosaviales", "无叶莲目"),
            ("Dioscoreales", "薯蓣目"),
            ("Pandanales", "露兜树目"),
            ("Liliales", "百合目"),
            ("Asparagales", "天门冬目"),
            ("Arecales", "棕榈目"),
            ("Zingiberales", "姜目"),
            ("Commelinales", "鸭跖草目"),
            ("Poales", "禾本目"),
        ]),
    ]),
])


def migrate_classes(conn):
    """将现有纲迁移到正确的门下"""
    migrations = {
        "Ginkgoopsida": "Ginkgophyta",
        "Pinopsida": "Pinophyta",
        "Magnoliopsida": "Magnoliophyta",
        "Liliopsida": "Magnoliophyta",
    }
    print("🔄 迁移现有纲到正确门下...")
    for cls_name, target_phy in migrations.items():
        cls = conn.execute("SELECT id, name, phylum_id FROM classes WHERE name=?",
                           (cls_name,)).fetchone()
        if not cls:
            continue
        old_phy_id = cls[2]
        new_phy = conn.execute("SELECT id FROM phyla WHERE name=?", (target_phy,)).fetchone()
        if not new_phy:
            print(f"   ⚠️ 目标门 {target_phy} 尚不存在")
            continue
        new_phy_id = new_phy[0]
        if old_phy_id != new_phy_id:
            conn.execute("UPDATE classes SET phylum_id=? WHERE id=?", (new_phy_id, cls[0]))
            conn.commit()
            old_phy_name = conn.execute("SELECT name FROM phyla WHERE id=?", (old_phy_id,)).fetchone()[0]
            print(f"   ✅ {cls_name}: {old_phy_name} → {target_phy}")
        else:
            print(f"   ℹ️ {cls_name} 已在正确门下")


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys=OFF")

    print("🌿 构建完整植物分类骨架...\n")

    kn = conn.execute("SELECT id FROM kingdoms WHERE name='Plantae'").fetchone()
    kingdom_id = kn[0]

    # ─── 1. 创建所有新门 ────────────────────────
    new_phyla = {}
    print("1️⃣  创建新门...")
    for phy_name, phy_cn, _ in PLANT_KINGDOM[2]:
        row = conn.execute("SELECT id FROM phyla WHERE name=? AND kingdom_id=?",
                           (phy_name, kingdom_id)).fetchone()
        if row:
            new_phyla[phy_name] = row[0]
            if phy_cn:
                conn.execute("UPDATE phyla SET chinese_name=? WHERE id=?", (phy_cn, row[0]))
                conn.commit()
            print(f"   📁 {phy_name} ({phy_cn}) — 已存在")
        else:
            conn.execute("INSERT INTO phyla (name, kingdom_id, chinese_name) VALUES (?,?,?)",
                         (phy_name, kingdom_id, phy_cn))
            conn.commit()
            pid = conn.execute("SELECT id FROM phyla WHERE name=? AND kingdom_id=?",
                               (phy_name, kingdom_id)).fetchone()[0]
            new_phyla[phy_name] = pid
            print(f"   📁 {phy_name} ({phy_cn}) — 新增")

    # ─── 2. 迁移现有纲到正确门下 ────────────────
    print("\n2️⃣  迁移现有纲...")
    migrate_classes(conn)

    # ─── 3. 创建所有新纲和目 ────────────────────
    print("\n3️⃣  创建所有纲和目...")
    stats = {"classes_new": 0, "orders_new": 0, "orders_existing": 0}

    for phy_name, phy_cn, class_list in PLANT_KINGDOM[2]:
        phy_id = new_phyla[phy_name]

        for cls_name, cls_cn, order_list in class_list:
            # 查找纲（可能在当前门下或已迁移过来）
            cls = conn.execute("SELECT id FROM classes WHERE name=?", (cls_name,)).fetchone()
            if cls:
                cls_id = cls[0]
                # 确保 phylum_id 正确
                current_phy = conn.execute("SELECT phylum_id FROM classes WHERE id=?", (cls_id,)).fetchone()[0]
                if current_phy != phy_id:
                    conn.execute("UPDATE classes SET phylum_id=? WHERE id=?", (phy_id, cls_id))
                    conn.commit()
                if cls_cn:
                    conn.execute("UPDATE classes SET chinese_name=? WHERE id=? AND (chinese_name IS NULL OR chinese_name='')",
                                 (cls_cn, cls_id))
                    conn.commit()
            else:
                conn.execute("INSERT INTO classes (name, phylum_id, chinese_name) VALUES (?,?,?)",
                             (cls_name, phy_id, cls_cn))
                conn.commit()
                cls_id = conn.execute("SELECT id FROM classes WHERE name=? AND phylum_id=?",
                                      (cls_name, phy_id)).fetchone()[0]
                stats["classes_new"] += 1
                print(f"   📂 纲 {cls_name} ({cls_cn}) — 新增")

            # 创建目
            for ord_name, ord_cn in order_list:
                row = conn.execute("SELECT id FROM orders WHERE name=? AND class_id=?",
                                   (ord_name, cls_id)).fetchone()
                if row:
                    if ord_cn:
                        conn.execute("UPDATE orders SET chinese_name=? WHERE id=? AND (chinese_name IS NULL OR chinese_name='')",
                                     (ord_cn, row[0]))
                        conn.commit()
                    stats["orders_existing"] += 1
                else:
                    conn.execute("INSERT INTO orders (name, class_id, chinese_name) VALUES (?,?,?)",
                                 (ord_name, cls_id, ord_cn))
                    conn.commit()
                    stats["orders_new"] += 1

    conn.commit()

    # ─── 4. 清理 ──────────────────────────────────
    print("\n4️⃣  清理空分类节点...")
    # 删掉空的旧门（如果所有纲都被迁走了）
    old_phy = conn.execute("SELECT id, name FROM phyla WHERE kingdom_id=?", (kingdom_id,)).fetchall()
    for pid, pname in old_phy:
        cls_count = conn.execute("SELECT COUNT(*) FROM classes WHERE phylum_id=?", (pid,)).fetchone()[0]
        if cls_count == 0:
            conn.execute("DELETE FROM phyla WHERE id=?", (pid,))
            conn.commit()
            print(f"   🗑️ 删除空门 {pname}")

    # ─── 5. 验证 ──────────────────────────────────
    print(f"\n{'='*60}")
    print(f"统计:")
    total = {
        "kingdoms": conn.execute("SELECT COUNT(*) FROM kingdoms").fetchone()[0],
        "phyla": conn.execute("SELECT COUNT(*) FROM phyla WHERE kingdom_id=? AND name NOT LIKE '(unknown)'",
                              (kingdom_id,)).fetchone()[0],
        "classes": conn.execute("SELECT COUNT(*) FROM classes c JOIN phyla p ON p.id=c.phylum_id WHERE p.kingdom_id=?",
                                (kingdom_id,)).fetchone()[0],
        "orders": conn.execute("SELECT COUNT(*) FROM orders o JOIN classes c ON c.id=o.class_id JOIN phyla p ON p.id=c.phylum_id WHERE p.kingdom_id=?",
                               (kingdom_id,)).fetchone()[0],
        "families": conn.execute("SELECT COUNT(*) FROM families").fetchone()[0],
        "genera": conn.execute("SELECT COUNT(*) FROM genera").fetchone()[0],
        "species": conn.execute("SELECT COUNT(*) FROM species").fetchone()[0],
    }
    print(f"  新增: {stats['classes_new']} 纲, {stats['orders_new']} 目")
    print(f"  合计: {total['phyla']} 门, {total['classes']} 纲, {total['orders']} 目, {total['families']} 科, {total['genera']} 属, {total['species']} 种")

    print(f"\n🌳 分类树:")
    for phy_name, phy_cn, class_list in PLANT_KINGDOM[2]:
        phy = conn.execute("SELECT id, chinese_name FROM phyla WHERE name=?", (phy_name,)).fetchone()
        if not phy:
            continue
        phy_id, phy_display = phy[0], phy[1] or phy_name
        print(f"\n  📁 {phy_display}")

        for cls_name, cls_cn, order_list in class_list:
            cls = conn.execute("SELECT id, chinese_name FROM classes WHERE name=? AND phylum_id=?",
                               (cls_name, phy_id)).fetchone()
            if not cls:
                cls = conn.execute("SELECT id, chinese_name FROM classes WHERE name=?", (cls_name,)).fetchone()
                if not cls:
                    continue
            cd = cls[1] or cls_name
            ord_count = conn.execute("SELECT COUNT(*) FROM orders WHERE class_id=?", (cls[0],)).fetchone()[0]
            print(f"    📂 {cd} ({ord_count} 目)")
            orders = conn.execute("SELECT name, chinese_name FROM orders WHERE class_id=? ORDER BY name",
                                  (cls[0],)).fetchall()
            for o_name, o_cn in orders:
                has_data = conn.execute("""
                    SELECT COUNT(*) FROM families f
                    JOIN genera g ON g.family_id = f.id
                    JOIN species s ON s.genus_id = g.id
                    WHERE f.order_id IN (SELECT id FROM orders WHERE name=? AND class_id=?)
                """, (o_name, cls[0])).fetchone()[0]
                marker = f" ({has_data}种)" if has_data else ""
                print(f"      📄 {o_cn or o_name}{marker}")

    conn.close()
    print(f"\n🎉 骨架构建完成！刷新页面查看效果。")


if __name__ == "__main__":
    main()
