"""
Flora Collector — 补全分类骨架（界门纲目科属标准化节点）
让分类树显示完整的层次结构，即使没有物种数据也显示为 0/0
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "data/flora.db"

# 完整分类骨架
# 格式: {纲: {科: {目: [属列表]}}} 或更直接的 {纲: {目: {科: [属]}}}
# 为了简洁用扁平结构

SKELETON = {
    # ── 松纲 Pinopsida ──
    "Pinopsida": {
        "Pinales": {          # 松柏目 ✅ 已存在
            "Pinaceae": ["Pinus"],  # 松科 ✅
        },
        "Cupressales": {      # 柏木目
            "Cupressaceae": ["Juniperus", "Cupressus", "Platycladus", "Taxodium", "Metasequoia"],
            "Taxaceae": ["Taxus", "Cephalotaxus"],
        },
        "Araucariales": {     # 南洋杉目
            "Araucariaceae": ["Araucaria", "Agathis"],
            "Podocarpaceae": ["Podocarpus"],
        },
    },

    # ── 银杏纲 Ginkgoopsida ──
    "Ginkgoopsida": {
        "Ginkgoales": {       # 银杏目 ✅
            "Ginkgoaceae": ["Ginkgo"],  # ✅
        },
    },

    # ── 百合纲 Liliopsida (单子叶植物) ──
    "Liliopsida": {
        "Poales": {           # 禾本目 ✅
            "Poaceae": ["Bambusoideae", "Phyllostachys", "Oryza", "Triticum", "Setaria"],
        },
        "Asparagales": {      # 天门冬目 ✅
            "Orchidaceae": ["Cymbidium"],
            "Amaryllidaceae": ["Narcissus"],
            "Asphodelaceae": ["Aloe"],
            "Iridaceae": ["Iris"],
            "Liliaceae": [],
        },
        "Liliales": {         # 百合目 ✅
            "Liliaceae": ["Lilium"],
        },
        "Arecales": {         # 棕榈目（新）
            "Arecaceae": ["Trachycarpus"],
        },
        "Zingiberales": {     # 姜目（新）
            "Zingiberaceae": [],
            "Musaceae": [],
        },
        "Alismatales": {      # 泽泻目（新）
            "Araceae": [],
        },
    },

    # ── 木兰纲 Magnoliopsida (双子叶植物) ──
    "Magnoliopsida": {
        "Saxifragales": {     # 虎耳草目 ✅
            "Paeoniaceae": ["Paeonia"],
        },
        "Rosales": {          # 蔷薇目 ✅
            "Rosaceae": ["Prunus", "Rosa", "Malus", "Sorbaria"],
            "Moraceae": ["Ficus"],
            "Urticaceae": [],
            "Rhamnaceae": [],
        },
        "Fabales": {          # 豆目 ✅
            "Fabaceae": ["Styphnolobium", "Mimosa", "Wisteria"],
        },
        "Asterales": {        # 菊目 ✅
            "Asteraceae": ["Chrysanthemum", "Helianthus", "Artemisia", "Taraxacum"],
        },
        "Lamiales": {         # 唇形目 ✅
            "Oleaceae": ["Osmanthus", "Jasminum"],
            "Lamiaceae": ["Lavandula", "Mentha", "Salvia"],
            "Plantaginaceae": ["Plantago"],
            "Bignoniaceae": [],
            "Pedaliaceae": [],
        },
        "Ericales": {         # 杜鹃花目 ✅
            "Theaceae": ["Camellia"],
            "Ericaceae": ["Rhododendron"],
            "Primulaceae": [],
        },
        "Malpighiales": {     # 金虎尾目 ✅
            "Salicaceae": ["Salix", "Populus"],
            "Violaceae": ["Viola"],
        },
        "Sapindales": {       # 无患子目 ✅
            "Sapindaceae": ["Acer"],
            "Rutaceae": ["Citrus"],
            "Anacardiaceae": [],
        },
        "Malvales": {         # 锦葵目 ✅
            "Malvaceae": ["Firmiana", "Gossypium"],
        },
        "Laurales": {         # 樟目 ✅
            "Lauraceae": ["Camphora"],
        },
        "Brassicales": {      # 十字花目 ✅
            "Brassicaceae": ["Brassica", "Capsella"],
        },
        "Solanales": {        # 茄目 ✅
            "Solanaceae": ["Lycium", "Solanum"],
            "Convolvulaceae": ["Ipomoea"],
        },
        "Caryophyllales": {   # 石竹目 ✅
            "Cactaceae": ["Opuntia", "Cylindropuntia"],
            "Amaranthaceae": [],
            "Caryophyllaceae": [],
        },
        "Cucurbitales": {     # 葫芦目 ✅
            "Cucurbitaceae": ["Cucumis", "Citrullus"],
        },
        "Proteales": {        # 山龙眼目 ✅
            "Nelumbonaceae": ["Nelumbo"],
            "Platanaceae": [],
        },
        "Fagales": {          # 壳斗目（新）
            "Fagaceae": ["Quercus"],
            "Betulaceae": [],
        },
        "Myrtales": {         # 桃金娘目（新）
            "Myrtaceae": ["Eucalyptus"],
            "Lythraceae": ["Lagerstroemia"],
        },
        "Ranunculales": {     # 毛茛目（新）
            "Ranunculaceae": [],
            "Berberidaceae": [],
        },
        "Gentianales": {      # 龙胆目（新）
            "Rubiaceae": [],
            "Gentianaceae": [],
            "Apocynaceae": [],
        },
        "Dipsacales": {       # 川续断目（新）
            "Caprifoliaceae": [],
            "Adoxaceae": [],
        },
    },
}

CHINESE_NAMES = {
    # 纲
    "Pinopsida": "松纲",
    "Ginkgoopsida": "银杏纲",
    "Liliopsida": "百合纲",
    "Magnoliopsida": "木兰纲",

    # 松柏目
    "Cupressales": "柏木目",
    "Cupressaceae": "柏科",
    "Taxaceae": "红豆杉科",
    "Juniperus": "刺柏属",
    "Cupressus": "柏木属",
    "Platycladus": "侧柏属",
    "Taxodium": "落羽杉属",
    "Metasequoia": "水杉属",
    "Taxus": "红豆杉属",
    "Cephalotaxus": "三尖杉属",

    # 南洋杉目
    "Araucariales": "南洋杉目",
    "Araucariaceae": "南洋杉科",
    "Podocarpaceae": "罗汉松科",
    "Araucaria": "南洋杉属",
    "Agathis": "贝壳杉属",
    "Podocarpus": "罗汉松属",

    # 新目
    "Arecales": "棕榈目",
    "Arecaceae": "棕榈科",
    "Trachycarpus": "棕榈属",
    "Zingiberales": "姜目",
    "Zingiberaceae": "姜科",
    "Musaceae": "芭蕉科",
    "Alismatales": "泽泻目",
    "Araceae": "天南星科",

    # 蔷薇目补充
    "Urticaceae": "荨麻科",
    "Rhamnaceae": "鼠李科",

    # 唇形目补充
    "Bignoniaceae": "紫葳科",
    "Pedaliaceae": "胡麻科",

    # 金虎尾补充
    "Primulaceae": "报春花科",

    # 无患子目补充
    "Rutaceae": "芸香科",
    "Anacardiaceae": "漆树科",
    "Citrus": "柑橘属",

    # 石竹目补充
    "Amaranthaceae": "苋科",
    "Caryophyllaceae": "石竹科",

    # 蛋白石目补充
    "Platanaceae": "悬铃木科",

    # 新目
    "Fagales": "壳斗目",
    "Fagaceae": "壳斗科",
    "Betulaceae": "桦木科",
    "Quercus": "栎属",

    "Myrtales": "桃金娘目",
    "Myrtaceae": "桃金娘科",
    "Lythraceae": "千屈菜科",
    "Eucalyptus": "桉属",
    "Lagerstroemia": "紫薇属",

    "Ranunculales": "毛茛目",
    "Ranunculaceae": "毛茛科",
    "Berberidaceae": "小檗科",

    "Gentianales": "龙胆目",
    "Rubiaceae": "茜草科",
    "Gentianaceae": "龙胆科",
    "Apocynaceae": "夹竹桃科",

    "Dipsacales": "川续断目",
    "Caprifoliaceae": "忍冬科",
    "Adoxaceae": "五福花科",

    # Liliopsida 补充
    "Iridaceae": "鸢尾科",
    "Iris": "鸢尾属",
}


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=OFF")

    # 获取已有数据
    existing = {
        "classes": set(r[0] for r in conn.execute("SELECT name FROM classes").fetchall()),
        "orders": set(r[0] for r in conn.execute("SELECT name FROM orders").fetchall()),
        "families": set(r[0] for r in conn.execute("SELECT name FROM families").fetchall()),
        "genera": set(r[0] for r in conn.execute("SELECT name FROM genera").fetchall()),
    }

    created = {"orders": 0, "families": 0, "genera": 0}

    for class_name, orders in SKELETON.items():
        # 找纲
        class_row = conn.execute("SELECT id, chinese_name FROM classes WHERE name=?", (class_name,)).fetchone()
        if not class_row:
            # 如果纲不存在，需要创建
            kingdom_row = conn.execute("SELECT id FROM kingdoms WHERE name='Plantae'").fetchone()
            if not kingdom_row:
                conn.execute("INSERT INTO kingdoms (name, chinese_name) VALUES ('Plantae', '植物界')")
                conn.commit()
                kingdom_id = conn.execute("SELECT id FROM kingdoms WHERE name='Plantae'").fetchone()[0]
            else:
                kingdom_id = kingdom_row[0]
            phylum_row = conn.execute("SELECT id FROM phyla WHERE name='Tracheophyta'").fetchone()
            if not phylum_row:
                conn.execute("INSERT INTO phyla (name, kingdom_id, chinese_name) VALUES ('Tracheophyta', ?, '维管植物门')", (kingdom_id,))
                conn.commit()
                phylum_id = conn.execute("SELECT id FROM phyla WHERE name='Tracheophyta'").fetchone()[0]
            else:
                phylum_id = phylum_row[0]
            cn = CHINESE_NAMES.get(class_name, "")
            conn.execute("INSERT INTO classes (name, phylum_id, chinese_name) VALUES (?, ?, ?)",
                         (class_name, phylum_id, cn))
            conn.commit()
            class_id = conn.execute("SELECT id FROM classes WHERE name=?", (class_name,)).fetchone()[0]
            print(f"  ✅ 创建纲 {class_name} ({cn})")
        else:
            class_id = class_row[0]
            # 补中文名
            cn = CHINESE_NAMES.get(class_name, "")
            if cn and (not class_row[1]):
                conn.execute("UPDATE classes SET chinese_name=? WHERE id=?", (cn, class_id))
                conn.commit()

        for order_name, families in orders.items():
            # 找目
            order_row = conn.execute("SELECT id, chinese_name FROM orders WHERE name=? AND class_id=?",
                                     (order_name, class_id)).fetchone()
            if order_row:
                order_id = order_row[0]
                # 补中文名
                cn = CHINESE_NAMES.get(order_name, "")
                if cn and (not order_row[1]):
                    conn.execute("UPDATE orders SET chinese_name=? WHERE id=?", (cn, order_id))
                    conn.commit()
            else:
                cn = CHINESE_NAMES.get(order_name, "")
                conn.execute("INSERT INTO orders (name, class_id, chinese_name) VALUES (?, ?, ?)",
                             (order_name, class_id, cn))
                conn.commit()
                order_id = conn.execute("SELECT id FROM orders WHERE name=? AND class_id=?",
                                       (order_name, class_id)).fetchone()[0]
                created["orders"] += 1
                print(f"    ✅ 创建目 {order_name} ({cn})")

            for family_name, genus_list in families.items():
                # 找科
                fam_row = conn.execute("SELECT id, chinese_name FROM families WHERE name=? AND order_id=?",
                                       (family_name, order_id)).fetchone()
                if fam_row:
                    family_id = fam_row[0]
                    cn = CHINESE_NAMES.get(family_name, "")
                    if cn and (not fam_row[1]):
                        conn.execute("UPDATE families SET chinese_name=? WHERE id=?", (cn, family_id))
                        conn.commit()
                else:
                    cn = CHINESE_NAMES.get(family_name, "")
                    conn.execute("INSERT INTO families (name, order_id, chinese_name) VALUES (?, ?, ?)",
                                 (family_name, order_id, cn))
                    conn.commit()
                    family_id = conn.execute("SELECT id FROM families WHERE name=? AND order_id=?",
                                           (family_name, order_id)).fetchone()[0]
                    created["families"] += 1

                for genus_name in genus_list:
                    # 找属
                    gen_row = conn.execute("SELECT id, chinese_name FROM genera WHERE name=? AND family_id=?",
                                          (genus_name, family_id)).fetchone()
                    if gen_row:
                        cn = CHINESE_NAMES.get(genus_name, "")
                        if cn and (not gen_row[1]):
                            conn.execute("UPDATE genera SET chinese_name=? WHERE id=?", (cn, gen_row[0]))
                            conn.commit()
                    else:
                        cn = CHINESE_NAMES.get(genus_name, "")
                        conn.execute("INSERT INTO genera (name, family_id, chinese_name) VALUES (?, ?, ?)",
                                     (genus_name, family_id, cn))
                        conn.commit()
                        created["genera"] += 1

    # 验证结果
    print(f"\n📊 新增节点:")
    print(f"  目: {created['orders']}")
    print(f"  科: {created['families']}")
    print(f"  属: {created['genera']}")

    print(f"\n📊 现有节点:")
    for table in ["kingdoms", "phyla", "classes", "orders", "families", "genera"]:
        total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        cn_count = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE chinese_name IS NOT NULL AND chinese_name != ''"
        ).fetchone()[0]
        print(f"  {table}: {total}（{cn_count} 有中文名）")

    # 显示每个纲的目
    print(f"\n🌳 分类结构:")
    for class_name in ["Liliopsida", "Magnoliopsida", "Pinopsida", "Ginkgoopsida"]:
        rows = conn.execute("""
            SELECT o.name, o.chinese_name, 
                   (SELECT COUNT(*) FROM families f WHERE f.order_id=o.id) as fams,
                   (SELECT COUNT(*) FROM genera g JOIN families f ON g.family_id=f.id WHERE f.order_id=o.id) as gens
            FROM orders o
            JOIN classes c ON c.id=o.class_id
            WHERE c.name=?
            ORDER BY o.name
        """, (class_name,)).fetchall()
        cn = CHINESE_NAMES.get(class_name, "")
        print(f"\n  {cn or class_name}:")
        for oname, ocn, fams, gens in rows:
            print(f"    {ocn or oname}（{fams} 科, {gens} 属）")

    conn.close()
    print("\n🎉 分类骨架补全完成！")


if __name__ == "__main__":
    main()
