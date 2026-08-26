"""initial

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')

    # Create tables
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('cameras',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location', Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('zone', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('detections',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('plate_number', sa.String(), nullable=False),
        sa.Column('camera_id', sa.UUID(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('vehicle_type', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('detections')
    op.drop_table('cameras')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS postgis;')
