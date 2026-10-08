"""create inventory tables

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("sku", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
    )
    op.create_table(
        "reservations",
        sa.Column("order_id", sa.String(36), primary_key=True),
        sa.Column("sku", sa.String(50), primary_key=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
    )
    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.String(36), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("processed_events")
    op.drop_table("reservations")
    op.drop_table("products")
