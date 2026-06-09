"""create contact_requests table

Revision ID: 20260608_0001
Revises:
Create Date: 2026-06-08 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260608_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contact_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contact_requests_email"), "contact_requests", ["email"], unique=False)
    op.create_index(op.f("ix_contact_requests_id"), "contact_requests", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_contact_requests_id"), table_name="contact_requests")
    op.drop_index(op.f("ix_contact_requests_email"), table_name="contact_requests")
    op.drop_table("contact_requests")
