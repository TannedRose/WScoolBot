"""update names

Revision ID: cd9ba4df1493
Revises: 9bea1782b488
Create Date: 2025-12-25 21:59:53.978231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd9ba4df1493'
down_revision: Union[str, Sequence[str], None] = '9bea1782b488'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('notifications', 'health')
    op.alter_column('profiles', 'qwery', new_column_name='query')



def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('health', 'notifications')
    op.alter_column('profiles', 'query', new_column_name='qwery')

    # ### end Alembic commands ###
