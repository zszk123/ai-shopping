"""initial schema

Revision ID: 20260531_0001
Revises:
Create Date: 2026-05-31
"""
from alembic import op
import sqlalchemy as sa

revision = "20260531_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=11), nullable=True),
        sa.Column("avatar", sa.String(length=512), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=True),
        sa.Column("create_time", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("update_time", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "goods",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("goods_name", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=64), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("spec_param", sa.String(length=255), nullable=True),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("shop_name", sa.String(length=128), nullable=True),
        sa.Column("original_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("real_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("coupon_desc", sa.String(length=512), nullable=True),
        sa.Column("goods_img", sa.String(length=512), nullable=True),
        sa.Column("goods_url", sa.String(length=800), nullable=False),
        sa.Column("goods_url_hash", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("sales_num", sa.Integer(), nullable=True),
        sa.Column("score", sa.Numeric(3, 1), nullable=True),
        sa.Column("feature_content", sa.Text(), nullable=True),
        sa.Column("sale_status", sa.SmallInteger(), nullable=True),
        sa.Column("last_update_time", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("create_time", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ux_goods_platform_url_hash", "goods", ["platform", "goods_url_hash"], unique=True)
    op.create_index("ix_goods_platform_sale_status", "goods", ["platform", "sale_status"])
    op.create_table(
        "goods_price_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("goods_id", sa.BigInteger(), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("create_time", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_goods_price_history_goods_id", "goods_price_history", ["goods_id"])
    op.create_index(
        "ux_goods_price_history_goods_date",
        "goods_price_history",
        ["goods_id", "record_date"],
        unique=True,
    )
    op.create_table(
        "user_compare_record",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("search_source", sa.String(length=1000), nullable=False),
        sa.Column("compare_type", sa.SmallInteger(), nullable=False),
        sa.Column("create_time", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_compare_record_user_id", "user_compare_record", ["user_id"])
    op.create_index("ix_user_compare_record_user_time", "user_compare_record", ["user_id", "create_time"])
    op.create_index("ux_user_phone", "user", ["phone"], unique=True)


def downgrade() -> None:
    op.drop_index("ux_user_phone", table_name="user")
    op.drop_index("ix_user_compare_record_user_time", table_name="user_compare_record")
    op.drop_index("ix_user_compare_record_user_id", table_name="user_compare_record")
    op.drop_table("user_compare_record")
    op.drop_index("ux_goods_price_history_goods_date", table_name="goods_price_history")
    op.drop_index("ix_goods_price_history_goods_id", table_name="goods_price_history")
    op.drop_table("goods_price_history")
    op.drop_index("ix_goods_platform_sale_status", table_name="goods")
    op.drop_index("ux_goods_platform_url_hash", table_name="goods")
    op.drop_table("goods")
    op.drop_table("user")
