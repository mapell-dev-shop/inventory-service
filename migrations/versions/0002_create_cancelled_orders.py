"""create cancelled_orders

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cancelled_orders",
        sa.Column("order_id", sa.String(36), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("cancelled_orders")
