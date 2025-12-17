"""add is_locked and token_version to users

Revision ID: 94e8f151a3f9
Revises: ac99040b77e3
Create Date: 2025-12-17 23:05:26.203460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94e8f151a3f9'
down_revision = 'ac99040b77e3'
branch_labels = None
depends_on = None


def upgrade():
    # Emergency lock ve session invalidation için alanlar ekle
    op.add_column('users', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('users', sa.Column('token_version', sa.Integer(), nullable=False, server_default=sa.text('0')))


def downgrade():
    op.drop_column('users', 'token_version')
    op.drop_column('users', 'is_locked')
