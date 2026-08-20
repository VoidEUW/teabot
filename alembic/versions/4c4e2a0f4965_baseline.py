"""Baseline migration.

Intentionally empty — there are no tables yet. This migration only
establishes the alembic_version row so that future migrations have a
known starting point and alembic check works correctly.

An empty upgrade()/downgrade() here is correct. When the first model
is added, autogenerate will produce a real migration.
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "4c4e2a0f4965"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
