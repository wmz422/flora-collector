"""Flora Collector — 分类数据映射表
家庭→目映射 + 所有分类级别中文名
"""
# 科 → 目 映射（覆盖约 80 个常见科）
FAMILY_TO_ORDER = {
    # ─── 单子叶植物 ──────────────────
    "Poaceae": "Poales",            # 禾本科 → 禾本目
    "Orchidaceae": "Asparagales",   # 兰科 → 天门冬目
    "Amaryllidaceae": "Asparagales",# 石蒜科 → 天门冬目
    "Asphodelaceae": "Asparagales", # 阿福花科 → 天门冬目
    "Iridaceae": "Asparagales",     # 鸢尾科 → 天门冬目
    "Liliaceae": "Liliales",        # 百合科 → 百合目
    "Arecaceae": "Arecales",        # 棕榈科 → 棕榈目
    "Zingiberaceae": "Zingiberales",# 姜科 → 姜目
    "Musaceae": "Zingiberales",     # 芭蕉科 → 姜目
    "Commelinaceae": "Commelinales",# 鸭跖草科 → 鸭跖草目
    "Araceae": "Alismatales",       # 天南星科 → 泽泻目
    "Dioscoreaceae": "Dioscoreales",# 薯蓣科 → 薯蓣目
    "Pandanaceae": "Pandanales",    # 露兜树科 → 露兜树目
    "Acoraceae": "Acorales",        # 菖蒲科 → 菖蒲目
    "Smilacaceae": "Liliales",      # 菝葜科 → 百合目
    "Juncaceae": "Poales",          # 灯心草科 → 禾本目
    "Cyperaceae": "Poales",         # 莎草科 → 禾本目
    "Strelitziaceae": "Zingiberales",
    "Heliconiaceae": "Zingiberales",

    # ─── 蔷薇类 ─────────────────────
    "Rosaceae": "Rosales",          # 蔷薇科 → 蔷薇目
    "Moraceae": "Rosales",          # 桑科 → 蔷薇目
    "Urticaceae": "Rosales",        # 荨麻科 → 蔷薇目
    "Rhamnaceae": "Rosales",        # 鼠李科 → 蔷薇目
    "Ulmaceae": "Rosales",          # 榆科 → 蔷薇目
    "Cannabaceae": "Rosales",       # 大麻科 → 蔷薇目
    "Fabaceae": "Fabales",          # 豆科 → 豆目
    "Polygalaceae": "Fabales",      # 远志科 → 豆目
    "Cucurbitaceae": "Cucurbitales",# 葫芦科 → 葫芦目
    "Begoniaceae": "Cucurbitales",  # 秋海棠科 → 葫芦目
    "Fagaceae": "Fagales",          # 壳斗科 → 壳斗目
    "Betulaceae": "Fagales",        # 桦木科 → 壳斗目
    "Juglandaceae": "Fagales",      # 胡桃科 → 壳斗目
    "Myrtaceae": "Myrtales",        # 桃金娘科 → 桃金娘目
    "Lythraceae": "Myrtales",       # 千屈菜科 → 桃金娘目
    "Onagraceae": "Myrtales",       # 柳叶菜科 → 桃金娘目
    "Combretaceae": "Myrtales",     # 使君子科 → 桃金娘目
    "Melastomataceae": "Myrtales",  # 野牡丹科 → 桃金娘目

    # ─── 锦葵类 ─────────────────────
    "Malvaceae": "Malvales",        # 锦葵科 → 锦葵目
    "Dipterocarpaceae": "Malvales", # 龙脑香科 → 锦葵目
    "Thymelaeaceae": "Malvales",    # 瑞香科 → 锦葵目
    "Brassicaceae": "Brassicales",  # 十字花科 → 十字花目
    "Sapindaceae": "Sapindales",    # 无患子科 → 无患子目
    "Rutaceae": "Sapindales",       # 芸香科 → 无患子目
    "Anacardiaceae": "Sapindales",  # 漆树科 → 无患子目
    "Meliaceae": "Sapindales",      # 楝科 → 无患子目
    "Simaroubaceae": "Sapindales",  # 苦木科 → 无患子目
    "Zygophyllaceae": "Zygophyllales",
    "Celastraceae": "Celastrales",  # 卫矛科 → 卫矛目
    "Oxalidaceae": "Oxalidales",    # 酢浆草科 → 酢浆草目
    "Geraniaceae": "Geraniales",    # 牻牛儿苗科 → 牻牛儿苗目

    # ─── 金虎尾类 ──────────────────
    "Salicaceae": "Malpighiales",   # 杨柳科 → 金虎尾目
    "Violaceae": "Malpighiales",    # 堇菜科 → 金虎尾目
    "Euphorbiaceae": "Malpighiales",# 大戟科 → 金虎尾目
    "Passifloraceae": "Malpighiales",
    "Hypericaceae": "Malpighiales", # 金丝桃科 → 金虎尾目
    "Clusiaceae": "Malpighiales",   # 藤黄科 → 金虎尾目
    "Rhizophoraceae": "Malpighiales",

    # ─── 菊类 ─────────────────────
    "Asteraceae": "Asterales",      # 菊科 → 菊目
    "Campanulaceae": "Asterales",   # 桔梗科 → 菊目
    "Apiaceae": "Apiales",          # 伞形科 → 伞形目
    "Araliaceae": "Apiales",        # 五加科 → 伞形目
    "Aquifoliaceae": "Aquifoliales",# 冬青科 → 冬青目
    "Caprifoliaceae": "Dipsacales", # 忍冬科 → 川续断目
    "Adoxaceae": "Dipsacales",      # 五福花科 → 川续断目
    "Valerianaceae": "Dipsacales",  # 缬草科 → 川续断目

    # ─── 唇形类 ──────────────────
    "Lamiaceae": "Lamiales",        # 唇形科 → 唇形目
    "Oleaceae": "Lamiales",         # 木樨科 → 唇形目
    "Plantaginaceae": "Lamiales",   # 车前科 → 唇形目
    "Scrophulariaceae": "Lamiales", # 玄参科 → 唇形目
    "Bignoniaceae": "Lamiales",     # 紫葳科 → 唇形目
    "Pedaliaceae": "Lamiales",      # 胡麻科 → 唇形目
    "Acanthaceae": "Lamiales",      # 爵床科 → 唇形目
    "Verbenaceae": "Lamiales",      # 马鞭草科 → 唇形目
    "Gesneriaceae": "Lamiales",     # 苦苣苔科 → 唇形目
    "Orobanchaceae": "Lamiales",    # 列当科 → 唇形目
    "Solanaceae": "Solanales",      # 茄科 → 茄目
    "Convolvulaceae": "Solanales",  # 旋花科 → 茄目
    "Boraginaceae": "Boraginales",  # 紫草科 → 紫草目
    "Rubiaceae": "Gentianales",     # 茜草科 → 龙胆目
    "Gentianaceae": "Gentianales",  # 龙胆科 → 龙胆目
    "Apocynaceae": "Gentianales",   # 夹竹桃科 → 龙胆目
    "Loganiaceae": "Gentianales",   # 马钱科 → 龙胆目

    # ─── 杜鹃花类 ─────────────────
    "Ericaceae": "Ericales",        # 杜鹃花科 → 杜鹃花目
    "Theaceae": "Ericales",         # 山茶科 → 杜鹃花目
    "Primulaceae": "Ericales",      # 报春花科 → 杜鹃花目
    "Ebenaceae": "Ericales",        # 柿科 → 杜鹃花目
    "Symplocaceae": "Ericales",     # 山矾科 → 杜鹃花目
    "Actinidiaceae": "Ericales",    # 猕猴桃科 → 杜鹃花目
    "Sapotaceae": "Ericales",       # 山榄科 → 杜鹃花目
    "Cornales": "Cornales",

    # ─── 基部真双子叶 ──────────────
    "Saxifragaceae": "Saxifragales",# 虎耳草科 → 虎耳草目
    "Paeoniaceae": "Saxifragales",  # 芍药科 → 虎耳草目
    "Crassulaceae": "Saxifragales", # 景天科 → 虎耳草目
    "Hamamelidaceae": "Saxifragales",
    "Vitales": "Vitales",
    "Vitaceae": "Vitales",          # 葡萄科 → 葡萄目
    "Santalaceae": "Santalales",    # 檀香科 → 檀香目
    "Loranthaceae": "Santalales",   # 桑寄生科 → 檀香目
    "Dilleniaceae": "Dilleniales",  # 五桠果科 → 五桠果目
    "Ranunculaceae": "Ranunculales", # 毛茛科 → 毛茛目
    "Berberidaceae": "Ranunculales",# 小檗科 → 毛茛目
    "Papaveraceae": "Ranunculales", # 罂粟科 → 毛茛目
    "Menispermaceae": "Ranunculales",
    "Nelumbonaceae": "Proteales",   # 莲科 → 山龙眼目
    "Platanaceae": "Proteales",     # 悬铃木科 → 山龙眼目
    "Proteaceae": "Proteales",      # 山龙眼科 → 山龙眼目
    "Trochodendraceae": "Trochodendrales",
    "Buxaceae": "Buxales",          # 黄杨科 → 黄杨目
    "Gunneraceae": "Gunnerales",    # 大叶草科 → 大叶草目
    "Myrothamnaceae": "Gunnerales",

    # ─── 木兰类 ──────────────────
    "Magnoliaceae": "Magnoliales",  # 木兰科 → 木兰目
    "Lauraceae": "Laurales",        # 樟科 → 樟目
    "Piperaceae": "Piperales",      # 胡椒科 → 胡椒目
    "Aristolochiaceae": "Piperales",# 马兜铃科 → 胡椒目
    "Canellaceae": "Canellales",
    "Winteraceae": "Canellales",
    "Myristicaceae": "Magnoliales",

    # ─── 基部被子植物 ──────────────
    "Nymphaeaceae": "Nymphaeales",  # 睡莲科 → 睡莲目
    "Amborellaceae": "Amborellales",
    "Chloranthaceae": "Chloranthales", # 金粟兰科 → 金粟兰目
    "Ceratophyllaceae": "Ceratophyllales", # 金鱼藻科 → 金鱼藻目

    # ─── 石竹类 ──────────────────
    "Cactaceae": "Caryophyllales",  # 仙人掌科 → 石竹目
    "Caryophyllaceae": "Caryophyllales",
    "Amaranthaceae": "Caryophyllales", # 苋科 → 石竹目
    "Chenopodiaceae": "Caryophyllales",
    "Polygonaceae": "Caryophyllales",  # 蓼科 → 石竹目
    "Portulacaceae": "Caryophyllales", # 马齿苋科 → 石竹目
    "Nyctaginaceae": "Caryophyllales", # 紫茉莉科 → 石竹目
    "Droseraceae": "Caryophyllales",   # 茅膏菜科 → 石竹目
    "Plumbaginaceae": "Caryophyllales",

    # ─── 裸子植物 ─────────────────
    "Pinaceae": "Pinales",          # 松科 → 松柏目
    "Cupressaceae": "Cupressales",  # 柏科 → 柏木目
    "Taxaceae": "Cupressales",      # 红豆杉科 → 柏木目
    "Araucariaceae": "Araucariales",# 南洋杉科 → 南洋杉目
    "Podocarpaceae": "Araucariales",# 罗汉松科 → 南洋杉目
    "Ginkgoaceae": "Ginkgoales",    # 银杏科 → 银杏目
    "Cycadaceae": "Cycadales",      # 苏铁科 → 苏铁目
    "Zamiaceae": "Cycadales",       # 泽米科 → 苏铁目
    "Gnetaceae": "Gnetales",        # 买麻藤科 → 买麻藤目
    "Ephedraceae": "Ephedrales",    # 麻黄科 → 麻黄目
    "Welwitschiaceae": "Welwitschiales",

    # ─── 蕨类 ────────────────────
    "Polypodiaceae": "Polypodiales",
    "Pteridaceae": "Polypodiales",
    "Aspleniaceae": "Polypodiales",
    "Dryopteridaceae": "Polypodiales",
    "Cyatheaceae": "Cyatheales",
    "Equisetaceae": "Equisetales",
    "Salviniaceae": "Salviniales",
    "Marsileaceae": "Salviniales",
    "Ophioglossaceae": "Ophioglossales",
    "Psilotaceae": "Psilotales",
    "Marattiaceae": "Marattiales",
    "Osmundaceae": "Osmundales",
    "Hymenophyllaceae": "Hymenophyllales",
    "Gleicheniaceae": "Gleicheniales",
    "Schizaeaceae": "Schizaeales",
    "Lygodiaceae": "Schizaeales",

    # ─── 石松 ────────────────────
    "Lycopodiaceae": "Lycopodiales",
    "Selaginellaceae": "Selaginellales",
    "Isoetaceae": "Isoetales",

    # ─── 苔藓 ────────────────────
    "Bryaceae": "Bryales",
    "Polytrichaceae": "Polytrichales",
    "Sphagnaceae": "Sphagnales",
    "Funariaceae": "Funariales",
    "Hypnaceae": "Hypnales",
    "Marchantiaceae": "Marchantiales",
}

