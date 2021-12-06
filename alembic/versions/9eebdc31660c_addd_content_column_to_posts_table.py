"""addd content column to posts table

Revision ID: 9eebdc31660c
Revises: 1801a5dcdb01
Create Date: 2021-12-06 11:33:31.335183

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9eebdc31660c'
down_revision = '1801a5dcdb01'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade():
    op.drop_column("posts", "content")
    pass
