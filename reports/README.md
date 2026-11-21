# Results

Measurements committed as they are produced, so that what was claimed at a given
commit stays inspectable. `arbiter report` writes `baseline-<domain>.md` and
`.svg` in place, so a result recomputed against more data replaces the previous
one; earlier versions are in the git history of each file
(`git log -p reports/baseline-insider.md`). A result found to be wrong, rather
than superseded, is moved to `withdrawn/` with the reason.

## What is here now

`baseline-insider.md` — the baseline arm on insider transactions, generated
2026-10-12: an initial fit on 26 days between 2026-03-02 and 2026-06-12, then
every trading day from 2026-06-15 to 2026-09-09 (60 days) scored walk-forward. Mean
information coefficient +0.0285 (t = 1.52) over 60 scored days and 3,909
issuer-days, indistinguishable from zero; Brier skill -0.0015, indistinguishable
from forecasting a constant rate. One sample and one regime: a measurement of the
control, not a strategy. An earlier version of this file, computed 2026-10-01 on
every fourth trading day, gave +0.121 (t = 3.09) over 11 scored days; the fuller
sample did not bear it out.

`baseline-insider.svg` — the same evaluation drawn as a figure: the information
coefficient by scored day with its mean and two-standard-error band, and the
calibration bands against the diagonal. Written by `arbiter report` beside the
Markdown report, so the two cannot disagree.

`withdrawn/baseline-insider-2026-09-19.md` — **withdrawn; no figure in it should
be cited.** The event store it was computed from held duplicated rows, from two
separate causes. A filing's single qualifying transaction had been stored once
per line on its form, inflating events by a factor averaging 2.94 across days
and ranging from 2.34 to 4.59. Separately, one transaction filed by several
joint reporting owners was counted once per owner — an over-weighting that
tracked filer type, since funds and large holders file jointly while officers
file alone.

Both causes are fixed and pinned by contract tests over recorded filings. The
report is kept rather than deleted so that what was claimed at its commit stays
inspectable, which is the same reason results are committed at all. Before
its replacement was computed, a review of the evaluation found four further
defects, each fixed and tested first: a clustering feature that counted filings
accepted later the same day, a holding fraction miscomputed for purchases, no
embargo between fitted and scored outcome windows, and a fit that counted
transaction rows while scoring counted issuer-days.

`redflag-population.md` — why the red-flag domain has no baseline arm yet. The
screened population is 94% officer transitions, while the restatements and
auditor changes the literature associates with large abnormal returns are 1%
and 5.6% of it. The pipeline works for this domain; the population cannot
support the measurement.

## What is planned

A weekly research log covering events processed, per-arm performance, where the
arms disagreed and which was right, representative decisions with their
reasoning, merged changes with their benchmark deltas, and cost against budget.
That requires a scored run of the agent arm, the neural and arbiter arms, and the
shadow portfolios; only the agent arm's analyst is built, and it has no scored
run yet.

## How to read any figure here

Every number is generated from the stored event and label data by a command in
this repository, never transcribed by hand. Results that did not work are
reported alongside those that did — a null result measured correctly is the
expected outcome for most of what this project tests, and reporting only the
favourable ones would make the whole exercise unreadable.
