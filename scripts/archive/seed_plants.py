"""
Flora Collector — 种子数据脚本
从 iNaturalist 拉取真实植物数据 + 补充中文信息
"""
import asyncio
import logging
import sys
from pathlib import Path

# 添加项目 src 目录到 path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from flora_collector.models import init_db, Species, EncyclopediaEntry, get_session
from flora_collector.services.inaturalist import INaturalistService
from flora_collector.services.encyclopedia import EncyclopediaService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 目标植物列表（中文名 + 学名，用于搜索 iNaturalist）
TARGET_PLANTS = [
    # ── 常见观赏植物 ──
    ("月季", "Rosa chinensis"),
    ("梅花", "Prunus mume"),
    ("牡丹", "Paeonia suffruticosa"),
    ("菊花", "Chrysanthemum morifolium"),
    ("荷花", "Nelumbo nucifera"),
    ("樱花", "Prunus serrulata"),
    ("桃花", "Prunus persica"),
    ("桂花", "Osmanthus fragrans"),
    ("山茶花", "Camellia japonica"),
    ("杜鹃花", "Rhododendron simsii"),
    ("茉莉花", "Jasminum sambac"),
    ("兰花/春兰", "Cymbidium goeringii"),
    ("水仙", "Narcissus tazetta"),
    ("百合", "Lilium brownii"),
    ("玫瑰", "Rosa rugosa"),

    # ── 树木 ──
    ("银杏", "Ginkgo biloba"),
    ("松树/马尾松", "Pinus massoniana"),
    ("柳树/垂柳", "Salix babylonica"),
    ("枫树/鸡爪槭", "Acer palmatum"),
    ("梧桐", "Firmiana simplex"),
    ("樟树", "Cinnamomum camphora"),
    ("榕树", "Ficus microcarpa"),
    ("白杨", "Populus alba"),
    ("竹子/毛竹", "Phyllostachys edulis"),
    ("槐树/国槐", "Styphnolobium japonicum"),

    # ── 药用/经济植物 ──
    ("茶树", "Camellia sinensis"),
    ("水稻", "Oryza sativa"),
    ("小麦", "Triticum aestivum"),
    ("棉花", "Gossypium hirsutum"),
    ("油菜", "Brassica napus"),
    ("向日葵", "Helianthus annuus"),
    ("薰衣草", "Lavandula angustifolia"),
    ("艾草", "Artemisia argyi"),
    ("枸杞", "Lycium chinense"),
    ("薄荷", "Mentha canadensis"),

    # ── 野菜野花 ──
    ("蒲公英", "Taraxacum mongolicum"),
    ("荠菜", "Capsella bursa-pastoris"),
    ("车前草", "Plantago asiatica"),
    ("狗尾草", "Setaria viridis"),
    ("紫花地丁", "Viola philippica"),
    ("牵牛花", "Ipomoea nil"),
    ("迎春花", "Jasminum nudiflorum"),
    ("仙人掌/仙人球", "Opuntia dillenii"),
    ("含羞草", "Mimosa pudica"),
    ("芦荟", "Aloe vera"),
    ("仙人掌", "Cylindropuntia imbricata"),

    # ── 果蔬 ──
    ("苹果", "Malus domestica"),
    ("番茄", "Solanum lycopersicum"),
    ("黄瓜", "Cucumis sativus"),
    ("西瓜", "Citrullus lanatus"),
]