# 分类级中文名映射（只覆盖最常用部分，其他自动 fallback 到拉丁名）
RANK_CHINESE = {
    # 界
    "Plantae": "植物界",
    
    # 门
    "Tracheophyta": "维管植物门",
    "Pinophyta": "松柏门",
    "Ginkgophyta": "银杏门",
    "Magnoliophyta": "被子植物门",
    "Cycadophyta": "苏铁门",
    "Gnetophyta": "买麻藤门",
    "Lycopodiophyta": "石松门",
    "Polypodiophyta": "蕨类植物门",
    "Bryophyta": "苔藓植物门",
    "Marchantiophyta": "地钱门",
    "Anthocerotophyta": "角苔门",
    "Angiospermae": "被子植物门",

    # 纲
    "Magnoliopsida": "木兰纲",
    "Liliopsida": "百合纲",
    "Pinopsida": "松纲",
    "Ginkgoopsida": "银杏纲",
    "Cycadopsida": "苏铁纲",
    "Gnetopsida": "买麻藤纲",
    "Lycopodiopsida": "石松纲",
    "Polypodiopsida": "真蕨纲",
    "Equisetopsida": "木贼纲",
    "Bryopsida": "藓纲",
    "Marchantiopsida": "地钱纲",
    "Jungermanniopsida": "叶苔纲",
    "Anthocerotopsida": "角苔纲",
    "Polypodiopsida": "真蕨纲",

    # 目
    "Poales": "禾本目",
    "Asparagales": "天门冬目",
    "Liliales": "百合目",
    "Arecales": "棕榈目",
    "Zingiberales": "姜目",
    "Commelinales": "鸭跖草目",
    "Alismatales": "泽泻目",
    "Dioscoreales": "薯蓣目",
    "Pandanales": "露兜树目",
    "Acorales": "菖蒲目",
    "Petrosaviales": "无叶莲目",
    "Rosales": "蔷薇目",
    "Fabales": "豆目",
    "Cucurbitales": "葫芦目",
    "Fagales": "壳斗目",
    "Myrtales": "桃金娘目",
    "Malvales": "锦葵目",
    "Brassicales": "十字花目",
    "Sapindales": "无患子目",
    "Zygophyllales": "蒺藜目",
    "Celastrales": "卫矛目",
    "Oxalidales": "酢浆草目",
    "Geraniales": "牻牛儿苗目",
    "Malpighiales": "金虎尾目",
    "Asterales": "菊目",
    "Apiales": "伞形目",
    "Aquifoliales": "冬青目",
    "Dipsacales": "川续断目",
    "Lamiales": "唇形目",
    "Solanales": "茄目",
    "Boraginales": "紫草目",
    "Gentianales": "龙胆目",
    "Ericales": "杜鹃花目",
    "Cornales": "山茱萸目",
    "Saxifragales": "虎耳草目",
    "Vitales": "葡萄目",
    "Santalales": "檀香目",
    "Dilleniales": "五桠果目",
    "Ranunculales": "毛茛目",
    "Proteales": "山龙眼目",
    "Trochodendrales": "昆栏树目",
    "Buxales": "黄杨目",
    "Gunnerales": "大叶草目",
    "Berberidopsidales": "红珊藤目",
    "Caryophyllales": "石竹目",
    "Nymphaeales": "睡莲目",
    "Amborellales": "无油樟目",
    "Chloranthales": "金粟兰目",
    "Ceratophyllales": "金鱼藻目",
    "Canellales": "白桂皮目",
    "Piperales": "胡椒目",
    "Magnoliales": "木兰目",
    "Laurales": "樟目",
    "Crossosomatales": "十齿花目",
    "Picramniales": "苦木目",
    "Huerteales": "十萼花目",
    "Garryales": "丝缨花目",
    "Icacinales": "茶茱萸目",
    "Metteniusales": "水螅花目",
    "Vahliales": "瓦利花目",
    "Bruniales": "布伦花目",
    "Escalloniales": "鼠刺目",
    "Paracryphiales": "寄生花目",
    "Pinales": "松柏目",
    "Araucariales": "南洋杉目",
    "Cupressales": "柏木目",
    "Ginkgoales": "银杏目",
    "Cycadales": "苏铁目",
    "Gnetales": "买麻藤目",
    "Ephedrales": "麻黄目",
    "Welwitschiales": "百岁兰目",
    "Lycopodiales": "石松目",
    "Isoetales": "水韭目",
    "Selaginellales": "卷柏目",
    "Equisetales": "木贼目",
    "Ophioglossales": "瓶尔小草目",
    "Psilotales": "松叶蕨目",
    "Marattiales": "观音座莲目",
    "Osmundales": "紫萁目",
    "Hymenophyllales": "膜蕨目",
    "Gleicheniales": "里白目",
    "Schizaeales": "莎草蕨目",
    "Salviniales": "槐叶苹目",
    "Cyatheales": "桫椤目",
    "Polypodiales": "水龙骨目",
    "Bryales": "真藓目",
    "Dicranales": "曲尾藓目",
    "Hypnales": "灰藓目",
    "Polytrichales": "金发藓目",
    "Sphagnales": "泥炭藓目",
    "Funariales": "葫芦藓目",
    "Grimmiales": "紫萼藓目",
    "Hookeriales": "油藓目",
    "Pottiales": "丛藓目",
    "Marchantiales": "地钱目",
    "Sphaerocarpales": "囊果苔目",
    "Lunulariales": "半月苔目",
    "Jungermanniales": "叶苔目",
    "Porellales": "光萼苔目",
    "Ptilidiales": "毛叶苔目",
    "Fossombroniales": "小叶苔目",
    "Pelliales": "溪苔目",
    "Anthocerotales": "角苔目",
    "Notothyladales": "短角苔目",
    "Dendrocerotales": "树角苔目",
    "Austrobaileyales": "木兰藤目",
}

