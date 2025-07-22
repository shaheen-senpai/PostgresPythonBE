"""Enable Gin Index

Revision ID: e54e49d83841
Revises: 
Create Date: 2025-07-22 16:19:11.470363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e54e49d83841'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
