"""Add galaxy models

Revision ID: 3c829af9a4d8
Revises: 5eb6f4e8def2
Create Date: 2025-12-30 18:42:38.677858

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c829af9a4d8'
down_revision = '5eb6f4e8def2'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create galaxies first (depends on games)
    op.create_table('galaxies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('shape', sa.String(length=20), nullable=False),
    sa.Column('density', sa.String(length=20), nullable=False),
    sa.Column('star_count', sa.Integer(), nullable=False),
    sa.Column('width', sa.Float(), nullable=False),
    sa.Column('height', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('game_id')
    )

    # 2. Create stars (depends on galaxies)
    op.create_table('stars',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('galaxy_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('x', sa.Float(), nullable=False),
    sa.Column('y', sa.Float(), nullable=False),
    sa.Column('is_nova', sa.Boolean(), nullable=False),
    sa.Column('nova_turn', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['galaxy_id'], ['galaxies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # 3. Create planets (depends on stars and game_players)
    op.create_table('planets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('star_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('orbit_index', sa.Integer(), nullable=True),
    sa.Column('temperature', sa.Float(), nullable=False),
    sa.Column('gravity', sa.Float(), nullable=False),
    sa.Column('metal_reserves', sa.Integer(), nullable=False),
    sa.Column('metal_remaining', sa.Integer(), nullable=False),
    sa.Column('state', sa.String(length=20), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('population', sa.Integer(), nullable=False),
    sa.Column('max_population', sa.Integer(), nullable=False),
    sa.Column('current_temperature', sa.Float(), nullable=False),
    sa.Column('terraform_budget', sa.Integer(), nullable=True),
    sa.Column('mining_budget', sa.Integer(), nullable=True),
    sa.Column('is_home_planet', sa.Boolean(), nullable=True),
    sa.Column('colonized_at', sa.DateTime(), nullable=True),
    sa.Column('explored_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['game_players.id'], ),
    sa.ForeignKeyConstraint(['star_id'], ['stars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # 4. Add columns to game_players (home_planet_id depends on planets)
    with op.batch_alter_table('game_players', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ai_difficulty', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('is_ready', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('home_planet_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_game_players_home_planet', 'planets', ['home_planet_id'], ['id'])


def downgrade():
    with op.batch_alter_table('game_players', schema=None) as batch_op:
        batch_op.drop_constraint('fk_game_players_home_planet', type_='foreignkey')
        batch_op.drop_column('home_planet_id')
        batch_op.drop_column('is_ready')
        batch_op.drop_column('ai_difficulty')

    op.drop_table('planets')
    op.drop_table('stars')
    op.drop_table('galaxies')
