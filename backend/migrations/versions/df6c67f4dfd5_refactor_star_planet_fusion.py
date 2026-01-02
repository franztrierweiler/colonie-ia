"""refactor_star_planet_fusion

Revision ID: df6c67f4dfd5
Revises: bb7d803a9b19
Create Date: 2025-12-31 09:48:43.363507

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'df6c67f4dfd5'
down_revision = 'bb7d803a9b19'
branch_labels = None
depends_on = None


def upgrade():
    # 1. First, drop foreign keys that reference stars table
    with op.batch_alter_table('planets', schema=None) as batch_op:
        batch_op.drop_constraint('planets_star_id_fkey', type_='foreignkey')
    
    with op.batch_alter_table('fleets', schema=None) as batch_op:
        batch_op.drop_constraint('fleets_current_star_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('fleets_destination_star_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('fleets_orbiting_planet_id_fkey', type_='foreignkey')
    
    # 2. Now we can safely drop the stars table
    op.drop_table('stars')
    
    # 3. Modify fleets table
    with op.batch_alter_table('fleets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current_planet_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('destination_planet_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'planets', ['current_planet_id'], ['id'])
        batch_op.create_foreign_key(None, 'planets', ['destination_planet_id'], ['id'])
        batch_op.drop_column('current_star_id')
        batch_op.drop_column('orbiting_planet_id')
        batch_op.drop_column('destination_star_id')

    # 4. Modify galaxies table
    with op.batch_alter_table('galaxies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('planet_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.drop_column('star_count')

    # 5. Modify planets table - add new columns and foreign key
    with op.batch_alter_table('planets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('galaxy_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('x', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('y', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('is_nova', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('nova_turn', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key(None, 'galaxies', ['galaxy_id'], ['id'])
        batch_op.drop_column('orbit_index')
        batch_op.drop_column('star_id')


def downgrade():
    # Reverse operations (simplified - data would be lost)
    with op.batch_alter_table('planets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('star_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('orbit_index', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('created_at')
        batch_op.drop_column('nova_turn')
        batch_op.drop_column('is_nova')
        batch_op.drop_column('y')
        batch_op.drop_column('x')
        batch_op.drop_column('galaxy_id')

    with op.batch_alter_table('galaxies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('star_count', sa.INTEGER(), autoincrement=False, nullable=False, server_default='0'))
        batch_op.drop_column('planet_count')

    with op.batch_alter_table('fleets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('destination_star_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('orbiting_planet_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('current_star_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('destination_planet_id')
        batch_op.drop_column('current_planet_id')

    op.create_table('stars',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('galaxy_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column('x', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
        sa.Column('y', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
        sa.Column('is_nova', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column('nova_turn', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['galaxy_id'], ['galaxies.id'], name='stars_galaxy_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='stars_pkey')
    )

    with op.batch_alter_table('planets', schema=None) as batch_op:
        batch_op.create_foreign_key('planets_star_id_fkey', 'stars', ['star_id'], ['id'])

    with op.batch_alter_table('fleets', schema=None) as batch_op:
        batch_op.create_foreign_key('fleets_orbiting_planet_id_fkey', 'planets', ['orbiting_planet_id'], ['id'])
        batch_op.create_foreign_key('fleets_destination_star_id_fkey', 'stars', ['destination_star_id'], ['id'])
        batch_op.create_foreign_key('fleets_current_star_id_fkey', 'stars', ['current_star_id'], ['id'])
