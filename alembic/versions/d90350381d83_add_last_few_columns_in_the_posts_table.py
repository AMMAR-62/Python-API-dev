"""add last few columns in the posts table

Revision ID: d90350381d83
Revises: bff0f3ce0e40
Create Date: 2021-12-06 12:08:54.527595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd90350381d83'
down_revision = 'bff0f3ce0e40'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column(
        'published', sa.Boolean(), nullable=False, server_default='TRUE'),)
    op.add_column('posts', sa.Column(
        'created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),)

def downgrade():
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
