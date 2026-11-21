"""Where the local ledger finds its migrations, and what happens when it cannot."""

from pathlib import Path

import pytest

from arbiter.db import local


def test_a_source_checkout_finds_its_own_migrations():
    root = local.migrations_root()

    assert (root / "alembic.ini").is_file()
    assert (root / "migrations" / "versions").is_dir()


def test_an_install_without_migrations_says_so(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A non-editable install keeps the package under site-packages, away from them."""
    installed = tmp_path / "site-packages" / "arbiter" / "db" / "local.py"
    monkeypatch.setattr(local, "__file__", str(installed))
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="checkout of the repository"):
        local.migrations_root()
