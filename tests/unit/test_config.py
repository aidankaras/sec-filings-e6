import pytest
from pydantic import ValidationError

from arbiter.config import Settings

VALID = {
    "sec_user_agent": "test-user test@example.com",
    "database_url": "postgresql+psycopg://u:p@localhost:5432/db",
}


def test_accepts_a_wellformed_user_agent() -> None:
    assert Settings(**VALID).sec_user_agent == "test-user test@example.com"


@pytest.mark.parametrize(
    "bad",
    ["no-email-here", "test@example.com", "", "name name2"],
    ids=["missing-email", "missing-name", "empty", "no-at-sign"],
)
def test_rejects_user_agents_edgar_would_throttle(bad: str) -> None:
    with pytest.raises(ValidationError, match="SEC_USER_AGENT"):
        Settings(**{**VALID, "sec_user_agent": bad})


def test_rejects_a_live_broker_endpoint() -> None:
    """A live endpoint must fail at startup, not at order submission."""
    with pytest.raises(ValidationError, match="paper trading only"):
        Settings(**{**VALID, "alpaca_base_url": "https://api.alpaca.markets"})


def test_defaults_to_the_paper_endpoint() -> None:
    assert "paper-api" in Settings(**VALID).alpaca_base_url


def test_rejects_unknown_configuration_keys() -> None:
    """A typo in an environment variable must fail loudly, not be ignored."""
    with pytest.raises(ValidationError):
        Settings(**{**VALID, "spend_ceiling": "100"})


def test_secrets_are_not_exposed_in_the_repr() -> None:
    settings = Settings(**{**VALID, "anthropic_api_key": "sk-should-not-appear"})
    assert "sk-should-not-appear" not in repr(settings)


@pytest.mark.parametrize("blank", ["", "   "], ids=["empty", "whitespace"])
def test_a_blank_secret_reads_as_unset(blank: str) -> None:
    """`.env.example` ships `ALPACA_API_KEY=""`; that is a missing key, not a key."""
    settings = Settings(**{**VALID, "alpaca_api_key": blank, "alpaca_secret_key": blank})

    assert settings.alpaca_api_key is None
    assert settings.alpaca_secret_key is None


def test_a_set_secret_is_kept() -> None:
    settings = Settings(**{**VALID, "alpaca_api_key": "key-id"})

    assert settings.alpaca_api_key is not None
    assert settings.alpaca_api_key.get_secret_value() == "key-id"
