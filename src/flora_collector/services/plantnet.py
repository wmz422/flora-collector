"""
Flora Collector — PlantNet 植物识别服务
"""
import logging
import aiohttp
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..config import PLANTNET_API_KEY, PLANTNET_API_URL

logger = logging.getLogger(__name__)


class PlantNetService:
    """调用 PlantNet API 进行植物识别"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or PLANTNET_API_KEY
        if not self.api_key:
            logger.warning("PlantNet API key not set. Recognition will fail.")

    async def identify(
        self,
        image_path: str,
        organs: List[str] = None,
    ) -> Dict[str, Any]:
        """
        识别植物

        Args:
            image_path: 图片文件路径
            organs: 植物器官类型，如 ["flower", "leaf"]

        Returns:
            API 返回的识别结果
        """
        if not self.api_key:
            return {"success": False, "error": "PLANTNET_API_KEY 未设置"}

        img_path = Path(image_path)
        if not img_path.exists():
            return {"success": False, "error": f"图片不存在: {image_path}"}

        url = f"{PLANTNET_API_URL}?api-key={self.api_key}"

        async with aiohttp.ClientSession() as session:
            with open(img_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("images", f, filename=img_path.name)

                if organs:
                    for organ in organs:
                        data.add_field("organs", organ)

                try:
                    async with session.post(url, data=data) as resp:
                        if resp.status != 200:
                            text = await resp.text()
                            return {
                                "success": False,
                                "error": f"API 返回 {resp.status}: {text[:200]}"
                            }
                        result = await resp.json()
                        return {"success": True, "data": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}

    @staticmethod
    def parse_results(api_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析 PlantNet API 返回结果，提取有用的识别信息

        Returns:
            [{"scientific_name": "...", "common_name": "...", "score": 0.95, "family": "..."}, ...]
        """
        if not api_result.get("success"):
            return []

        data = api_result.get("data", {})
        results = data.get("results", [])
        parsed = []

        for r in results[:5]:  # 取 top 5
            species = r.get("species", {})
            parsed.append({
                "scientific_name": species.get("scientificName", ""),
                "common_name": species.get("commonNames", [None])[0] if species.get("commonNames") else "",
                "kingdom": species.get("kingdom", {}).get("scientificName", ""),
                "phylum": species.get("phylum", {}).get("scientificName", ""),
                "class_name": species.get("class", {}).get("scientificName", ""),
                "order": species.get("order", {}).get("scientificName", ""),
                "family": species.get("family", {}).get("scientificName", ""),
                "genus": species.get("genus", {}).get("scientificName", ""),
                "score": r.get("score", 0.0),
                "gbif_id": species.get("gbifId"),
            })

        return parsed


def build_taxonomy_dict(parsed_match: dict) -> dict:
    """从 PlantNet 解析结果构建 taxonomy dict（供 record_discovery 使用）

    使用 GENUS_TO_BASIC 映射表兜底缺失的门/纲/界。
    """
    from .taxonomy_map import GENUS_TO_BASIC
    genus_name = parsed_match.get("genus", "")
    fallback = GENUS_TO_BASIC.get(genus_name, {})
    return {
        "scientific_name": parsed_match["scientific_name"],
        "chinese_name": parsed_match.get("chinese_name", ""),
        "common_name": parsed_match.get("common_name", ""),
        "kingdom": parsed_match.get("kingdom") or fallback.get("kingdom", "Plantae"),
        "phylum": parsed_match.get("phylum") or fallback.get("phylum", "Tracheophyta"),
        "class_name": parsed_match.get("class_name") or fallback.get("class_name", "Magnoliopsida"),
        "order": parsed_match.get("order", ""),
        "family": parsed_match.get("family", ""),
        "genus": genus_name,
    }