# 科中文名（常见）
FAMILY_CHINESE = {
    "Poaceae": "禾本科",
    "Orchidaceae": "兰科",
    "Amaryllidaceae": "石蒜科",
    "Asphodelaceae": "阿福花科",
    "Liliaceae": "百合科",
    "Iridaceae": "鸢尾科",
    "Arecaceae": "棕榈科",
    "Zingiberaceae": "姜科",
    "Musaceae": "芭蕉科",
    "Commelinaceae": "鸭跖草科",
    "Araceae": "天南星科",
    "Dioscoreaceae": "薯蓣科",
    "Pandanaceae": "露兜树科",
    "Smilacaceae": "菝葜科",
    "Juncaceae": "灯心草科",
    "Cyperaceae": "莎草科",
    "Rosaceae": "蔷薇科",
    "Moraceae": "桑科",
    "Urticaceae": "荨麻科",
    "Rhamnaceae": "鼠李科",
    "Ulmaceae": "榆科",
    "Cannabaceae": "大麻科",
    "Fabaceae": "豆科",
    "Polygalaceae": "远志科",
    "Cucurbitaceae": "葫芦科",
    "Begoniaceae": "秋海棠科",
    "Fagaceae": "壳斗科",
    "Betulaceae": "桦木科",
    "Juglandaceae": "胡桃科",
    "Myrtaceae": "桃金娘科",
    "Lythraceae": "千屈菜科",
    "Onagraceae": "柳叶菜科",
    "Combretaceae": "使君子科",
    "Melastomataceae": "野牡丹科",
    "Malvaceae": "锦葵科",
    "Dipterocarpaceae": "龙脑香科",
    "Thymelaeaceae": "瑞香科",
    "Brassicaceae": "十字花科",
    "Sapindaceae": "无患子科",
    "Rutaceae": "芸香科",
    "Anacardiaceae": "漆树科",
    "Meliaceae": "楝科",
    "Simaroubaceae": "苦木科",
    "Zygophyllaceae": "蒺藜科",
    "Celastraceae": "卫矛科",
    "Oxalidaceae": "酢浆草科",
    "Geraniaceae": "牻牛儿苗科",
    "Salicaceae": "杨柳科",
    "Violaceae": "堇菜科",
    "Euphorbiaceae": "大戟科",
    "Passifloraceae": "西番莲科",
    "Hypericaceae": "金丝桃科",
    "Clusiaceae": "藤黄科",
    "Asteraceae": "菊科",
    "Campanulaceae": "桔梗科",
    "Apiaceae": "伞形科",
    "Araliaceae": "五加科",
    "Aquifoliaceae": "冬青科",
    "Caprifoliaceae": "忍冬科",
    "Adoxaceae": "五福花科",
    "Valerianaceae": "缬草科",
    "Lamiaceae": "唇形科",
    "Oleaceae": "木樨科",
    "Plantaginaceae": "车前科",
    "Scrophulariaceae": "玄参科",
    "Bignoniaceae": "紫葳科",
    "Pedaliaceae": "胡麻科",
    "Acanthaceae": "爵床科",
    "Verbenaceae": "马鞭草科",
    "Gesneriaceae": "苦苣苔科",
    "Orobanchaceae": "列当科",
    "Solanaceae": "茄科",
    "Convolvulaceae": "旋花科",
    "Boraginaceae": "紫草科",
    "Rubiaceae": "茜草科",
    "Gentianaceae": "龙胆科",
    "Apocynaceae": "夹竹桃科",
    "Loganiaceae": "马钱科",
    "Ericaceae": "杜鹃花科",
    "Theaceae": "山茶科",
    "Primulaceae": "报春花科",
    "Ebenaceae": "柿科",
    "Symplocaceae": "山矾科",
    "Actinidiaceae": "猕猴桃科",
    "Sapotaceae": "山榄科",
    "Saxifragaceae": "虎耳草科",
    "Paeoniaceae": "芍药科",
    "Crassulaceae": "景天科",
    "Hamamelidaceae": "金缕梅科",
    "Vitaceae": "葡萄科",
    "Santalaceae": "檀香科",
    "Loranthaceae": "桑寄生科",
    "Dilleniaceae": "五桠果科",
    "Ranunculaceae": "毛茛科",
    "Berberidaceae": "小檗科",
    "Papaveraceae": "罂粟科",
    "Menispermaceae": "防己科",
    "Nelumbonaceae": "莲科",
    "Platanaceae": "悬铃木科",
    "Proteaceae": "山龙眼科",
    "Trochodendraceae": "昆栏树科",
    "Buxaceae": "黄杨科",
    "Gunneraceae": "大叶草科",
    "Myrothamnaceae": "密叶苔科",
    "Magnoliaceae": "木兰科",
    "Lauraceae": "樟科",
    "Piperaceae": "胡椒科",
    "Aristolochiaceae": "马兜铃科",
    "Canellaceae": "白桂皮科",
    "Winteraceae": "林仙科",
    "Myristicaceae": "肉豆蔻科",
    "Nymphaeaceae": "睡莲科",
    "Amborellaceae": "无油樟科",
    "Chloranthaceae": "金粟兰科",
    "Ceratophyllaceae": "金鱼藻科",
    "Cactaceae": "仙人掌科",
    "Caryophyllaceae": "石竹科",
    "Amaranthaceae": "苋科",
    "Polygonaceae": "蓼科",
    "Portulacaceae": "马齿苋科",
    "Nyctaginaceae": "紫茉莉科",
    "Droseraceae": "茅膏菜科",
    "Plumbaginaceae": "白花丹科",
    "Papaveraceae": "罂粟科",
    "Pinaceae": "松科",
    "Cupressaceae": "柏科",
    "Taxaceae": "红豆杉科",
    "Araucariaceae": "南洋杉科",
    "Podocarpaceae": "罗汉松科",
    "Ginkgoaceae": "银杏科",
    "Cycadaceae": "苏铁科",
    "Gnetaceae": "买麻藤科",
    "Ephedraceae": "麻黄科",
    "Welwitschiaceae": "百岁兰科",
    "Lycopodiaceae": "石松科",
    "Selaginellaceae": "卷柏科",
    "Isoetaceae": "水韭科",
    "Equisetaceae": "木贼科",
    "Polypodiaceae": "水龙骨科",
    "Pteridaceae": "凤尾蕨科",
    "Aspleniaceae": "铁角蕨科",
    "Dryopteridaceae": "鳞毛蕨科",
    "Cyatheaceae": "桫椤科",
    "Salviniaceae": "槐叶苹科",
    "Ophioglossaceae": "瓶尔小草科",
    "Psilotaceae": "松叶蕨科",
    "Marattiaceae": "合囊蕨科",
    "Osmundaceae": "紫萁科",
    "Hymenophyllaceae": "膜蕨科",
    "Gleicheniaceae": "里白科",
    "Schizaeaceae": "莎草蕨科",
    "Bryaceae": "真藓科",
    "Polytrichaceae": "金发藓科",
}

