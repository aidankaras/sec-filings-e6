from datetime import date, timedelta
from decimal import Decimal

import pytest

from arbiter.ingestion.market import (
    RecentSipWindowError,
    daily_bars,
    newest_permitted_end,
)

pytestmark = pytest.mark.integration

# A settled window, well clear of the feed's current-session restriction.
WINDOW_START = date(2026, 8, 3)
WINDOW_END = date(2026, 8, 28)
ISSUER = "MO"
BENCHMARK = "XLP"


def test_bars_are_returned_for_the_issuer_and_its_benchmark():
    bars = daily_bars([ISSUER, BENCHMARK], WINDOW_START, WINDOW_END, today=date.today())

    assert bars[ISSUER]
    assert bars[BENCHMARK]
    assert len(bars[ISSUER]) == len(bars[BENCHMARK])


def test_live_bars_carry_aware_timestamps_and_exact_prices():
    bars = daily_bars([ISSUER], WINDOW_START, WINDOW_END, today=date.today())

    first = bars[ISSUER][0]
    assert first.timestamp.tzinfo is not None
    assert isinstance(first.close, Decimal)
    assert first.high >= first.low


def test_bars_stay_within_the_requested_window():
    """A window that silently widened would pull prices from outside the event."""
    bars = daily_bars([ISSUER], WINDOW_START, WINDOW_END, today=date.today())

    dates = [bar.timestamp.date() for bar in bars[ISSUER]]
    assert min(dates) >= WINDOW_START
    assert max(dates) <= WINDOW_END


def test_a_window_covering_the_current_session_is_refused_before_the_request():
    """The feed would reject it remotely; this fails first, with a clear reason."""
    today = date.today()

    with pytest.raises(RecentSipWindowError, match="current session"):
        daily_bars([ISSUER], today - timedelta(days=5), today, today=today)


def test_the_newest_permitted_end_is_actually_served():
    """Pins the measured rule against the live service rather than a memory of it."""
    today = date.today()
    end = newest_permitted_end(today)

    bars = daily_bars([ISSUER], end - timedelta(days=10), end, today=today)

    assert bars[ISSUER]
