"""
Flora Collector — 补充中文名和描述
针对那些从 iNaturalist 拉取但没有中文信息的物种
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from flora_collector.models import init_db, Species, get_session

EXTRA_INFO = {
    "Prunus persica": {
        "chinese_name": "桃花",
        "description": "蔷薇科李属落叶小乔木，春季开花，花粉红色，果实为桃。",
        "habitat": "原产中国，各地广泛栽培。",
    },
    "Rhododendron simsii": {
        "chinese_name": "杜鹃花",
        "description": "杜鹃花科杜鹃花属灌木，春季开花，花色艳丽，为中国十大名花之一。",
        "habitat": "中国中南部山区广泛分布，喜酸性土壤。",
    },
    "Jasminum sambac": {
        "chinese_name": "茉莉花",
        "description": "木樨科素馨属灌木，花白色，香气浓郁，可用于窨制花茶。",
        "habitat": "原产印度，中国南方广泛栽培。",
    },
    "Narcissus tazetta": {
        "chinese_name": "水仙",
        "description": "石蒜科水仙属多年生草本，冬季开花，花白色带黄心，清香，是中国传统年花。",
        "habitat": "原产地中海地区，中国广泛盆栽。",
    },
    "Lilium brownii": {
        "chinese_name": "百合",
        "description": "百合科百合属多年生草本，花大而美，鳞茎可食用。",
        "habitat": "中国中部和南方山区有分布。",
    },
    "Rosa rugosa": {
        "chinese_name": "玫瑰",
        "description": "蔷薇科蔷薇属灌木，枝密刺，花紫红色，芳香，可提取精油。",
        "habitat": "原产中国东北、朝鲜、日本，各地有栽培。",
    },
    "Pinus massoniana": {
        "chinese_name": "马尾松",
        "description": "松科松属常绿乔木，针叶两针一束，是中国南方最重要的用材树种之一。",
        "habitat": "中国南方广泛分布，喜光、耐贫瘠。",
    },
    "Firmiana simplex": {
        "chinese_name": "梧桐",
        "description": "锦葵科梧桐属落叶乔木，树皮青绿色，叶大形美。",
        "habitat": "原产中国，各地有栽培。",
    },
    "Ficus microcarpa": {
        "chinese_name": "榕树",
        "description": "桑科榕属常绿大乔木，有众多气生根，树冠巨大，是南方常见绿化树种。",
        "habitat": "中国南方广泛分布，喜温暖湿润。",
    },
    "Populus alba": {
        "chinese_name": "银白杨",
        "description": "杨柳科杨属落叶乔木，叶背银白色，生长迅速。",
        "habitat": "中国北方和西北地区有分布。",
    },
    "Styphnolobium japonicum": {
        "chinese_name": "国槐",
        "description": "豆科槐属落叶乔木，中国特产，花可食，树形优美。",
        "habitat": "原产中国，南北各地广泛栽培。",
    },
    "Camellia japonica": {
        "chinese_name": "山茶花",
        "description": "山茶科山茶属常绿灌木或小乔木，冬春开花，花大色艳，为中国十大名花之一。",
        "habitat": "原产中国南方，喜半阴、湿润环境。",
    },
    "Oryza sativa": {
        "chinese_name": "水稻",
        "description": "禾本科稻属一年生草本，最重要的粮食作物之一，养活了世界半数人口。",
        "habitat": "广泛栽培于亚洲水田。",
    },
    "Triticum aestivum": {
        "chinese_name": "小麦",
        "description": "禾本科小麦属一年生草本，世界三大谷物之一。",
        "habitat": "广泛栽培于温带地区。",
    },
    "Gossypium hirsutum": {
        "chinese_name": "陆地棉",
        "description": "锦葵科棉属一年生草本，纤维用于纺织，是最重要的天然纤维作物。",
        "habitat": "原产中美洲，世界各地广泛栽培。",
    },
    "Brassica napus": {
        "chinese_name": "油菜",
        "description": "十字花科芸薹属一年或二年生草本，花黄色，种子可榨油。",
        "habitat": "广泛栽培，喜凉爽气候。",
    },
    "Artemisia argyi": {
        "chinese_name": "艾草",
        "description": "菊科蒿属多年生草本，有特殊香气，端午节民俗用品，也可药用。",
        "habitat": "中国各地广泛分布。",
    },
    "Lycium chinense": {
        "chinese_name": "枸杞",
        "description": "茄科枸杞属灌木，果实枸杞子为常用中药材。",
        "habitat": "中国南北各地均有分布。",
    },
    "Mentha canadensis": {
        "chinese_name": "薄荷",
        "description": "唇形科薄荷属多年生草本，全株有清凉香气，可食用或药用。",
        "habitat": "中国各地广泛分布，喜湿润环境。",
    },
    "Taraxacum mongolicum": {
        "chinese_name": "蒲公英",
        "description": "菊科蒲公英属多年生草本，头状花序黄色，种子有白色冠毛可随风传播。",
        "habitat": "中国各地广泛分布，常见于路旁、田野。",
    },
    "Capsella bursa-pastoris": {
        "chinese_name": "荠菜",
        "description": "十字花科荠属一年或二年生草本，春季常见野菜。",
        "habitat": "中国各地广泛分布。",
    },
    "Plantago asiatica": {
        "chinese_name": "车前草",
        "description": "车前科车前属多年生草本，叶基生，穗状花序，全草可入药。",
        "habitat": "中国各地广泛分布。",
    },
    "Setaria viridis": {
        "chinese_name": "狗尾草",
        "description": "禾本科狗尾草属一年生草本，圆锥花序呈圆柱状似狗尾，常见杂草。",
        "habitat": "中国各地广泛分布。",
    },
    "Viola philippica": {
        "chinese_name": "紫花地丁",
        "description": "堇菜科堇菜属多年生草本，早春开花，花紫色，全草可入药。",
        "habitat": "中国各地广泛分布。",
    },
    "Ipomoea nil": {
        "chinese_name": "牵牛花",
        "description": "旋花科虎掌藤属一年生缠绕草本，花喇叭状，晨开午谢。",
        "habitat": "原产热带美洲，中国各地有栽培或逸为野生。",
    },
    "Jasminum nudiflorum": {
        "chinese_name": "迎春花",
        "description": "木樨科素馨属落叶灌木，早春先花后叶，花黄色，是春季最早开花的植物之一。",
        "habitat": "原产中国，各地园林广泛栽培。",
    },
    "Opuntia dillenii": {
        "chinese_name": "仙人掌",
        "description": "仙人掌科仙人掌属灌木状肉质植物，茎扁平如掌，有刺。",
        "habitat": "原产美洲，中国南方有野生或栽培。",
    },
    "Mimosa pudica": {
        "chinese_name": "含羞草",
        "description": "豆科含羞草属草本或亚灌木，叶受触碰即闭合下垂，趣味性强。",
        "habitat": "原产热带美洲，中国南方有逸生。",
    },
    "Aloe vera": {
        "chinese_name": "库拉索芦荟",
        "description": "阿福花科芦荟属多年生肉质草本，叶肥厚多汁，可用于护肤和药用。",
        "habitat": "原产阿拉伯半岛，世界各地广泛栽培。",
    },
    "Cylindropuntia imbricata": {
        "chinese_name": "仙人掌",
        "description": "仙人掌科圆柱掌属灌木状肉质植物，茎节圆柱形。",
        "habitat": "原产美洲，引种栽培。",
    },
    "Malus domestica": {
        "chinese_name": "苹果",
        "description": "蔷薇科苹果属落叶乔木，果实为常见水果。",
        "habitat": "广泛栽培于温带地区。",
    },
    "Solanum lycopersicum": {
        "chinese_name": "番茄",
        "description": "茄科茄属一年生草本，果实为常见蔬菜/水果。",
        "habitat": "原产南美洲，世界各地广泛栽培。",
    },
    "Cucumis sativus": {
        "chinese_name": "黄瓜",
        "description": "葫芦科黄瓜属一年生攀缘草本，果实为常见蔬菜。",
        "habitat": "原产南亚，世界各地广泛栽培。",
    },
    "Citrullus lanatus": {
        "chinese_name": "西瓜",
        "description": "葫芦科西瓜属一年生蔓生草本，果实为夏季消暑佳品。",
        "habitat": "原产非洲，世界各地广泛栽培。",
    },
    "Prunus serrulata": {
        "chinese_name": "樱花",
        "description": "蔷薇科李属落叶乔木，春季开花，花团锦簇，花期短暂而绚烂。",
        "habitat": "原产中国、日本、朝鲜，各地园林广泛栽培。",
    },
}

def fill_extra_info():
    init_db()
    session = get_session()
    try:
        count = 0
        for sci_name, info in EXTRA_INFO.items():
            species = session.query(Species).filter_by(scientific_name=sci_name).first()
            if species:
                updated = False
                if info.get("chinese_name") and not species.chinese_name:
                    species.chinese_name = info["chinese_name"]
                    updated = True
                if info.get("description") and not species.description:
                    species.description = info["description"]
                    updated = True
                if info.get("habitat") and not species.habitat:
                    species.habitat = info["habitat"]
                    updated = True
                if updated:
                    count += 1
                    print(f"  ✅ {sci_name} → {info.get('chinese_name', '')}")
        session.commit()
        print(f"\n补充完成：{count} 个物种已更新")
    finally:
        session.close()

if __name__ == "__main__":
    fill_extra_info()
