"""add_combat_reports_table

Revision ID: e339cf9dadf4
Revises: 765d8d414750
Create Date: 2026-01-04 00:08:15.449565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e339cf9dadf4"
down_revision = "765d8d414750"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "combat_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("planet_id", sa.Integer(), nullable=False),
        sa.Column("turn", sa.Integer(), nullable=False),
        sa.Column("attacker_ids", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("defender_id", sa.Integer(), nullable=True),
        sa.Column("victor_id", sa.Integer(), nullable=True),
        sa.Column("is_draw", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("attacker_forces", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("defender_forces", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("attacker_losses", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("defender_losses", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("population_casualties", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_debris_metal", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metal_recovered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("planet_captured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("planet_colonized", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("new_owner_id", sa.Integer(), nullable=True),
        sa.Column("combat_log", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["planet_id"], ["planets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["defender_id"], ["game_players.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["victor_id"], ["game_players.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["new_owner_id"], ["game_players.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    # Index for querying combat reports by game and turn
    op.create_index("ix_combat_reports_game_turn", "combat_reports", ["game_id", "turn"])


def downgrade():
    op.drop_index("ix_combat_reports_game_turn", "combat_reports")
    op.drop_table("combat_reports")
