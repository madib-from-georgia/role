"""add_exercise_field_to_checklist_answers

Revision ID: 0cc3a9a04343
Revises: 1570f549c52f
Create Date: 2025-08-15 19:43:46.359552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cc3a9a04343'
down_revision: Union[str, None] = '1570f549c52f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поле exercise в таблицу checklist_answers
    op.add_column('checklist_answers', sa.Column('exercise', sa.Text(), nullable=True))


def downgrade() -> None:
    # Удаляем поле exercise из таблицы checklist_answers
    op.drop_column('checklist_answers', 'exercise')
