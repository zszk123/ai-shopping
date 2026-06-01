import hashlib

from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.jwt_handler import create_token

_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def _verify_password(password: str, password_hash: str) -> bool:
    if len(password_hash) == 64 and password_hash == hashlib.sha256(password.encode()).hexdigest():
        return True
    try:
        return _pwd_context.verify(password, password_hash)
    except UnknownHashError:
        return False


async def register(db: AsyncSession, username: str, password: str, phone: str) -> dict:
    result = await db.execute(select(User).where(User.phone == phone))
    if result.scalar_one_or_none() is not None:
        return {"ok": False, "msg": "Phone number is already registered"}

    user = User(
        username=username,
        password=_hash_password(password),
        phone=phone,
    )
    db.add(user)
    await db.flush()

    token = create_token(user.id)
    return {"ok": True, "user_id": user.id, "token": token}


async def login(db: AsyncSession, phone: str, password: str) -> dict:
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if user is None:
        return {"ok": False, "msg": "Invalid phone number or password"}
    if not _verify_password(password, user.password):
        return {"ok": False, "msg": "Invalid phone number or password"}
    if user.status == 0:
        return {"ok": False, "msg": "Account is disabled"}

    token = create_token(user.id)
    return {"ok": True, "token": token, "user_id": user.id}


async def get_user_info(db: AsyncSession, user_id: int) -> dict | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    return {
        "id": user.id,
        "username": user.username,
        "phone": user.phone,
        "avatar": user.avatar,
        "status": user.status,
        "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S"),
    }


async def update_user(db: AsyncSession, user_id: int, username: str | None, avatar: str | None) -> bool:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return False
    if username is not None:
        user.username = username
    if avatar is not None:
        user.avatar = avatar
    return True
