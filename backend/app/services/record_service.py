from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_compare_record import UserCompareRecord


async def get_compare_records(db: AsyncSession, user_id: int) -> list[dict]:
    result = await db.execute(
        select(UserCompareRecord)
        .where(UserCompareRecord.user_id == user_id)
        .order_by(UserCompareRecord.create_time.desc())
    )
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "search_source": r.search_source,
            "compare_type": r.compare_type,
            "create_time": r.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for r in records
    ]


async def delete_compare_record(db: AsyncSession, user_id: int, record_id: int) -> bool:
    result = await db.execute(
        delete(UserCompareRecord).where(
            UserCompareRecord.id == record_id,
            UserCompareRecord.user_id == user_id,
        )
    )
    await db.flush()
    return result.rowcount > 0
