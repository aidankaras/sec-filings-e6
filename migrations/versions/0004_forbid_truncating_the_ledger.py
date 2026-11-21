"""Forbid TRUNCATE on the append-only ledger tables.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-21

The guards from 0001 and 0003 fire on UPDATE and DELETE only. TRUNCATE does not
fire DELETE triggers, so `TRUNCATE predictions CASCADE` emptied the ledger
without tripping either. Postgres allows TRUNCATE triggers only at statement
level, which is the level the existing guards already use.
"""

from __future__ import annotations

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

_GUARDED_TABLES = ("predictions", "llm_calls", "agent_exclusions")


def upgrade() -> None:
    """Attach a TRUNCATE guard to each append-only table."""
    for table in _GUARDED_TABLES:
        op.execute(
            f"CREATE TRIGGER {table}_no_truncate "
            f"BEFORE TRUNCATE ON {table} "
            "FOR EACH STATEMENT EXECUTE FUNCTION arbiter_forbid_mutation();"
        )


def downgrade() -> None:
    """Remove the TRUNCATE guards."""
    for table in reversed(_GUARDED_TABLES):
        op.execute(f"DROP TRIGGER IF EXISTS {table}_no_truncate ON {table};")
