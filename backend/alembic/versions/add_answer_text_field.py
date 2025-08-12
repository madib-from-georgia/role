"""Add answer_text field to checklist_responses

Revision ID: add_answer_text_field
Revises: 8c15e2a3b4f6
Create Date: 2025-08-12 17:18:30.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_answer_text_field'
down_revision = '8c15e2a3b4f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add answer_text column to checklist_responses table
    op.add_column('checklist_responses', sa.Column('answer_text', sa.Text(), nullable=True))


def downgrade():
    # Remove answer_text column from checklist_responses table
    op.drop_column('checklist_responses', 'answer_text')