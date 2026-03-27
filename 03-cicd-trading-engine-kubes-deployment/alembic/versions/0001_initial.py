"""create trading_signals table

Revision ID: 0001_initial
Revises:
Create Date: 2024-11-15 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trading_signals",
        sa.Column("id",               sa.Integer(),    primary_key=True, index=True),
        sa.Column("ticker",           sa.String(20),   nullable=False),
        sa.Column("signal",           sa.String(20),   nullable=False),
        sa.Column("rsi",              sa.Float(),      nullable=True),
        sa.Column("macd",             sa.Float(),      nullable=True),
        sa.Column("macd_signal_line", sa.Float(),      nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_trading_signals_ticker",         "trading_signals", ["ticker"])
    op.create_index("ix_trading_signals_ticker_created", "trading_signals", ["ticker", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_trading_signals_ticker_created", table_name="trading_signals")
    op.drop_index("ix_trading_signals_ticker",         table_name="trading_signals")
    op.drop_table("trading_signals")
