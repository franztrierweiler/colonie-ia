"""add_planet_history_fields

Revision ID: f74e57cc264d
Revises: df6c67f4dfd5
Create Date: 2025-12-31 14:07:58.125102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f74e57cc264d"
down_revision = "df6c67f4dfd5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("planets", sa.Column("history_line1", sa.String(200), nullable=True))
    op.add_column("planets", sa.Column("history_line2", sa.String(200), nullable=True))


def downgrade():
    op.drop_column("planets", "history_line2")
    op.drop_column("planets", "history_line1")
