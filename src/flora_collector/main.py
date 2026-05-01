"""
Flora Collector — FastAPI 应用入口
"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import IMAGES_DIR
from .models import init_db
from .api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title="Flora Collector",
    description="拍照识植物 · 植物图鉴收集系统",
    version="0.1.0",
)

# 注册路由（API 优先）
app.include_router(router)

# 静态目录
STATIC_DIR = Path(__file__).parent / "static"

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")


@app.get("/")
async def index():
    """前端主页"""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.on_event("startup")
async def startup():
    """启动时初始化数据库并自愈缺失数据"""
    logger.info("Initializing database...")
    init_db()

    # 自愈：自动补爬所有缺少描述的物种
    try:
        from .services.iplant import fetch_iplant_data
        from .models import get_session, Species

        session = get_session()
        no_desc = session.query(Species).filter(
            (Species.description == None) | (Species.description == '')
        ).all()

        if no_desc:
            logger.info(f"Found {len(no_desc)} species missing descriptions, auto-healing...")
            for s in no_desc:
                iplant = fetch_iplant_data(s.scientific_name)
                if iplant and iplant.get("description"):
                    s.description = iplant["description"]
                    s.desc_source = "iplant"
                    if iplant.get("chinese_name"):
                        s.chinese_name = iplant["chinese_name"]
                    session.flush()
                    logger.info(f"  Healed: {s.scientific_name} ({len(iplant['description'])} chars)")
            session.commit()
        session.close()
        logger.info("Self-healing complete!")
    except Exception as e:
        logger.warning(f"Self-healing skipped: {e}")

    logger.info("Flora Collector is ready!")
