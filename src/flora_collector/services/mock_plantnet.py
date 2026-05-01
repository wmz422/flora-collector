"""
Flora Collector — 模拟植物识别（无 API Key 时使用）
"""
import random
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


# 模拟数据：常见植物的识别样本
MOCK_PLANTS = [
    {
        "scientific_name": "Rosa chinensis",
        "chinese_name": "月季",
        "common_name": "Chinese Rose",
        "family": "Rosaceae",
        "genus": "Rosa",
        "description": "蔷薇科蔷薇属植物，四季开花，花色丰富。",
        "habitat": "广泛栽培于中国各地，喜光、耐寒。",
    },
    {
        "scientific_name": "Camellia sinensis",
        "chinese_name": "茶树",
        "common_name": "Tea Plant",
        "family": "Theaceae",
        "genus": "Camellia",
        "description": "山茶科山茶属，叶可制茶，是中国重要经济作物。",
        "habitat": "中国南方山区广泛种植。",
    },
    {
        "scientific_name": "Prunus mume",
        "chinese_name": "梅花",
        "common_name": "Japanese Apricot",
        "family": "Rosaceae",
        "genus": "Prunus",
        "description": "蔷薇科李属，早春开花，花色白、粉、红。",
        "habitat": "原产中国南方，各地有栽培。",
    },
    {
        "scientific_name": "Nelumbo nucifera",
        "chinese_name": "荷花",
        "common_name": "Sacred Lotus",
        "family": "Nelumbonaceae",
        "genus": "Nelumbo",
        "description": "莲科莲属，水生植物，花大色艳，根茎为莲藕。",
        "habitat": "池塘、湖泊等静水水体。",
    },
    {
        "scientific_name": "Chrysanthemum morifolium",
        "chinese_name": "菊花",
        "common_name": "Florist's Chrysanthemum",
        "family": "Asteraceae",
        "genus": "Chrysanthemum",
        "description": "菊科菊属，秋季开花，品种极多。",
        "habitat": "广泛栽培，喜凉爽气候。",
    },
    {
        "scientific_name": "Paeonia suffruticosa",
        "chinese_name": "牡丹",
        "common_name": "Tree Peony",
        "family": "Paeoniaceae",
        "genus": "Paeonia",
        "description": "芍药科芍药属，花大色艳，被誉为花王。",
        "habitat": "中国中部和北部，喜光耐寒。",
    },
    {
        "scientific_name": "Bambusoideae",
        "chinese_name": "竹子",
        "common_name": "Bamboo",
        "family": "Poaceae",
        "genus": "Bambusoideae",
        "description": "禾本科竹亚科，多年生禾本科植物。",
        "habitat": "中国南方广泛分布。",
    },
    {
        "scientific_name": "Ginkgo biloba",
        "chinese_name": "银杏",
        "common_name": "Ginkgo",
        "family": "Ginkgoaceae",
        "genus": "Ginkgo",
        "description": "银杏科银杏属，活化石植物，秋季叶色金黄。",
        "habitat": "中国特有，各地有栽培。",
    },
    {
        "scientific_name": "Lavandula angustifolia",
        "chinese_name": "薰衣草",
        "common_name": "English Lavender",
        "family": "Lamiaceae",
        "genus": "Lavandula",
        "description": "唇形科薰衣草属，芳香植物，花紫色。",
        "habitat": "地中海地区，中国有引种栽培。",
    },
    {
        "scientific_name": "Cymbidium goeringii",
        "chinese_name": "春兰",
        "common_name": "Spring Orchid",
        "family": "Orchidaceae",
        "genus": "Cymbidium",
        "description": "兰科兰属，中国传统名花，春季开花。",
        "habitat": "中国中南部山区林下。",
    },
]

# 器官描述映射
ORGAN_DESCRIPTIONS = {
    "flower": "花",
    "leaf": "叶",
    "fruit": "果实",
    "stem": "茎",
    "bark": "树皮",
    "root": "根",
    "whole": "整体",
}


class MockPlantNetService:
    """模拟识别服务，返回预置的植物数据"""

    async def identify(
        self, image_path: str, organs: List[str] = None
    ) -> Dict[str, Any]:
        """模拟识别：从预置数据中随机选一个"""
        img_path = Path(image_path)
        file_size = img_path.stat().st_size if img_path.exists() else 0

        plant = random.choice(MOCK_PLANTS)
        organ = (organs or ["leaf"])[0]
        confidence = round(random.uniform(0.78, 0.99), 3)

        return {
            "success": True,
            "data": {
                "results": [r for r in [
                    {
                        "score": confidence,
                        "species": {
                            "scientificName": plant["scientific_name"],
                            "commonNames": [plant["common_name"]],
                            "family": {"scientificName": plant["family"]},
                            "genus": {"scientificName": plant["genus"]},
                            "gbifId": None,
                        },
                    },
                    {
                        "score": round(confidence * 0.85, 3),
                        "species": {
                            "scientificName": plant["scientific_name"],
                            "commonNames": [plant["common_name"]],
                            "family": {"scientificName": plant["family"]},
                            "genus": {"scientificName": plant["genus"]},
                            "gbifId": None,
                        },
                    } if random.random() > 0.5 else None,
                ] if r is not None],
            },
            "organ": organ,
            "organ_label": ORGAN_DESCRIPTIONS.get(organ, organ),
            "image_size": file_size,
            "mock": True,
        }

    @staticmethod
    def parse_results(api_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not api_result.get("success"):
            return []

        data = api_result.get("data", {})
        results = data.get("results", [])
        parsed = []
        for r in results[:5]:
            if r is None:
                continue
            species = r.get("species", {})
            parsed.append({
                "scientific_name": species.get("scientificName", ""),
                "common_name": (
                    species.get("commonNames", [None])[0]
                    if species.get("commonNames") else ""
                ),
                "family": species.get("family", {}).get("scientificName", ""),
                "genus": species.get("genus", {}).get("scientificName", ""),
                "score": r.get("score", 0.0),
                "gbif_id": species.get("gbifId"),
            })
        return parsed
