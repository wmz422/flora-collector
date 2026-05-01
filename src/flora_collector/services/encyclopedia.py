"""
Flora Collector — 双图鉴服务

核心流程：
  用户识别植物 → 创建/更新 GlobalEncyclopediaEntry
               → 创建/更新 UserEncyclopediaEntry
               → 自动补全中文名+描述
"""
import logging
from datetime import datetime
from typing import Optional

from ..models import (
    Species, GlobalEncyclopediaEntry, UserEncyclopediaEntry,
    CollectionRecord, PlantPart, Season,
    get_session
)
from .taxonomy import ensure_taxonomy_chain, get_species_taxonomy
from .iplant import fetch_iplant_data

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
# 核心入口
# ════════════════════════════════════════════════════════════════

def record_discovery(
    user_id: str,
    scientific_name: str,
    taxonomy: dict,
    plant_part: str = "whole",
    season: str = "year_round",
    confidence: float = 0.0,
    image_path: str = "",
) -> dict:
    """
    记录一次发现。这是核心方法。

    流程：
    1. 查找或创建 Species（含自动补中文名+描述）
    2. 创建/更新 GlobalEncyclopediaEntry
    3. 创建/更新 UserEncyclopediaEntry
    4. 写入 CollectionRecord
    5. 更新全局统计

    返回丰富的响应信息。
    """
    session = get_session()
    try:
        species, ge, is_new_global = _find_or_create_species(
            session, user_id, scientific_name, taxonomy,
        )

        user_entry, is_new_user = _ensure_user_entry(session, user_id, species, ge)
        _update_collection_progress(session, user_entry, plant_part, season)
        _create_collection_record(
            session, user_entry, user_id, species.id,
            plant_part, season, image_path, confidence,
        )
        ge = _update_global_stats(session, ge, user_id)

        session.commit()

        return {
            "success": True,
            "species_id": species.id,
            "scientific_name": species.scientific_name,
            "chinese_name": species.chinese_name or "",
            "is_new_global": is_new_global,
            "is_new_user": is_new_user,
            "completion_pct": user_entry.completion_pct,
            "discovery_count": user_entry.discovery_count,
            "total_global_discoveries": ge.total_discoveries,
        }

    except Exception as e:
        session.rollback()
        logger.error(f"record_discovery failed: {e}")
        return {"success": False, "error": str(e)}
    finally:
        session.close()


# ════════════════════════════════════════════════════════════════
# 子函数
# ════════════════════════════════════════════════════════════════

def _find_or_create_species(
    session, user_id: str, scientific_name: str, taxonomy: dict,
) -> tuple:
    """查找或创建 Species，同时创建 GlobalEncyclopediaEntry。

    Returns:
        (species, global_entry, is_new_global)
    """
    species = session.query(Species).filter_by(
        scientific_name=scientific_name
    ).first()

    if not species:
        return _create_new_species(session, user_id, scientific_name, taxonomy)

    # 物种已存在 — 确保有全局条目
    ge = session.query(GlobalEncyclopediaEntry).filter_by(
        species_id=species.id
    ).first()
    if not ge:
        ge = GlobalEncyclopediaEntry(
            species_id=species.id,
            first_discovered_at=datetime.utcnow(),
            first_discovered_by=user_id,
        )
        session.add(ge)
        session.flush()

    # 补爬缺失的描述
    _heal_missing_description(session, species)

    return species, ge, False


def _create_new_species(
    session, user_id: str, scientific_name: str, taxonomy: dict,
) -> tuple:
    """创建新物种（爬 iPlant 数据，建分类链，建全局条目）"""
    # 爬中国植物志
    iplant_data = fetch_iplant_data(scientific_name)

    if iplant_data and iplant_data.get("chinese_name"):
        name_data = iplant_data
        logger.info(f"iPlant: {scientific_name} → {name_data['chinese_name']}")
        _apply_iplant_taxonomy(taxonomy, iplant_data)
    else:
        name_data = {
            "chinese_name": "", "description": "",
            "name_source": "", "desc_source": "", "image_url": "",
        }
        logger.info(f"iPlant: {scientific_name} → 未找到，使用英文名")

    # 创建分类链
    genus = ensure_taxonomy_chain(taxonomy, session=session)

    species = Species(
        scientific_name=scientific_name,
        chinese_name=name_data.get("chinese_name", taxonomy.get("chinese_name", "")),
        common_name=taxonomy.get("common_name", ""),
        genus_id=genus.id,
        description=name_data.get("description", ""),
        image_url=name_data.get("image_url", ""),
        name_source=name_data.get("name_source", ""),
        desc_source=name_data.get("desc_source", ""),
    )
    session.add(species)
    session.flush()

    ge = GlobalEncyclopediaEntry(
        species_id=species.id,
        first_discovered_at=datetime.utcnow(),
        first_discovered_by=user_id,
        total_discoveries=0,
        unique_discoverers=0,
    )
    session.add(ge)
    session.flush()

    return species, ge, True


