"""add_progressive_lock_and_mfa_fields

Revision ID: 727e20610b00
Revises: 755e023b7f19
Create Date: 2025-12-03 22:58:34.851763

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '727e20610b00'
down_revision = '755e023b7f19'
branch_labels = None
depends_on = None


def upgrade():
    # Progressive lock ve MFA için yeni alanlar ekle
    op.add_column('users', sa.Column('locked_until', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_ip', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('last_device_info', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('require_mfa', sa.Boolean(), nullable=True, server_default='0'))


def downgrade():
    # Eklenen alanları kaldır
    op.drop_column('users', 'require_mfa')
    op.drop_column('users', 'last_device_info')
    op.drop_column('users', 'last_ip')
    op.drop_column('users', 'locked_until')