# 属中文名（常见属，按需添加）
GENUS_CHINESE = {
    "Camphora": "樟属",
    "Cinnamomum": "樟属",
    "Pinus": "松属",
    "Picea": "云杉属",
    "Abies": "冷杉属",
    "Salix": "柳属",
    "Populus": "杨属",
    "Rosa": "蔷薇属",
    "Malus": "苹果属",
    "Prunus": "李属",
    "Wisteria": "紫藤属",
    "Sorbaria": "珍珠梅属",
    "Ginkgo": "银杏属",
    "Salvia": "鼠尾草属",
    "Quercus": "栎属",
    "Ficus": "榕属",
    "Morus": "桑属",
    "Camellia": "山茶属",
    "Rhododendron": "杜鹃花属",
    "Magnolia": "木兰属",
    "Jasminum": "素馨属",
    "Ligustrum": "女贞属",
    "Osmanthus": "木樨属",
    "Bambusa": "簕竹属",
    "Phyllostachys": "刚竹属",
    "Nelumbo": "莲属",
    "Nymphaea": "睡莲属",
}

# 属 → 纲/门/界 映射（兜底，当 PlantNet 未返回 class/phylum 时使用）
# 主要覆盖裸子植物、蕨类、苔藓等非木兰纲植物
GENUS_TO_BASIC = {
    # ─── 松柏类（Pinopsida / Pinophyta）───────────
    "Pinus": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Picea": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Abies": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Cedrus": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Larix": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Pseudotsuga": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Tsuga": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Juniperus": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Cupressus": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Thuja": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Chamaecyparis": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Sequoia": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Sequoiadendron": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Metasequoia": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Cryptomeria": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Taxodium": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Taxus": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Cephalotaxus": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Araucaria": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Agathis": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Podocarpus": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    "Sciadopitys": {"class_name": "Pinopsida", "phylum": "Pinophyta", "kingdom": "Plantae"},
    # ─── 银杏（Ginkgoopsida / Ginkgophyta）───────
    "Ginkgo": {"class_name": "Ginkgoopsida", "phylum": "Ginkgophyta", "kingdom": "Plantae"},
    # ─── 苏铁（Cycadopsida / Cycadophyta）───────
    "Cycas": {"class_name": "Cycadopsida", "phylum": "Cycadophyta", "kingdom": "Plantae"},
    "Zamia": {"class_name": "Cycadopsida", "phylum": "Cycadophyta", "kingdom": "Plantae"},
    "Ceratozamia": {"class_name": "Cycadopsida", "phylum": "Cycadophyta", "kingdom": "Plantae"},
    "Dioon": {"class_name": "Cycadopsida", "phylum": "Cycadophyta", "kingdom": "Plantae"},
    "Encephalartos": {"class_name": "Cycadopsida", "phylum": "Cycadophyta", "kingdom": "Plantae"},
    "Macrozamia": {"class_name": "Cycadopsida", "phylum": "Cycadophyta", "kingdom": "Plantae"},
    # ─── 买麻藤（Gnetopsida / Gnetophyta）───────
    "Gnetum": {"class_name": "Gnetopsida", "phylum": "Gnetophyta", "kingdom": "Plantae"},
    "Ephedra": {"class_name": "Gnetopsida", "phylum": "Gnetophyta", "kingdom": "Plantae"},
    "Welwitschia": {"class_name": "Gnetopsida", "phylum": "Gnetophyta", "kingdom": "Plantae"},
}
