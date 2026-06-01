from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, Index, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GoodsPriceHistory(Base):
    __tablename__ = "goods_price_history"
    __table_args__ = (Index("ux_goods_price_history_goods_date", "goods_id", "record_date", unique=True),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    goods_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="goods id", index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, comment="recorded price")
    record_date: Mapped[date] = mapped_column(Date, nullable=False, comment="record date")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="created at")
