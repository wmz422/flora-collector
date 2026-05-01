"""
Flora Collector — 分类学骨架服务
管理界门纲目科属的自动创建和查询
"""
import logging
from typing import Optional, Dict, Any

from ..models import (
    Kingdom, Phylum, Class, Order, Family, Genus, Species,
    GlobalEncyclopediaEntry, UserEncyclopediaEntry,
    get_session
)
from .taxonomy_map import FAMILY_TO_ORDER, RANK_CHINESE, FAMILY_CHINESE, GENUS_CHINESE, GENUS_TO_BASIC

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════
# 分类链创建
# ════════════════════════════════════════════════════════════════

def ensure_taxonomy_chain(taxonomy: dict, session=None) -> Genus:
    """
    根据分类字典，自动创建/获取完整的分类链。
    返回 Genus 实例。

    如果传入了 session，使用该 session；否则自己创建。

    taxonomy: {
        "kingdom": "Plantae",
        "phylum": "Tracheophyta",
        "class_name": "Magnoliopsida",
        "order": "Rosales",
        "family": "Rosaceae",
        "genus": "Rosa",
    }
    """
    own_session = False
    if session is None:
        session = get_session()
        own_session = True

    try:
        def goc(model, **kwargs):
            obj = session.query(model).filter_by(**kwargs).first()
            if not obj:
                obj = model(**kwargs)
                session.add(obj)
                session.flush()
            return obj

        def _fill_cn(obj, mapping):
            """如果节点没有中文名，从标准映射表或 taxonomy dict 填入。
            优先级：标准映射表 → iPlant taxonomy dict
            """
            if obj.chinese_name:
                return
            # 先查标准映射表
            cn = mapping.get(obj.name, "")
            if cn:
                obj.chinese_name = cn
                session.flush()
                return
            # 映射表没有，再用 iPlant 的原始中文名
            class_to_key = {"Kingdom": "kingdom_cn", "Phylum": "phylum_cn",
                            "Class": "class_name_cn", "Order": "order_cn",
                            "Family": "family_cn", "Genus": "genus_cn"}
            rank_key = class_to_key.get(type(obj).__name__, "")
            if rank_key and taxonomy.get(rank_key):
                obj.chinese_name = taxonomy[rank_key]
                session.flush()

        kingdom_name = taxonomy.get("kingdom", "Plantae") or "Plantae"
        phylum_name = taxonomy.get("phylum", "") or "Tracheophyta"
        class_name = taxonomy.get("class_name", "") or "Magnoliopsida"
        order_name = taxonomy.get("order", "") or ""
        family_name = taxonomy.get("family", "") or ""
        genus_name = taxonomy.get("genus", "") or ""
        if not genus_name:
            sci = taxonomy.get("scientific_name", "")
            if sci:
                genus_name = sci.split()[0] if " " in sci else sci

        # 属→纲/门/界兜底（当 PlantNet 等来源未返回时）
        genus_fallback = GENUS_TO_BASIC.get(genus_name, {})
        if not taxonomy.get("class_name"):
            class_name = genus_fallback.get("class_name", class_name)
        if not taxonomy.get("phylum"):
            phylum_name = genus_fallback.get("phylum", phylum_name)
        if not taxonomy.get("kingdom"):
            kingdom_name = genus_fallback.get("kingdom", kingdom_name)

        # 如果目为空，尝试通过科名反查
        if not order_name and family_name:
            guessed = FAMILY_TO_ORDER.get(family_name, "")
            if guessed:
                order_name = guessed
                logger.info(f"Auto-resolved order for {family_name}: {order_name}")
            else:
                class_defaults = {
                    "Magnoliopsida": "Saxifragales",
                    "Liliopsida": "Poales",
                    "Pinopsida": "Pinales",
                    "Ginkgoopsida": "Ginkgoales",
                }
                order_name = class_defaults.get(class_name, "Saxifragales")
                logger.info(f"Default order for {class_name}/{family_name}: {order_name}")

        k = goc(Kingdom, name=kingdom_name)
        _fill_cn(k, RANK_CHINESE)
        p = goc(Phylum, name=phylum_name, kingdom_id=k.id)
        _fill_cn(p, RANK_CHINESE)
        c = goc(Class, name=class_name, phylum_id=p.id)
        _fill_cn(c, RANK_CHINESE)

        if not order_name:
            order_name = "Saxifragales"
        o = goc(Order, name=order_name, class_id=c.id)
        _fill_cn(o, RANK_CHINESE)

        if family_name:
            f = goc(Family, name=family_name, order_id=o.id)
        else:
            f = goc(Family, name=f"(unknown)", order_id=o.id)
        _fill_cn(f, FAMILY_CHINESE)

        if genus_name:
            g = goc(Genus, name=genus_name, family_id=f.id)
            _fill_cn(g, GENUS_CHINESE)
        else:
            raise ValueError(f"No genus provided in taxonomy: {taxonomy}")

        if own_session:
            session.commit()
        return g
    except Exception:
        if own_session:
            session.rollback()
        raise
    finally:
        if own_session:
            session.close()


