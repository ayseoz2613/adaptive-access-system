"""add risk_reasons to login_attempts

Revision ID: ac99040b77e3
Revises: 9a01_add_mfa_otp_fields
Create Date: 2025-12-16 13:44:05.767171

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ac99040b77e3'
down_revision = '9a01_add_mfa_otp_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "login_attempts",
        sa.Column("risk_reasons", sa.Text(), nullable=True)
    )


def downgrade():
    op.drop_column("login_attempts", "risk_reasons")
