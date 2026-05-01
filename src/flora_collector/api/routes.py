"""
Flora Collector — API 路由 v2（双图鉴 + 分类树）
"""
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
from io import BytesIO

import aiohttp
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header

from ..config import IMAGES_DIR, PLANTNET_API_KEY
from ..services.plantnet import PlantNetService, build_taxonomy_dict
from ..services.mock_plantnet import MockPlantNetService
from ..services.inaturalist import INaturalistService
from ..services import encyclopedia as enc_svc
from ..services import taxonomy as tax_svc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

# ── 识别服务 ─────────────────────────────────────
if PLANTNET_API_KEY:
    plantnet = PlantNetService()
    logger.info("Using REAL PlantNet API")
else:
    plantnet = MockPlantNetService()
    logger.info("Using MOCK PlantNet (set PLANTNET_API_KEY for real)")
inat = INaturalistService()

# ── 辅助函数 ─────────────────────────────────────
def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """获取当前用户 ID，缺省为 default"""
    return x_user_id or "default"


def compress_image(content: bytes, max_size: int = 1200, quality: int = 70) -> bytes:
    """压缩图片，缩小到 max_size 以内，适合手机大图上传"""
    try:
        img = Image.open(BytesIO(content))
        # 转 RGB（去掉 RGBA/调色板模式）
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # 缩小到 max_size
        w, h = img.size
        if w > max_size or h > max_size:
            ratio = min(max_size / w, max_size / h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()
    except Exception:
        return content  # 压缩失败就返回原图


# ══════════════════════════════════════════════════
# 健康检查
# ══════════════════════════════════════════════════

@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ══════════════════════════════════════════════════
# 识别（核心入口）
# ══════════════════════════════════════════════════

@router.post("/identify")
async def identify_plant(
    image: UploadFile = File(...),
    organ: str = Form("leaf"),
    x_user_id: Optional[str] = Header(None),
):
    user_id = get_user_id(x_user_id)
    ext = Path(image.filename or "photo.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = IMAGES_DIR / filename

    # 压缩上传的图片（手机大图 → ~200KB）
    content = await image.read()
    content = compress_image(content)
    filepath.write_bytes(content)

    # 调用识别服务
    result = await plantnet.identify(str(filepath), organs=[organ])
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "识别失败"))

    parsed = plantnet.parse_results(result)
    if not parsed:
        return {
            "success": True,
            "identified": False,
            "message": "未能识别出植物",
        }

    top = parsed[0]

    # 构建 taxonomy dict（含属→纲/门/界兜底）
    taxonomy = build_taxonomy_dict(top)

    # 记录发现（双图鉴模式）
    discovery = enc_svc.record_discovery(
        user_id=user_id,
        scientific_name=top["scientific_name"],
        taxonomy=taxonomy,
        plant_part=organ,
        confidence=top["score"],
        image_path=str(filepath),
    )

    if not discovery.get("success"):
        raise HTTPException(500, discovery.get("error", "记录失败"))

    return {
        "success": True,
        "identified": True,
        "top_matches": parsed,
        "discovery": discovery,
    }


# ══════════════════════════════════════════════════
# 图鉴统计
# ══════════════════════════════════════════════════

@router.get("/encyclopedia/user")
async def get_user_encyclopedia(x_user_id: Optional[str] = Header(None)):
    """用户个人图鉴统计"""
    user_id = get_user_id(x_user_id)
    return enc_svc.get_user_encyclopedia_stats(user_id)


@router.get("/encyclopedia/global")
async def get_global_encyclopedia():
    """全球图鉴统计"""
    return enc_svc.get_global_encyclopedia_stats()


# ══════════════════════════════════════════════════
# 物种详情
# ══════════════════════════════════════════════════

@router.get("/species/{species_id}")
async def get_species_detail(
    species_id: int,
    x_user_id: Optional[str] = Header(None),
):
    """物种详情 + 全球/用户收集数据"""
    user_id = get_user_id(x_user_id)
    result = enc_svc.get_species_detail(species_id, user_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


# ══════════════════════════════════════════════════
# 分类树
# ══════════════════════════════════════════════════

@router.get("/taxonomy/tree")
async def get_taxonomy_tree(
    scope: str = "world",
    x_user_id: Optional[str] = Header(None),
):
    """完整分类树（界门纲目科属种）
    scope=world: 全球图鉴（所有物种，未发现显示???）
    scope=user:  个人图鉴（只显示已发现的）
    """
    user_id = get_user_id(x_user_id) if scope == "user" else None
    tree_tree = tax_svc.build_taxonomy_tree(scope=scope, user_id=user_id)
    stats = tax_svc.get_global_stats()
    return {
        "total_species": stats["total_species"],
        "total_discovered": stats["total_discovered"],
        "completion_pct": stats["completion_pct"],
        "tree": tree_tree,
    }


# ══════════════════════════════════════════════════
# iNaturalist 数据拉取
# ══════════════════════════════════════════════════

@router.get("/search/inaturalist")
async def search_inaturalist(q: str):
    results = await inat.search_taxa(q)
    return {"results": [inat.parse_taxon(t) for t in results]}


@router.post("/seed/inaturalist/{taxon_id}")
async def seed_from_inaturalist(taxon_id: int):
    """从 iNaturalist 导入一个物种到全球图鉴"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{inat.BASE_URL}/taxa/{taxon_id}") as resp:
            if resp.status != 200:
                raise HTTPException(400, "查询失败")
            data = await resp.json()
            results = data.get("results", [])
            if not results:
                raise HTTPException(404, "未找到该物种")

    taxon = results[0]
    parsed = inat.parse_taxon(taxon)

    # 如果 species 已存在，返回
    existing = enc_svc.get_species_detail_by_name(parsed["scientific_name"])
    if existing:
        return {"success": True, "species_id": existing.id, "message": "已存在"}

    discovery = enc_svc.record_discovery(
        user_id="system",
        scientific_name=parsed["scientific_name"],
        taxonomy=parsed,
    )
    if not discovery.get("success"):
        raise HTTPException(400, discovery.get("error", "导入失败"))

    return {
        "success": True,
        "species_id": discovery["species_id"],
        "is_new_global": discovery.get("is_new_global", False),
    }
