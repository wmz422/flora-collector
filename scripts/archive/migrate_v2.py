"""
迁移脚本 v2：一次性事务，导入 51 种到新架构
"""
import sys, os, time, sqlite3
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ['FLORA_DB'] = os.path.join(os.path.dirname(__file__), '..', 'data', 'flora.db')

from src.flora_collector.models import (
    get_session, SessionLocal, engine, init_db,
    Kingdom, Phylum, Class, Order, Family, Genus,
    Species, GlobalEncyclopediaEntry, UserEncyclopediaEntry
)
from src.flora_collector.services.name_pipeline import resolve_name_and_description

# 连接旧备份
BAK_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'flora.db.bak')
if not os.path.exists(BAK_PATH):
    print("⚠ 备份不存在")
    sys.exit(1)

bak = sqlite3.connect(BAK_PATH)
old_rows = bak.execute('''
    SELECT id, scientific_name, chinese_name, common_name, 
           kingdom, phylum, class_name, "order", family, genus,
           description, habitat, image_url, inaturalist_taxon_id
    FROM species ORDER BY id
''').fetchall()
bak.close()

print(f"📖 读取 {len(old_rows)} 种")

# 用新 session
session = get_session()
try:
    # ── 辅助：获取或创建分类节点 ──
    def get_or_create(model, **kwargs):
        obj = session.query(model).filter_by(**kwargs).first()
        if not obj:
            obj = model(**kwargs)
            session.add(obj)
            session.flush()
        return obj

    imported = 0
    pipeline_cn = 0
    
    for i, (sid, sci_name, cn, common, kingdom, phylum_n, cls, ordr, fam, gen, desc, hab, img_url, inat_id) in enumerate(old_rows):
        if session.query(Species).filter_by(scientific_name=sci_name).first():
            print(f"  [{i+1}/{len(old_rows)}] ⏭ {sci_name} (已存在)")
            continue
        
        # 建分类链
        k = get_or_create(Kingdom, name=kingdom or "Plantae")
        p = get_or_create(Phylum, name=phylum_n or "Tracheophyta", kingdom_id=k.id)
        c = get_or_create(Class, name=cls or "Magnoliopsida", phylum_id=p.id)
        o = get_or_create(Order, name=ordr or f"(unplaced {fam or sci_name})", class_id=c.id)
        f = get_or_create(Family, name=fam or "(unknown family)", order_id=o.id)
        g = get_or_create(Genus, name=gen or sci_name.split()[0], family_id=f.id)
        
        # Pipeline 补中文名+描述
        name_source = ""
        desc_source = ""
        if not cn or not desc:
            nd = resolve_name_and_description(sci_name)
            time.sleep(0.3)
            if not cn:
                cn = nd.get("chinese_name", "") or ""
                name_source = nd.get("name_source", "") or ""
                if cn: pipeline_cn += 1
            if not desc:
                desc = nd.get("description", "") or ""
                desc_source = nd.get("desc_source", "") or ""
            if not img_url:
                img_url = nd.get("image_url", "") or ""
        
        sp = Species(
            scientific_name=sci_name,
            chinese_name=cn or "",
            common_name=common or "",
            genus_id=g.id,
            description=desc or "",
            habitat=hab or "",
            image_url=img_url or "",
            inaturalist_taxon_id=inat_id,
            name_source=name_source,
            desc_source=desc_source,
        )
        session.add(sp)
        session.flush()
        
        # 全球图鉴
        ge = GlobalEncyclopediaEntry(
            species_id=sp.id,
            first_discovered_by="system",
            first_discovered_at=datetime.utcnow(),
            total_discoveries=0,
            unique_discoverers=0,
        )
        session.add(ge)
        session.flush()
        
        # 如果有中文名 = 之前已发现，给 default 用户一条记录
        if cn:
            ue = UserEncyclopediaEntry(
                user_id="default",
                species_id=sp.id,
                global_entry_id=ge.id,
                is_discovered=1,
                discovered_at=datetime.utcnow(),
                discovery_count=1,
                parts_collected=1,
                seasons_collected=1,
            )
            session.add(ue)
            ge.total_discoveries = 1
            ge.unique_discoverers = 1
        
        imported += 1
        print(f"  [{i+1}/{len(old_rows)}] {'✅' if cn else '⛔'} {sci_name} → {fam}")

    session.commit()
    
    # 统计
    total_sp = session.query(Species).count()
    total_ge = session.query(GlobalEncyclopediaEntry).count()
    total_ue = session.query(UserEncyclopediaEntry).filter_by(user_id="default").count()
    disc_ue = session.query(UserEncyclopediaEntry).filter_by(user_id="default", is_discovered=1).count()
    k_cnt = session.query(Kingdom).count()
    p_cnt = session.query(Phylum).count()
    c_cnt = session.query(Class).count()
    o_cnt = session.query(Order).count()
    f_cnt = session.query(Family).count()
    g_cnt = session.query(Genus).count()
    
    print(f"\n{'='*40}")
    print(f"✅ 导入 {imported} 种 (pipeline 补名: {pipeline_cn})")
    print(f"\n📊 数据库:")
    print(f"  界×{k_cnt} 门×{p_cnt} 纲×{c_cnt} 目×{o_cnt} 科×{f_cnt} 属×{g_cnt}")
    print(f"  物种: {total_sp} | 全球图鉴: {total_ge} | 用户图鉴: {total_ue} (已发现: {disc_ue})")

except Exception as e:
    session.rollback()
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
