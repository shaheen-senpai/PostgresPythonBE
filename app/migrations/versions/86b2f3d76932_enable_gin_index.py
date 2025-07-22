"""Enable Gin Index

Revision ID: 86b2f3d76932
Revises: 104ad2c3489a
Create Date: 2025-07-22 14:42:16.098118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86b2f3d76932'
down_revision = '104ad2c3489a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