# 备用的中文描述数据（当 API 获取不到时使用）
FALLBACK_DESCRIPTIONS = {
    "Rosa chinensis": {
        "chinese_name": "月季",
        "description": "蔷薇科蔷薇属植物，又称月月红，四季开花，花色丰富，是中国十大名花之一。",
        "habitat": "原产中国，全国各地广泛栽培，喜光、耐寒、耐旱。",
    },
    "Prunus mume": {
        "chinese_name": "梅花",
        "description": "蔷薇科李属植物，早春先花后叶，花色以白、粉、红为主，香气清幽，象征坚韧高洁。",
        "habitat": "原产中国南方，各地有栽培，耐寒、喜光。",
    },
    "Paeonia suffruticosa": {
        "chinese_name": "牡丹",
        "description": "芍药科芍药属植物，花大色艳，富丽堂皇，被誉为花王，是中国国花候选。",
        "habitat": "原产中国中北部，喜光、耐寒、怕积水。",
    },
    "Nelumbo nucifera": {
        "chinese_name": "荷花",
        "description": "莲科莲属水生植物，花大而美，根茎为莲藕，种子为莲子，全身是宝。",
        "habitat": "中国南北各地水域广泛分布栽培。",
    },
    "Ginkgo biloba": {
        "chinese_name": "银杏",
        "description": "银杏科银杏属落叶乔木，被誉为活化石，叶扇形，秋季金黄，果实为白果。",
        "habitat": "中国特有树种，各地有栽培，寿命极长。",
    },
    "Osmanthus fragrans": {
        "chinese_name": "桂花",
        "description": "木樨科木樨属常绿灌木或小乔木，秋季开花，花香浓郁，可用于制作桂花糕、桂花茶。",
        "habitat": "原产中国西南部，南方广泛栽培，喜光、喜温暖湿润气候。",
    },
    "Camellia sinensis": {
        "chinese_name": "茶树",
        "description": "山茶科山茶属常绿灌木或小乔木，嫩叶可制茶，是中国重要经济作物。",
        "habitat": "原产中国西南部，南方各省广泛种植，喜温暖湿润、酸性土壤。",
    },
    "Prunus serrulata": {
        "chinese_name": "樱花",
        "description": "蔷薇科李属落叶乔木，春季开花，花团锦簇，花色白、粉、红，花期短暂而绚烂。",
        "habitat": "原产中国、日本、朝鲜，各地园林广泛栽培。",
    },
    "Chrysanthemum morifolium": {
        "chinese_name": "菊花",
        "description": "菊科菊属多年生草本，秋季开花，品种繁多，花型花色极为丰富。",
        "habitat": "原产中国，全国各地广泛栽培，喜凉爽气候。",
    },
    "Cinnamomum camphora": {
        "chinese_name": "樟树",
        "description": "樟科樟属常绿大乔木，全株含樟脑香气，木材优良，是南方重要绿化树种。",
        "habitat": "中国南方广泛分布，喜温暖湿润气候。",
    },
    "Salix babylonica": {
        "chinese_name": "垂柳",
        "description": "杨柳科柳属落叶乔木，枝条细长下垂，姿态优美，常见于水边。",
        "habitat": "中国各地广泛栽培，喜水湿、耐寒。",
    },
    "Phyllostachys edulis": {
        "chinese_name": "毛竹",
        "description": "禾本科刚竹属高大竹类，笋可食用，竹材用途广泛，是中国最重要的经济竹种。",
        "habitat": "中国南方广泛分布，喜温暖湿润、土层深厚。",
    },
    "Lavandula angustifolia": {
        "chinese_name": "薰衣草",
        "description": "唇形科薰衣草属多年生草本或小灌木，花紫色，全株芳香，可提取精油。",
        "habitat": "原产地中海地区，中国有引种栽培。",
    },
    "Helianthus annuus": {
        "chinese_name": "向日葵",
        "description": "菊科向日葵属一年生高大草本，头状花序随太阳转动，种子可榨油或食用。",
        "habitat": "原产北美洲，世界各地广泛栽培。",
    },
    "Bambusoideae": {
        "chinese_name": "竹子",
        "description": "禾本科竹亚科植物的统称，多年生常绿植物，茎秆中空有节，用途极广。",
        "habitat": "中国南方广泛分布，喜温暖湿润气候。",
    },
    "Acer palmatum": {
        "chinese_name": "鸡爪槭",
        "description": "无患子科槭属落叶小乔木，叶掌状深裂，秋季叶色变红，是著名的红叶观赏树种。",
        "habitat": "原产中国、日本、朝鲜，喜光、喜湿润环境。",
    },
}

# iNaturalist ID 备选（直接用 taxon_id 拉取，更准确）
DIRECT_IDS = {
    "Rosa chinensis": 133392,
    "Prunus mume": 125415,
    "Ginkgo biloba": 50615,
    "Nelumbo nucifera": 61155,
    "Camellia sinensis": 1351703,
    "Osmanthus fragrans": 143201,
    "Chrysanthemum morifolium": 129372,
    "Helianthus annuus": 52536,
    "Cinnamomum camphora": 135413,
    "Phyllostachys edulis": 133036,
    "Acer palmatum": 133381,
    "Lavandula angustifolia": 131415,
    "Salix babylonica": 155279,
}


async def seed_plants():
    """主流程：拉取数据并填充数据库"""
    init_db()
    inat = INaturalistService()
    enc = EncyclopediaService()

    total = len(TARGET_PLANTS)
    success = 0
    skipped = 0
    errors = []

    for i, (cn_name, sci_name) in enumerate(TARGET_PLANTS, 1):
        print(f"[{i}/{total}] {cn_name} ({sci_name})...", end=" ")

        # 检查是否已存在
        session = get_session()
        existing = session.query(Species).filter_by(scientific_name=sci_name).first()
        session.close()
        if existing:
            print(f"✓ 已存在 (id={existing.id})")
            skipped += 1
            continue

        # 尝试从 iNaturalist 拉取
        plant_data = {
            "scientific_name": sci_name,
            "chinese_name": cn_name,
        }

        # 先用 taxon_id 直查
        taxon_id = DIRECT_IDS.get(sci_name)
        fetched = False
        if taxon_id:
            try:
                async with asyncio.timeout(10):
                    results = await inat.search_taxa(sci_name, limit=5)
                    for t in results:
                        if t.get("name", "").lower() == sci_name.lower():
                            parsed = inat.parse_taxon(t)
                            plant_data.update(parsed)
                            fetched = True
                            break
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"  iNaturalist search failed for {sci_name}: {e}")

        # iNaturalist 没找到，用备用数据
        if not fetched and sci_name in FALLBACK_DESCRIPTIONS:
            fb = FALLBACK_DESCRIPTIONS[sci_name]
            plant_data["chinese_name"] = fb["chinese_name"]
            plant_data["description"] = fb["description"]
            plant_data["habitat"] = fb["habitat"]
            fetched = True

        try:
            species = enc.get_or_create_species(plant_data)
            print(f"✅ id={species.id}")
            success += 1
        except Exception as e:
            print(f"❌ 失败: {e}")
            errors.append((sci_name, str(e)))

        # 避免 API 限流
        await asyncio.sleep(0.3)

    print(f"\n=== 完成 ===")
    print(f"成功: {success}, 跳过(已存在): {skipped}, 失败: {len(errors)}")
    if errors:
        for name, err in errors:
            print(f"  ❌ {name}: {err}")


if __name__ == "__main__":
    asyncio.run(seed_plants())
