"""What a scored arm produced, in the shapes every report and comparison reads.

These types sit in `evaluation` rather than beside the baseline arm that first
produced them, so that the report, figure and breakdowns can read a result
without importing an arm, and so any arm can be scored into the same shapes.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import NamedTuple

from arbiter.evaluation.metrics import CalibrationBin, ICSummary


class IssuerScore(NamedTuple):
    """One issuer's scored day: what was forecast and what followed.

    The unit the information coefficient is computed over, kept with its issuer
    so a breakdown by an issuer attribute can regroup the same numbers.
    """

    cik: int
    forecast: float
    abnormal_return: float


@dataclass(frozen=True)
class DayOfEvents:
    """One day's events, their features, and the outcomes they resolved to."""

    day: date
    features: list[dict[str, float]]
    outcomes: list[int]
    returns: list[float]
    issuers: list[int]
    #: The session each event's outcome window closed on, from its stored label.
    #: Taken from the label rather than inferred from the filing day: a filing
    #: accepted late in a day, or a window crossing a gap in the price
    #: sessions, closes later than a calendar count from the partition day says.
    exit_sessions: list[date]
    #: Events filed that day that resolved to no outcome, every one of them
    #: recorded as an exclusion by the labeling pass.
    unlabelled: int = 0
    #: Each row's accession number: how a forecast stored per filing, such as
    #: the agent arm's, finds the rows it covers. Empty for days built in tests
    #: that do not need it.
    accessions: list[str] = field(default_factory=list[str])

    def __len__(self) -> int:
        return len(self.features)


@dataclass(frozen=True)
class Fold:
    """One refit and the block of days it forecast."""

    #: Days contributing at least one fitted event: those filed before the
    #: block whose outcome had closed by the block's first day. A day whose
    #: events closed at different sessions may be fitted in part.
    fit_days: list[date]
    scored_days: list[date]
    #: Share of fitted issuer-days that rose; the feasible reference for the
    #: block's Brier skill.
    fitted_base_rate: float
    train_events: int


@dataclass(frozen=True)
class Evaluation:
    """What an arm scored on days it was not fitted on."""

    ic: ICSummary
    daily_ic: dict[date, float]
    calibration: list[CalibrationBin]
    #: Against forecasting the base rate of the model that made each forecast:
    #: the constant a forecaster could have quoted before any scored outcome in
    #: that block was known.
    brier_skill: float
    #: Against forecasting the scored period's own rate, which was not knowable
    #: in advance — a stricter reference than any feasible constant.
    brier_skill_scored_rate: float
    #: The reference rate averaged over scored issuer-days: each fold's fitted
    #: up-rate, weighted by the issuer-days that fold scored. This is the mean of
    #: the per-observation references `brier_skill` is measured against.
    fitted_base_rate: float
    #: Share of scored issuer-days that rose.
    base_rate: float
    #: Days fitted on before the first forecast and never scored.
    initial_days: list[date]
    #: Every scored day, in order: all populated days after the initial window.
    test_days: list[date]
    folds: list[Fold]
    #: Events in the last fold's fitting set.
    train_events: int
    test_events: int
    #: Events on scored days dropped for want of an outcome, each recorded as
    #: an exclusion. Reported so the labelled share of the sample is visible.
    test_events_unlabelled: int
    #: Issuer-days on days that contributed a rank correlation: the sample the
    #: information coefficient rests on.
    test_issuer_days: int
    #: Every scored issuer-day, which calibration, Brier skill and the base
    #: rate are pooled over. Larger than `test_issuer_days` whenever a scored
    #: day had too few issuers to rank.
    pooled_issuer_days: int
    #: The last fold's model, which saw the most data. Earlier folds' weights
    #: are not kept; the report labels this table as the final refit's.
    coefficients: dict[str, float]
    #: Every scored day's issuers with the forecast and return the headline used
    #: for each, so a breakdown re-slices the identical numbers. Includes days
    #: too thin to contribute a coefficient.
    issuer_scores: dict[date, list[IssuerScore]] = field(
        default_factory=dict[date, list[IssuerScore]]
    )


def scores_by_issuer(forecasts: Sequence[float], day: DayOfEvents) -> list[IssuerScore]:
    """Collapse a day to one forecast and one outcome per issuer.

    Filings by several insiders at one company resolve to a single outcome, so
    the forecast for that issuer is the average of what was said about it.
    """
    grouped: dict[int, tuple[list[float], list[float]]] = {}
    for probability, realised, issuer in zip(forecasts, day.returns, day.issuers, strict=True):
        probabilities, returns = grouped.setdefault(issuer, ([], []))
        probabilities.append(probability)
        returns.append(realised)

    return [
        IssuerScore(
            issuer, sum(probabilities) / len(probabilities), sum(returns) / len(returns)
        )
        for issuer, (probabilities, returns) in grouped.items()
    ]
