"""Enable Gin Index

Revision ID: b63b5a489386
Revises: 
Create Date: 2025-07-22 16:23:39.547504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b63b5a489386'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")