"""create devices table

Revision ID: b42ec0ca0000
Revises: 61c8ff25f2ab
Create Date: 2020-11-27 05:57:34.301453

"""
from typing import Tuple

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

revision = "b42ec0ca0000"
down_revision = "61c8ff25f2ab"
branch_labels = None  # type: ignore
depends_on = None  # type: ignore


def timestamps() -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def upgrade() -> None:
    op.create_table(
        "devices",
        sa.Column(
            "id",
            UUID,
            server_default=sa.text("uuid_generate_v4()"),
            primary_key=True,
        ),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column(
            "data",
            postgresql.JSONB(none_as_null=True),
            nullable=False,
        ),
        *timestamps(),
    )


def downgrade() -> None:
    op.drop_table("devices")