# ════════════════════════════════════════════════════════════════
# 分类树构建
# ════════════════════════════════════════════════════════════════

# 分类树层级配置
# (rank_name, rank_label, child_attr, leaf_test)
# child_attr: lambda node: [children] — 获取子节点列表
# leaf_test: lambda node: True/False 或 None（表示非叶子）
_TREE_LEVELS = [
    ("kingdom", "界", lambda k: k.phyla, None),
    ("phylum", "门", lambda p: p.classes, None),
    ("class_name", "纲", lambda c: c.orders, None),
    ("order", "目", lambda o: o.families, None),
    ("family", "科", lambda f: f.genera, None),
    ("genus", "属", lambda g: g.species_list, None),
]


def get_species_taxonomy(species: Species, session=None) -> dict:
    """获取物种的完整分类链"""
    if session is None:
        from ..models import get_session as gs
        session = gs()
        try:
            return _do_get_taxonomy(species, session)
        finally:
            session.close()
    return _do_get_taxonomy(species, session)


def _do_get_taxonomy(species, session):
    genus = species.genus
    family = genus.family
    order = family.order
    class_obj = order.class_
    phylum = class_obj.phylum
    kingdom = phylum.kingdom
    return {
        "kingdom": kingdom.name,
        "phylum": phylum.name,
        "class_name": class_obj.name,
        "order": order.name,
        "family": family.name,
        "genus": genus.name,
    }


def build_taxonomy_tree(session=None, scope='world', user_id=None):
    """构建完整的分类树，含每层计数

    scope='world': 显示全球所有物种，未发现显示 ???
    scope='user':  只显示用户已发现的物种
    """
    own_session = False
    if session is None:
        session = get_session()
        own_session = True
    try:
        # 用户已发现物种 ID 集合
        user_species_ids = set()
        if user_id:
            rows = session.query(UserEncyclopediaEntry.species_id).filter_by(
                user_id=user_id, is_discovered=1
            ).all()
            user_species_ids = set(r[0] for r in rows)

        # 全球已发现物种 ID 集合（用于 user scope 的分母）
        global_species_ids = set()
        if scope == 'user':
            rows = session.query(GlobalEncyclopediaEntry.species_id).filter(
                GlobalEncyclopediaEntry.total_discoveries > 0
            ).all()
            global_species_ids = set(r[0] for r in rows)

        def build_node(node, level_idx: int):
            """递归构建分类树节点"""
            # Species 是叶子节点，特殊处理
            if level_idx >= len(_TREE_LEVELS):
                return _build_species_node(node, scope, user_species_ids, global_species_ids, session)

            rank, label, get_children, _ = _TREE_LEVELS[level_idx]
            children = [
                build_node(c, level_idx + 1)
                for c in get_children(node)
            ]
            # user scope: 过滤掉全球都没发现的分支
            if scope == 'user':
                children = [c for c in children if c]

            total = sum(n["total"] for n in children)
            disc = sum(n["discovered"] for n in children)

            return {
                "rank": rank,
                "rank_label": label,
                "name": node.name,
                "chinese_name": node.chinese_name or "",
                "total": total,
                "discovered": disc,
                "children": children,
            }

        kingdoms = session.query(Kingdom).order_by(Kingdom.name).all()
        tree = [build_node(k, 0) for k in kingdoms]
        if scope == 'user':
            tree = [t for t in tree if t["children"]]
        return tree

    finally:
        if own_session:
            session.close()


def _build_species_node(s, scope, user_species_ids, global_species_ids, session):
    """构建物种叶子节点"""
    ge = s.global_entry
    is_global = bool(ge and ge.total_discoveries > 0)

    if scope == 'user':
        # 我的图鉴：只展示全球已发现的物种（未发现显示 🔒 ???）
        if not is_global:
            return None
        is_disc = s.id in user_species_ids
    else:
        is_disc = is_global

    cp = 0
    if is_disc:
        ue = session.query(UserEncyclopediaEntry).filter_by(
            species_id=s.id, is_discovered=1
        ).first()
        if ue:
            cp = ue.completion_pct

    return {
        "id": s.id,
        "species_id": s.id,
        "rank": "species",
        "rank_label": "种",
        "name": s.chinese_name or "",
        "scientific_name": s.scientific_name,
        "is_discovered": is_disc,
        "total": 1,
        "discovered": 1 if is_disc else 0,
        "completion_pct": cp,
        "children": [],
    }


def get_global_stats(session=None):
    """获取全局统计"""
    own_session = False
    if session is None:
        session = get_session()
        own_session = True
    try:
        total_species = session.query(Species).count()
        total_discovered = session.query(GlobalEncyclopediaEntry).filter(
            GlobalEncyclopediaEntry.total_discoveries > 0
        ).count()
        return {
            "total_species": total_species,
            "total_discovered": total_discovered,
            "completion_pct": round(total_discovered / max(total_species, 1) * 100, 1),
        }
    finally:
        if own_session:
            session.close()
