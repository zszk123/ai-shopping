from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import login_rate_limit, require_user_id
from app.schemas.user import UserLoginReq, UserRegisterReq, UserUpdateReq
from app.services import user_service
from app.utils.response import fail, success

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register", dependencies=[Depends(login_rate_limit)])
async def register(req: UserRegisterReq, db: AsyncSession = Depends(get_db)):
    result = await user_service.register(db, req.username, req.password, req.phone)
    if not result["ok"]:
        return fail(msg=result["msg"])
    return success(data={"token": result["token"], "user_id": result["user_id"]})


@router.post("/login", dependencies=[Depends(login_rate_limit)])
async def login(req: UserLoginReq, db: AsyncSession = Depends(get_db)):
    result = await user_service.login(db, req.phone, req.password)
    if not result["ok"]:
        return fail(msg=result["msg"])
    return success(data={"token": result["token"], "user_id": result["user_id"]})


@router.get("/info")
async def get_info(user_id: int = Depends(require_user_id), db: AsyncSession = Depends(get_db)):
    info = await user_service.get_user_info(db, user_id)
    if info is None:
        return fail(msg="User not found", code=404)
    return success(data=info)


@router.put("/update")
async def update_info(
    req: UserUpdateReq,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    ok = await user_service.update_user(db, user_id, req.username, req.avatar)
    if not ok:
        return fail(msg="User not found", code=404)
    return success()