def _apply_iplant_taxonomy(taxonomy: dict, iplant_data: dict):
    """用 iPlant 的分类（更权威）覆盖 PlantNet 的分类"""
    iplant_tax = iplant_data.get("iplant_taxonomy", {})
    if not iplant_tax:
        return

    for k in ["kingdom", "phylum", "class_name", "order", "family", "genus"]:
        if iplant_tax.get(k):
            taxonomy[k] = iplant_tax[k]

    for k in ["kingdom_cn", "phylum_cn", "class_name_cn", "order_cn", "family_cn", "genus_cn"]:
        if iplant_data.get(k):
            taxonomy[k] = iplant_data[k]

    logger.info(
        f"iPlant taxonomy applied: {taxonomy.get('class_name')} "
        f"/ {taxonomy.get('order')} / {taxonomy.get('family')}"
    )


def _heal_missing_description(session, species: Species):
    """如果物种缺少描述，从 iPlant 补爬"""
    if species.description:
        return

    logger.info(f"补充描述: {species.scientific_name}")
    iplant_data = fetch_iplant_data(species.scientific_name)
    if not iplant_data or not iplant_data.get("description"):
        return

    species.description = iplant_data["description"]
    species.desc_source = "iplant"
    if iplant_data.get("chinese_name"):
        species.chinese_name = iplant_data["chinese_name"]
    if iplant_data.get("image_url"):
        species.image_url = iplant_data["image_url"]
    session.flush()
    logger.info(f"描述已补充: {len(iplant_data['description'])} 字")


def _ensure_user_entry(session, user_id: str, species: Species, ge: GlobalEncyclopediaEntry) -> tuple:
    """查找或创建用户图鉴条目，返回 (user_entry, is_new_user)"""
    user_entry = session.query(UserEncyclopediaEntry).filter_by(
        user_id=user_id, species_id=species.id
    ).first()

    if user_entry:
        if not user_entry.is_discovered:
            user_entry.is_discovered = 1
            user_entry.discovered_at = datetime.utcnow()
        user_entry.discovery_count = (user_entry.discovery_count or 0) + 1
        return user_entry, False

    user_entry = UserEncyclopediaEntry(
        user_id=user_id,
        species_id=species.id,
        global_entry_id=ge.id,
        is_discovered=1,
        discovered_at=datetime.utcnow(),
        discovery_count=1,
    )
    session.add(user_entry)
    session.flush()
    return user_entry, True


def _update_collection_progress(session, user_entry: UserEncyclopediaEntry, plant_part: str, season: str):
    """更新用户对该物种的器官/季节收集进度（去重）"""
    existing_parts = set()
    existing_seasons = set()
    for r in user_entry.records:
        if r.plant_part:
            existing_parts.add(r.plant_part.value)
        if r.season:
            existing_seasons.add(r.season.value)
    existing_parts.add(plant_part)
    existing_seasons.add(season)
    user_entry.parts_collected = len(existing_parts)
    user_entry.seasons_collected = len(existing_seasons)


def _create_collection_record(
    session, user_entry: UserEncyclopediaEntry,
    user_id: str, species_id: int,
    plant_part: str, season: str, image_path: str, confidence: float,
):
    """写入一条收集记录"""
    record = CollectionRecord(
        user_entry_id=user_entry.id,
        user_id=user_id,
        species_id=species_id,
        plant_part=PlantPart(plant_part) if plant_part else None,
        season=Season(season) if season else None,
        image_path=image_path,
        confidence=confidence,
    )
    session.add(record)


def _update_global_stats(session, ge: GlobalEncyclopediaEntry, user_id: str) -> GlobalEncyclopediaEntry:
    """更新全局条目统计信息"""
    ge.total_discoveries = (ge.total_discoveries or 0) + 1

    unique_users = session.query(UserEncyclopediaEntry).filter(
        UserEncyclopediaEntry.global_entry_id == ge.id,
        UserEncyclopediaEntry.is_discovered == 1
    ).count()
    ge.unique_discoverers = unique_users

    if not ge.first_discovered_at:
        ge.first_discovered_at = datetime.utcnow()
        ge.first_discovered_by = user_id

    return ge


# ════════════════════════════════════════════════════════════════
# 图鉴统计
# ════════════════════════════════════════════════════════════════

