"""Commands fail on missing configuration before doing any work, legibly.

Each test runs in an empty directory, so no `.env` is read, and sets the
environment itself.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from arbiter import cli
from arbiter.cli import app
from arbiter.config import get_settings

runner = CliRunner()

AGENT = "test-user test@example.com"


@pytest.fixture(autouse=True)
def _clean_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.chdir(tmp_path)
    for name in ("SEC_USER_AGENT", "ALPACA_API_KEY", "ALPACA_SECRET_KEY"):
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _must_not_run(*_: object, **__: object) -> object:
    raise AssertionError("work started despite missing configuration")


def test_ingest_without_a_user_agent_names_the_variable_instead_of_a_traceback(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(cli, "ingest_day", _must_not_run)

    result = runner.invoke(app, ["ingest", "2026-08-03"])

    assert result.exit_code == 1
    assert "SEC_USER_AGENT" in result.output
    assert "Traceback" not in result.output


def test_backfill_with_blank_market_keys_stops_before_ingesting(
    monkeypatch: pytest.MonkeyPatch,
):
    """The `.env.example` values: present in the file, empty in substance."""
    monkeypatch.setenv("SEC_USER_AGENT", AGENT)
    monkeypatch.setenv("ALPACA_API_KEY", "")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "")
    monkeypatch.setattr(cli, "ingest_and_resolve", _must_not_run)

    result = runner.invoke(app, ["backfill", "2026-08-03", "2026-08-07"])

    assert result.exit_code == 1
    assert "ALPACA_API_KEY and ALPACA_SECRET_KEY" in result.output


def test_check_reports_missing_market_keys(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SEC_USER_AGENT", AGENT)
    monkeypatch.setenv("ALPACA_API_KEY", "")

    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0
    assert "market data:   not configured (ALPACA_API_KEY, ALPACA_SECRET_KEY)" in result.output


def test_check_reports_market_keys_once_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SEC_USER_AGENT", AGENT)
    monkeypatch.setenv("ALPACA_API_KEY", "id")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "secret")

    result = runner.invoke(app, ["check"])

    assert "market data:   keys set" in result.output
