"""change knowledge embedding to 384

Revision ID: c2b4a9f1d6e8
Revises: a8f4c2d91b73
Create Date: 2026-06-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c2b4a9f1d6e8"
down_revision: Union[str, Sequence[str], None] = "a8f4c2d91b73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DELETE FROM knowledge")
    op.execute(
        """
        ALTER TABLE knowledge
        ALTER COLUMN embedding TYPE vector(384)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE knowledge
        ALTER COLUMN embedding TYPE vector(1536)
        USING embedding::vector(1536)
        """
    )