def get_user_encyclopedia_stats(user_id: str) -> dict:
    """获取用户个人图鉴统计"""
    session = get_session()
    try:
        total = session.query(UserEncyclopediaEntry).filter_by(
            user_id=user_id
        ).count()
        discovered = session.query(UserEncyclopediaEntry).filter_by(
            user_id=user_id, is_discovered=1
        ).count()
        recent = (
            session.query(UserEncyclopediaEntry)
            .filter_by(user_id=user_id, is_discovered=1)
            .order_by(UserEncyclopediaEntry.discovered_at.desc())
            .limit(5)
            .all()
        )
        total_global = session.query(Species).count()

        return {
            "user_id": user_id,
            "total_discoverable": total_global,
            "user_discovered": discovered,
            "user_total": total,
            "user_completion_pct": round(discovered / max(total_global, 1) * 100, 1),
            "recent_discoveries": [
                {
                    "species_id": e.species_id,
                    "scientific_name": e.species.scientific_name,
                    "chinese_name": e.species.chinese_name,
                    "completion": e.completion_pct,
                }
                for e in recent
            ],
        }
    finally:
        session.close()


def get_global_encyclopedia_stats() -> dict:
    """获取全球图鉴统计"""
    session = get_session()
    try:
        total_species = session.query(Species).count()
        total_discovered = session.query(GlobalEncyclopediaEntry).filter(
            GlobalEncyclopediaEntry.total_discoveries > 0
        ).count()
        recent = (
            session.query(GlobalEncyclopediaEntry)
            .filter(GlobalEncyclopediaEntry.total_discoveries > 0)
            .order_by(GlobalEncyclopediaEntry.first_discovered_at.desc())
            .limit(10)
            .all()
        )

        return {
            "total_species": total_species,
            "total_discovered": total_discovered,
            "completion_pct": round(total_discovered / max(total_species, 1) * 100, 1),
            "recent_discoveries": [
                {
                    "species_id": e.species_id,
                    "scientific_name": e.species.scientific_name,
                    "chinese_name": e.species.chinese_name,
                    "first_discovered_by": e.first_discovered_by,
                    "total_discoveries": e.total_discoveries,
                    "unique_discoverers": e.unique_discoverers,
                }
                for e in recent
            ],
        }
    finally:
        session.close()


# ════════════════════════════════════════════════════════════════
# 物种详情
# ════════════════════════════════════════════════════════════════

def get_species_detail(species_id: int, user_id: Optional[str] = None) -> dict:
    """获取物种详情，可选附带用户收集数据"""
    session = get_session()
    try:
        species = session.query(Species).filter_by(id=species_id).first()
        if not species:
            return {"error": "物种不存在"}

        # 获取完整分类
        genus = species.genus
        family = genus.family
        order = family.order
        class_obj = order.class_
        phylum = class_obj.phylum
        kingdom = phylum.kingdom

        # 全球数据
        ge = species.global_entry
        global_collection = {
            "is_discovered": bool(ge and ge.total_discoveries > 0),
            "total_discoveries": ge.total_discoveries if ge else 0,
            "unique_discoverers": ge.unique_discoverers if ge else 0,
            "first_discovered_by": ge.first_discovered_by if ge else None,
            "first_discovered_at": ge.first_discovered_at.isoformat() if ge and ge.first_discovered_at else None,
        } if ge else None

        # 用户数据
        user_collection = None
        if user_id:
            ue = session.query(UserEncyclopediaEntry).filter_by(
                user_id=user_id, species_id=species_id
            ).first()
            if ue:
                records = [
                    {
                        "id": r.id,
                        "plant_part": r.plant_part.value if r.plant_part else None,
                        "season": r.season.value if r.season else None,
                        "confidence": r.confidence,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in ue.records
                ]
                user_collection = {
                    "is_discovered": bool(ue.is_discovered),
                    "discovered_at": ue.discovered_at.isoformat() if ue.discovered_at else None,
                    "discovery_count": ue.discovery_count,
                    "completion_pct": ue.completion_pct,
                    "parts_collected": ue.parts_collected,
                    "seasons_collected": ue.seasons_collected,
                    "records": records,
                }

        return {
            "species": {
                "id": species.id,
                "scientific_name": species.scientific_name,
                "chinese_name": species.chinese_name,
                "common_name": species.common_name,
                "kingdom": kingdom.name,
                "kingdom_cn": kingdom.chinese_name or kingdom.name,
                "phylum": phylum.name,
                "phylum_cn": phylum.chinese_name or phylum.name,
                "class_name": class_obj.name,
                "class_name_cn": class_obj.chinese_name or class_obj.name,
                "order": order.name,
                "order_cn": order.chinese_name or order.name,
                "family": family.name,
                "family_cn": family.chinese_name or family.name,
                "genus": genus.name,
                "genus_cn": genus.chinese_name or genus.name,
                "description": species.description,
                "habitat": species.habitat,
                "image_url": species.image_url,
                "image_attribution": species.image_attribution,
                "name_source": species.name_source,
                "desc_source": species.desc_source,
            },
            "global_collection": global_collection,
            "user_collection": user_collection,
        }
    finally:
        session.close()


def get_species_detail_by_name(scientific_name: str):
    """通过学名查找物种"""
    session = get_session()
    try:
        return session.query(Species).filter_by(
            scientific_name=scientific_name
        ).first()
    finally:
        session.close()
