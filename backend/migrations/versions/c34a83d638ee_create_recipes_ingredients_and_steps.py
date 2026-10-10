"""create recipes, ingredients and steps

Revision ID: c34a83d638ee
Revises: 
Create Date: 2026-10-09 16:52:37.656789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c34a83d638ee'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('recipes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('source_type', sa.String(length=20), nullable=False),
    sa.Column('source_url', sa.Text(), nullable=True),
    sa.Column('image_url', sa.Text(), nullable=True),
    sa.Column('servings', sa.Integer(), nullable=True),
    sa.Column('total_minutes', sa.Integer(), nullable=True),
    sa.Column('tags', sa.ARRAY(sa.String(length=50)), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ingredients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('raw', sa.Text(), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=True),
    sa.Column('unit', sa.String(length=30), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ingredients_recipe_id'), 'ingredients', ['recipe_id'], unique=False)
    op.create_table('steps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_steps_recipe_id'), 'steps', ['recipe_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_steps_recipe_id'), table_name='steps')
    op.drop_table('steps')
    op.drop_index(op.f('ix_ingredients_recipe_id'), table_name='ingredients')
    op.drop_table('ingredients')
    op.drop_table('recipes')
