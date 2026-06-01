import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db, ping_db
from app.exceptions import AppError, app_error_handler, unhandled_error_handler, validation_error_handler
from app.logging_config import configure_logging
from app.middleware import request_context_middleware
from app.routers import agent, compare, goods, internal, record, spider_control, user
from app.services.vector_service import init_milvus, ping_milvus
from app.utils.redis_client import redis_client

configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

_spider_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _spider_task
    await redis_client.connect()
    await init_db()
    try:
        await init_milvus()
    except Exception:
        logger.warning("Milvus connection failed, vector features will be unavailable", exc_info=True)

    if settings.SPIDER_AUTO_START:
        from app.spider.scheduler import start_scheduler

        _spider_task = asyncio.create_task(start_scheduler())
        logger.info("Spider scheduler started in background")

    yield

    if _spider_task:
        _spider_task.cancel()
    await redis_client.disconnect()
    await close_db()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.middleware("http")(request_context_middleware)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(agent.router)
app.include_router(compare.router)
app.include_router(record.router)
app.include_router(goods.router)
app.include_router(internal.router)
app.include_router(spider_control.router)


@app.get("/")
async def root():
    return {"code": 200, "msg": f"{settings.PROJECT_NAME} v{settings.VERSION}", "data": None}


@app.get("/healthz")
async def healthz():
    return {"code": 200, "msg": "ok", "data": {"status": "healthy"}}


@app.get("/readyz")
async def readyz():
    checks = {"database": False, "redis": False, "milvus": False}
    try:
        checks["database"] = await ping_db()
    except Exception:
        logger.exception("Database readiness check failed")
    try:
        checks["redis"] = await redis_client.ping()
    except Exception:
        logger.exception("Redis readiness check failed")
    try:
        checks["milvus"] = await ping_milvus()
    except Exception:
        logger.exception("Milvus readiness check failed")

    ready = all(checks.values())
    return {"code": 200 if ready else 503, "msg": "ready" if ready else "not ready", "data": checks}
