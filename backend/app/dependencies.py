from fastapi import Header, HTTPException, Request

from app.config import settings
from app.utils.jwt_handler import get_user_id_from_token
from app.utils.redis_client import redis_client


async def get_current_user_id(authorization: str = Header(default=None, alias="Authorization")) -> int | None:
    if authorization is None:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    cache_key = f"token:{token}"
    cached_user_id = await redis_client.get(cache_key)
    if cached_user_id is not None:
        return int(cached_user_id)

    user_id = get_user_id_from_token(token)
    if user_id is None:
        return None

    await redis_client.set(cache_key, user_id, ttl=settings.JWT_CACHE_TTL)
    return user_id


async def require_user_id(authorization: str = Header(default=None, alias="Authorization")) -> int:
    user_id = await get_current_user_id(authorization)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Please login first")
    return user_id


async def require_internal_token(x_internal_token: str = Header(default="", alias="X-Internal-Token")) -> None:
    if not settings.INTERNAL_API_TOKEN:
        if settings.IS_PRODUCTION:
            raise HTTPException(status_code=500, detail="Internal token is not configured")
        return
    if x_internal_token != settings.INTERNAL_API_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")


async def login_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    cache_key = f"rate:login:{client_host}"
    try:
        count = await redis_client.client.incr(cache_key)
        if count == 1:
            await redis_client.client.expire(cache_key, settings.LOGIN_RATE_LIMIT_SECONDS)
        if count > settings.LOGIN_RATE_LIMIT_COUNT:
            raise HTTPException(status_code=429, detail="Too many login attempts")
    except HTTPException:
        raise
    except Exception:
        return
