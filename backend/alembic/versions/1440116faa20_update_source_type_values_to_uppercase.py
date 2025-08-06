"""update_source_type_values_to_uppercase

Revision ID: 1440116faa20
Revises: 9f7ffa4a5c45
Create Date: 2025-08-06 11:02:09.584507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1440116faa20'
down_revision: Union[str, None] = '9f7ffa4a5c45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
