"""
Flora Collector — 核心数据模型 v2

    架构重构：界门纲目科属独立建表，Species 关联 Genus
    双图鉴系统：GlobalEncyclopedia（全物种）+ UserEncyclopedia（个人收集）
"""

import hashlib
import os
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    ForeignKey, Enum as SAEnum, create_engine, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import enum

from .config import DATABASE_URL

Base = declarative_base()

# ════════════════════════════════════════════════════════════════
# Enums
# ════════════════════════════════════════════════════════════════

class PlantPart(str, enum.Enum):
    FLOWER = "flower"
    LEAF = "leaf"
    FRUIT = "fruit"
    STEM = "stem"
    BARK = "bark"
    ROOT = "root"
    WHOLE = "whole"
    OTHER = "other"

class Season(str, enum.Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    YEAR_ROUND = "year_round"


# ════════════════════════════════════════════════════════════════
# 分类学骨架 — 界门纲目科属
# ════════════════════════════════════════════════════════════════

class Kingdom(Base):
    """界"""
    __tablename__ = "kingdoms"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    chinese_name = Column(String(100), default="")  # 中文名，如"植物界"
    phyla = relationship("Phylum", back_populates="kingdom", cascade="all, delete-orphan")

class Phylum(Base):
    """门"""
    __tablename__ = "phyla"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    chinese_name = Column(String(100), default="")  # 中文名，如"被子植物门"
    kingdom_id = Column(Integer, ForeignKey("kingdoms.id"), nullable=False)
    kingdom = relationship("Kingdom", back_populates="phyla")
    classes = relationship("Class", back_populates="phylum", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("name", "kingdom_id"),)

class Class(Base):
    """纲"""
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    chinese_name = Column(String(100), default="")  # 中文名，如"木兰纲"
    phylum_id = Column(Integer, ForeignKey("phyla.id"), nullable=False)
    phylum = relationship("Phylum", back_populates="classes")
    orders = relationship("Order", back_populates="class_", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("name", "phylum_id"),)

class Order(Base):
    """目"""
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    chinese_name = Column(String(100), default="")  # 中文名，如"蔷薇目"
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    class_ = relationship("Class", back_populates="orders")
    families = relationship("Family", back_populates="order", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("name", "class_id"),)

class Family(Base):
    """科"""
    __tablename__ = "families"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    chinese_name = Column(String(100), default="")  # 中文名，如"蔷薇科"
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    order = relationship("Order", back_populates="families")
    genera = relationship("Genus", back_populates="family", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("name", "order_id"),)

class Genus(Base):
    """属"""
    __tablename__ = "genera"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    chinese_name = Column(String(100), default="")  # 中文名，如"蔷薇属"
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    family = relationship("Family", back_populates="genera")
    species_list = relationship("Species", back_populates="genus", cascade="all, delete-orphan")
    __table_args__ = (UniqueConstraint("name", "family_id"),)


# ════════════════════════════════════════════════════════════════
# 物种 — 关联到属
# ════════════════════════════════════════════════════════════════

class Species(Base):
    """物种 — 关联 Genus，不再存扁平分类字符串"""
    __tablename__ = "species"

    id = Column(Integer, primary_key=True)
    scientific_name = Column(String(255), unique=True, nullable=False, index=True)
    chinese_name = Column(String(255))
    common_name = Column(String(255))

    # 关联到属
    genus_id = Column(Integer, ForeignKey("genera.id"), nullable=False)
    genus = relationship("Genus", back_populates="species_list")

    # 描述
    description = Column(Text)
    habitat = Column(Text)
    uses = Column(Text)
    warning = Column(Text)

    # 外部引用
    inaturalist_taxon_id = Column(Integer)
    image_url = Column(String(500))
    image_attribution = Column(String(500))  # 图片来源署名

    # 数据来源元信息
    name_source = Column(String(50), default="")      # chinese_name 来源（inat/wiki/llm）
    desc_source = Column(String(50), default="")      # description 来源（inat/wiki/llm）

    # 关联
    global_entry = relationship("GlobalEncyclopediaEntry", back_populates="species", uselist=False)
    images = relationship("PlantImage", back_populates="species")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Species {self.scientific_name} ({self.chinese_name or '?'})>"


class PlantImage(Base):
    """植物图片"""
    __tablename__ = "plant_images"
    id = Column(Integer, primary_key=True)
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    plant_part = Column(SAEnum(PlantPart), default=PlantPart.WHOLE)
    season = Column(SAEnum(Season), default=Season.YEAR_ROUND)
    description = Column(String(500))
    source = Column(String(100))

    species = relationship("Species", back_populates="images")


# ════════════════════════════════════════════════════════════════
# 双图鉴系统
# ════════════════════════════════════════════════════════════════

class GlobalEncyclopediaEntry(Base):
    """全球图鉴 — 每个物种一条，记录全局收集数据"""
    __tablename__ = "global_encyclopedia"

    id = Column(Integer, primary_key=True)
    species_id = Column(Integer, ForeignKey("species.id"), unique=True, nullable=False)

    # 全局统计
    total_discoveries = Column(Integer, default=0)     # 所有用户的发现次数
    unique_discoverers = Column(Integer, default=0)    # 发现过该物种的用户数
    first_discovered_at = Column(DateTime)             # 首次被发现的时刻
    first_discovered_by = Column(String(100))          # 首个发现者

    species = relationship("Species", back_populates="global_entry")
    user_entries = relationship("UserEncyclopediaEntry", back_populates="global_entry")


class UserEncyclopediaEntry(Base):
    """用户图鉴 — 每个用户每种物种一条"""
    __tablename__ = "user_encyclopedia"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    global_entry_id = Column(Integer, ForeignKey("global_encyclopedia.id"), nullable=False)

    # 用户收集进度
    is_discovered = Column(Integer, default=0)
    discovered_at = Column(DateTime)
    discovery_count = Column(Integer, default=0)

    # 多器官/多季节收集
    parts_collected = Column(Integer, default=0)
    total_parts = Column(Integer, default=1)
    seasons_collected = Column(Integer, default=0)
    total_seasons = Column(Integer, default=1)

    species = relationship("Species")
    global_entry = relationship("GlobalEncyclopediaEntry", back_populates="user_entries")
    records = relationship("CollectionRecord", back_populates="user_entry")

    __table_args__ = (UniqueConstraint("user_id", "species_id"),)

    @property
    def completion_pct(self) -> float:
        if self.total_parts + self.total_seasons == 0:
            return 0.0
        part_ratio = min(self.parts_collected / max(self.total_parts, 1), 1.0)
        season_ratio = min(self.seasons_collected / max(self.total_seasons, 1), 1.0)
        return round((part_ratio * 0.5 + season_ratio * 0.5) * 100, 1)


class CollectionRecord(Base):
    """收集记录 — 每次识别的日志"""
    __tablename__ = "collection_records"

    id = Column(Integer, primary_key=True)
    user_entry_id = Column(Integer, ForeignKey("user_encyclopedia.id"), nullable=False)
    user_id = Column(String(100), nullable=False, index=True)
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)

    plant_part = Column(SAEnum(PlantPart))
    season = Column(SAEnum(Season))
    image_path = Column(String(500))
    confidence = Column(Float)
    notes = Column(Text)

    user_entry = relationship("UserEncyclopediaEntry", back_populates="records")
    species = relationship("Species")

    created_at = Column(DateTime, default=datetime.utcnow)


# ════════════════════════════════════════════════════════════════
# Database Setup
# ════════════════════════════════════════════════════════════════

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """创建所有表"""
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
