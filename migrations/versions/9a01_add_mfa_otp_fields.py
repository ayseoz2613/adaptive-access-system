"""add mfa otp fields

Revision ID: 9a01_add_mfa_otp_fields
Revises: 727e20610b00
Create Date: 2025-12-13
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "9a01_add_mfa_otp_fields"
down_revision = "727e20610b00"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("mfa_code_hash", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("mfa_expires_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("mfa_pending", sa.Boolean(), nullable=False, server_default=sa.text("0")))


def downgrade():
    op.drop_column("users", "mfa_pending")
    op.drop_column("users", "mfa_expires_at")
    op.drop_column("users", "mfa_code_hash")
