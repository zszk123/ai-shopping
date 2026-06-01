from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserCompareRecord(Base):
    __tablename__ = "user_compare_record"
    __table_args__ = (Index("ix_user_compare_record_user_time", "user_id", "create_time"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="user id", index=True)
    search_source: Mapped[str] = mapped_column(String(1000), nullable=False, comment="source url/text/keyword")
    compare_type: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment="1 image, 2 url, 3 keyword")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="created at")
