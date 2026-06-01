import logging
import time
import uuid

from fastapi import Request

logger = logging.getLogger("app.request")


async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        cost_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "request_failed method=%s path=%s cost_ms=%.2f request_id=%s",
            request.method,
            request.url.path,
            cost_ms,
            request_id,
        )
        raise

    cost_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request_done method=%s path=%s status=%s cost_ms=%.2f request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        cost_ms,
        request_id,
    )
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-ms"] = str(round(cost_ms, 2))
    return response
