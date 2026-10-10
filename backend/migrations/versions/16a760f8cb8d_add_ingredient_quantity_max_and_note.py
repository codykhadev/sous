"""add ingredient quantity_max and note

Revision ID: 16a760f8cb8d
Revises: c34a83d638ee
Create Date: 2026-10-10 15:27:49.764945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '16a760f8cb8d'
down_revision: Union[str, Sequence[str], None] = 'c34a83d638ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('ingredients', sa.Column('quantity_max', sa.Float(), nullable=True))
    op.add_column('ingredients', sa.Column('note', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('ingredients', 'note')
    op.drop_column('ingredients', 'quantity_max')
