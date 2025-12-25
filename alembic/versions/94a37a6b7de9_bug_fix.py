"""fix sequence ownership

Revision ID: 123456789abc
Revises: 94a37a6b7de9
Create Date: 2025-12-25 22:40:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '123456789abc'
down_revision: Union[str, Sequence[str], None] = 'cd9ba4df1493'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Перепривязываем последовательность к правильной колонке
    op.execute("ALTER SEQUENCE notifications_id_seq OWNED BY health.id")


def downgrade() -> None:
    # Возвращаем обратно на health.id (если нужно откатить)
    op.execute("ALTER SEQUENCE notifications_id_seq OWNED BY notifications.id")
