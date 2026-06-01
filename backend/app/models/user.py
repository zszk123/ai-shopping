from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = (Index("ux_user_phone", "phone", unique=True),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="user id")
    username: Mapped[str] = mapped_column(String(32), nullable=False, comment="username")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="password hash")
    phone: Mapped[str] = mapped_column(String(11), default="", comment="phone number")
    avatar: Mapped[str] = mapped_column(String(512), default="", comment="avatar url")
    status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="1 active, 0 disabled")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="created at")
    update_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="updated at"
    )
