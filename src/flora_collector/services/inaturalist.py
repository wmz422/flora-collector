"""
Flora Collector — iNaturalist 数据拉取服务
"""
import logging
import aiohttp
import asyncio
from typing import Optional, List, Dict, Any

from ..config import INATURALIST_API_URL

logger = logging.getLogger(__name__)


class INaturalistService:
    """从 iNaturalist API 拉取植物物种数据"""

    BASE_URL = INATURALIST_API_URL

    async def search_taxa(
        self,
        query: str,
        rank: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        搜索植物分类单元

        Args:
            query: 搜索关键词（学名或中文名）
            rank: 筛选分类等级（species, genus, family 等）
            limit: 返回数量
        """
        params = {
            "q": query,
            "is_active": "true",
            "limit": min(limit, 200),
        }
        if rank:
            params["rank"] = rank

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/taxa",
                params=params,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"iNaturalist API error: {resp.status}")
                    return []
                data = await resp.json()
                return data.get("results", [])

    async def get_taxon_children(
        self,
        taxon_id: int,
        page: int = 1,
        per_page: int = 100,
    ) -> Dict[str, Any]:
        """获取某个分类单元的子级（比如科下的属）"""
        params = {
            "parent_id": taxon_id,
            "page": page,
            "per_page": min(per_page, 200),
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/taxa",
                params=params,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    return {"results": [], "total": 0}
                data = await resp.json()
                return data

    async def get_observations(
        self,
        taxon_id: int,
        photos: bool = True,
        page: int = 1,
        per_page: int = 50,
    ) -> List[Dict[str, Any]]:
        """获取某个物种的观察记录（含图片）"""
        params = {
            "taxon_id": taxon_id,
            "photos": str(photos).lower(),
            "page": page,
            "per_page": min(per_page, 200),
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/observations",
                params=params,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                return data.get("results", [])

    @staticmethod
    def parse_taxon(taxon: Dict[str, Any]) -> Dict[str, Any]:
        """将 iNaturalist taxon 转为我们的物种模型字段"""
        ancestry = taxon.get("ancestry", "").split("/") if taxon.get("ancestry") else []
        ancestors = {a.get("rank"): a.get("name", "") for a in taxon.get("ancestors", [])}

        # 提取代表图
        photo_url = ""
        default_photo = taxon.get("default_photo")
        if default_photo:
            photo_url = default_photo.get("medium_url") or default_photo.get("url", "")

        return {
            "scientific_name": taxon.get("name", ""),
            "chinese_name": "",  # iNaturalist 不一定有中文名
            "common_name": taxon.get("preferred_common_name", ""),
            "kingdom": ancestors.get("kingdom", ""),
            "phylum": ancestors.get("phylum", ""),
            "class_name": ancestors.get("class", ""),
            "order": ancestors.get("order", ""),
            "family": ancestors.get("family", ""),
            "genus": ancestors.get("genus", ""),
            "description": "",  # iNaturalist API 不直接返回描述
            "image_url": photo_url,
            "inaturalist_taxon_id": taxon.get("id"),
        }
