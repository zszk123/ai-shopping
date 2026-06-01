from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Index, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Goods(Base):
    __tablename__ = "goods"
    __table_args__ = (
        Index("ux_goods_platform_url_hash", "platform", "goods_url_hash", unique=True),
        Index("ix_goods_platform_sale_status", "platform", "sale_status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="goods id")
    goods_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="goods name")
    brand: Mapped[str] = mapped_column(String(64), default="", comment="brand")
    model: Mapped[str] = mapped_column(String(128), default="", comment="model")
    spec_param: Mapped[str] = mapped_column(String(255), default="", comment="specification")
    platform: Mapped[str] = mapped_column(String(32), nullable=False, comment="platform")
    shop_name: Mapped[str] = mapped_column(String(128), default="", comment="shop name")
    original_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, comment="original price")
    real_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, comment="final price")
    coupon_desc: Mapped[str] = mapped_column(String(512), default="", comment="coupon description")
    goods_img: Mapped[str] = mapped_column(String(512), default="", comment="goods image url")
    goods_url: Mapped[str] = mapped_column(String(800), nullable=False, comment="source goods url")
    goods_url_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="", comment="sha256 of goods url")
    sales_num: Mapped[int] = mapped_column(Integer, default=0, comment="sales count")
    score: Mapped[Decimal] = mapped_column(Numeric(3, 1), default=0.0, comment="rating score")
    feature_content: Mapped[str] = mapped_column(Text, default="", comment="embedding feature text")
    sale_status: Mapped[int] = mapped_column(SmallInteger, default=1, comment="1 on sale, 0 off shelf")
    last_update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="last updated at")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="created at")
