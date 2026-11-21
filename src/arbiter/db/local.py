"""A persistent embedded Postgres for running the ledger on one machine.

The ledger's guarantees — rows that cannot be edited, duplicate forecasts that
cannot be written — are enforced by Postgres triggers and constraints, so a
local run needs real Postgres, not a substitute engine. `pgserver` ships the
server as a Python package, which keeps the requirement to `uv sync --extra
ledger` on a machine without Docker.
"""

from __future__ import annotations

from pathlib import Path

#: Where `arbiter ledger-up` keeps the database files unless told otherwise.
DEFAULT_LEDGER_DIR = Path("data/ledger")


def ensure_local_ledger(data_dir: Path) -> str:
    """Start the ledger server for `data_dir`, or attach to it, and return its URL.

    The server outlives this process, and the URL is stable for a given
    directory. It does not survive a reboot: `ledger-up` and the agent commands
    start it again, and other commands that read `DATABASE_URL` do not.

    Raises:
        ModuleNotFoundError: the `ledger` extra is not installed.
    """
    from pgserver.postgres_server import get_server

    data_dir.mkdir(parents=True, exist_ok=True)
    server = get_server(data_dir, cleanup_mode=None)
    return server.get_uri().replace("postgresql://", "postgresql+psycopg://", 1)


def migrations_root() -> Path:
    """Return the directory holding `alembic.ini` and `migrations/`.

    The migrations are not part of the installed package, so they are found in
    the source checkout this module was imported from, or else in the working
    directory.

    Raises:
        FileNotFoundError: neither location holds them, as in a non-editable
            install such as the Docker image.
    """
    for candidate in (Path(__file__).resolve().parents[3], Path.cwd()):
        if (candidate / "alembic.ini").is_file() and (candidate / "migrations").is_dir():
            return candidate
    msg = (
        "alembic.ini and migrations/ were not found beside the package or in the "
        "working directory; run this from a checkout of the repository"
    )
    raise FileNotFoundError(msg)


def upgrade_to_head() -> None:
    """Apply every migration to the database the settings point at.

    Raises:
        FileNotFoundError: the migrations cannot be found (see `migrations_root`).
    """
    from alembic import command
    from alembic.config import Config

    root = migrations_root()
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    command.upgrade(config, "head")
