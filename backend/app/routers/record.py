from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_user_id
from app.services import record_service
from app.utils.response import fail, success

router = APIRouter(prefix="/api/record", tags=["record"])


@router.get("/list")
async def list_records(
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    records = await record_service.get_compare_records(db, user_id)
    return success(data=records)


@router.delete("/delete")
async def delete_record(
    record_id: int = Query(...),
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    ok = await record_service.delete_compare_record(db, user_id, record_id)
    if not ok:
        return fail(msg="Record not found", code=404)
    return success()
