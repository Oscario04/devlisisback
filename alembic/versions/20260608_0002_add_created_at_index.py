"""add created_at index on contact_requests

Revision ID: 20260608_0002
Revises: 20260608_0001
Create Date: 2026-06-08 00:10:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260608_0002"
down_revision: Union[str, Sequence[str], None] = "20260608_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_contact_requests_created_at",
        "contact_requests",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_contact_requests_created_at", table_name="contact_requests")
