"""add foreign key to post table

Revision ID: bff0f3ce0e40
Revises: ed39ad703209
Create Date: 2021-12-06 12:04:40.878806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bff0f3ce0e40'
down_revision = 'ed39ad703209'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("owner_id", sa.Integer, nullable=False))
    op.create_foreign_key("posts_users_fk", source_table="posts", referent_table="users", local_cols=['owner_id'], remote_cols=['id'], ondelete='CASCADE')

def downgrade():
    op.drop_constraint('posts_users_fk', table_name='posts')
    op.drop_column("posts", "owner_id")
    pass
