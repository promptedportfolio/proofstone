# Proofstone

Brought to you by [The Prompted Portfolio](https://promptedportfolio.com).

Proofstone shows how much of a backtest's result is real, and how to combine several backtests into a portfolio within limits you set. You bring the return series, from any backtester or spreadsheet, and Proofstone reports:

- whether each backtest beats chance, given how many versions were tried to find it;
- the best mix of backtests for a return goal under a Sharpe floor or a drawdown cap, with the band of mixes that can't be told apart from the best;
- the history, and thousands of simulated futures, in a report you open in a browser.

A touchstone was the stone used to test gold by the streak it left, and the word now means the standard something is judged by. Proofstone is meant to be that standard for backtests.

## Status

**Planning. Nothing is built yet.** The repository is private. Version 1 will be free. This README is the working plan; the [open decisions](#open-decisions) at the end each have a proposed default.

## What it does

### Statistics for one backtest

| You provide | Proofstone reports |
|---|---|
| The return series, the number of versions tried, and an estimate of how much their Sharpe ratios varied | The probabilistic Sharpe ratio, the deflated Sharpe ratio, the minimum track record length, the Harvey-Liu haircut, and bootstrap confidence intervals |
| Every version's return series | All of the above, plus the probability of backtest overfitting (by combinatorially symmetric cross-validation), White's Reality Check or Hansen's SPA test, and an effective number of tries, since 500 near-identical versions count for less than 500 independent ones |

You can also cut a backtest's return by a set amount before anything else uses it, for a backtest that came from data mining.

### Portfolios of backtests

Proofstone treats each backtest's return series as an asset and solves for the weights within limits you set, such as weight bounds, long only, or a leverage cap. Two goals:

- **Maximize return with Sharpe ≥ X.** This is a convex problem: the Sharpe floor is a second-order cone constraint, so a solver finds the true optimum for any number of backtests. The floor applies to the deflated Sharpe ratio, not the raw one.
- **Maximize return with drawdown ≤ Y.** This isn't convex, because drawdown depends on the order of returns. A grid or random search handles a handful of backtests. For more, a limit on conditional drawdown at risk (CDaR, the average of the worst drawdowns) makes it a linear program.

Three things set it apart from existing optimizers:

1. **Drawdown limits apply to simulated drawdowns by default**, such as the 95th-percentile drawdown across resampled paths, with the historical maximum shown beside it. The historical maximum is a single sample: whichever crash happens to be in the data.
2. **The frontier is a band, not a line.** An optimizer piles weight on whichever backtest got luckiest. Re-running it on resampled histories shows the set of mixes that can't be told apart from the best one.
3. **The optimization counts as more tries.** Choosing weights is itself a search, so the report says how much of the best mix's edge holds up when the weights are fit on one half of the history and tested on the other.

### History and Monte Carlo

- **History:** growth, drawdowns, rolling returns and Sharpe ratio, calendar returns, and the longest time under water.
- **Monte Carlo:** block bootstrap resampling, fan charts, the distribution of ending wealth and of drawdowns, and the chance of breaching a limit.

### The report

One self-contained HTML file that works offline and can be sent as a file. It has interactive charts (hover, toggles, and sliders over results computed in advance, such as frontiers at a grid of Sharpe floors and drawdown caps), light and dark themes, and prints to PDF.

## Principles

- **Local first, bring your own data.** Proofstone runs on your machine and ships no market data. Most free market data, such as Yahoo's and exchange and index providers' sites, is licensed for personal use only, and licenses to redistribute it cost far more. You supply series from your own sources, accounts, or other backtesters. Examples use simulated series and public-domain FRED series.
- **A calculator, not an adviser.** You supply the strategies and the limits. Proofstone ships no recommended funds, weights, or presets, doesn't ask about your finances, and isn't marketed as finding your best portfolio. The Advisers Act's definition of an adviser includes being paid, and ads, affiliate links, or a paid upgrade can count, so a securities lawyer reviews the line before any paid version.
- **Adjusted beside unadjusted.** Every adjusted figure is shown next to the raw one, and "doesn't beat chance" is a normal result.
- **Nothing private comes in.** No data, results, or account details from the owner's private research enter this repository. Code from that research is rewritten for general inputs, not copied with its assumptions.

## Architecture

```text
CSV or Excel ──▶ engine ──────────▶ results.json ──▶ report renderer ──▶ report.html
(returns or      (statistics,        (versioned        (layout, charts,
 prices)          Monte Carlo,        schema)           themes)
                  optimizer)
```

- **Inputs:** return or price series in CSV or Excel files, daily or monthly, starting on different dates, and the risk-free rate from FRED.
- **Engine:** a Python library.
- **Results file:** JSON with a versioned schema, the only contract between the engine and the report. After the design phase, changes to the schema are additions only.
- **Report renderer:** builds the HTML from a results file alone, so the report can be designed and built before the engine exists.
- **Command line:** commands that write a report, for example `proofstone report` for one backtest and `proofstone frontier` for a portfolio of them.

Later shells over the same engine and report: `proofstone serve` on localhost for live re-optimization, a browser-only version, and a desktop app.

## Plan: design first

The report is built first, against made-up results, and the engine fills it in section by section. Design runs on the owner's fast review while the engine's code goes through the slower agent review.

### Phases

1. **Contract and sample data (days 1–2).** The results schema, and a throwaway script that writes sample results from simulated strategies. The samples are difficult on purpose: histories that start on different dates, one extreme month, a strategy that fails, long names, and both 2 and 12 strategies.
2. **Design rounds (days 2–5).** Two or three visual directions rendered from the samples. The owner picks one and refines it over 3 or 4 rounds. The mockups are thrown away afterward.
3. **Production report and a thin real slice (week 2).** The chosen design becomes the report's components. Beside it, the first slice runs end to end: CSV in, growth and drawdowns out, in the real report.
4. **Slices (weeks 3–4).** Each engine slice switches one report section from sample data to real results, in a report that already looks finished.

### Slices

Each slice is one pull request, or a few, lands with its tests, and leaves the report working.

| Slice | What it adds | Section it makes real | Depends on |
|---|---|---|---|
| S0 | Package skeleton, command line, automated checks | — | — |
| S1 | Results schema, version 1, and the sample-data script | All sections, on sample data | S0 |
| S2 | Design mockups, thrown away, not merged | — | S1 |
| S3 | The report's production components and themes | All sections, on sample data | S2 |
| S4 | Input: CSV and Excel files, aligning histories and frequencies, the risk-free rate | — | S0 |
| S5 | Core measures: growth, drawdowns, CAGR, volatility, Sharpe and Sortino ratios, time under water, rolling measures | History | S3, S4 |
| S6 | Sharpe statistics: probabilistic and deflated Sharpe ratios, minimum track record length, haircut, bootstrap intervals, each tested against published worked examples | Statistics | S5 |
| S7 | Monte Carlo: block bootstrap, fan charts, ending wealth, drawdown distribution | Monte Carlo | S5 |
| S8 | Frontier I: goals, limits, return cuts, the Sharpe-floor solver, the drawdown grid search, frontiers computed in advance over a grid of limits | Frontier | S5 |
| S9 | Frontier II: the resampled band, limits on simulated drawdowns, the half-and-half test | Frontier's band | S7, S8 |
| S10 | Overfitting tests from every version's series: probability of backtest overfitting, Reality Check or SPA, effective number of tries | Statistics' overfitting tests | S6 |
| S11 | CDaR optimizer for many backtests | Frontier, many backtests | S8 |
| S12 | Docs: a method write-up with citations, and examples on simulated and FRED data | — | S6–S9 |

The critical path is S0, S1, S2, S3, S5, S8, S9, then the release. S4, S6, S7, S10, S11 and S12 run beside it.

### Milestones and versions

| Milestone or version | Target | Done when |
|---|---|---|
| M1: design chosen | End of week 1 | Schema version 1 is merged, and the owner has chosen the design from mockups on sample data |
| 0.1.0: first real report | End of week 2 | A CSV of returns produces a finished-looking report; History is real, and the other sections still show sample data |
| 0.2.0: statistics and Monte Carlo | Week 3 | S6 and S7 are merged |
| 0.3.0: frontier | Week 3–4 | S8 and S9 are merged |
| 1.0.0: free public release | Weeks 3–4 | Every section is real, S10 to S12 are merged, the license is chosen, and the repository is public |
| 1.1.0: localhost | After 1.0.0, if early users ask | `proofstone serve` re-optimizes live as limits change |

A smaller 1.0.0, without S10 and S11 (grid search only, and statistics from the number of tries only), takes about 2 weeks.

Later, unscheduled:

- after-tax returns by tax bracket and account type;
- imports from other tools' exports, such as Portfolio Visualizer, QuantConnect, and broker statements;
- a browser-only version, served as a static site with the computation on the user's machine;
- a desktop app, only if installing becomes the main complaint;
- a paid layer, after a securities lawyer's review.

### Timeline

About 3 to 4 weeks to 1.0.0. Review rounds set the pace, not coding: about 8 slices are in sequence, and at two agent review rounds each that's about 16 rounds, or about 8 working days at half a day per round. Getting the statistics right (2 to 3 days) and the design rounds (3 to 5 days, overlapping other work) add the rest. A web app instead of a command-line tool would take 6 weeks or more.

### Process

- Production code goes through agent review. Design mockups are reviewed by the owner only, pending the owner's decision.
- Each statistic's expected numbers, taken from published worked examples, are written into the spec before its code, so review checks the code against fixed answers instead of re-deriving the math.
- Pull requests stay small, and slices that don't depend on each other are reviewed at the same time.

## Related tools

| Tool | What it does |
|---|---|
| [Assayon](https://strategy-platform-web.onrender.com/) | A free stock backtester that adjusts its t-statistic for the number of tries, counts every combination in a parameter sweep as a try, and requires a blind out-of-sample window |
| [BacktestProof](https://chromewebstore.google.com/detail/hnanggmnenahjfkobmfmjafimdenkicf) | A Chrome extension that scores exports from NinjaTrader, MetaTrader 5, and TradingView from 0 to 100, including for overfitting |
| Portfolio Visualizer, testfol.io | Portfolio backtests and optimizers, with licensed data |
| QuantConnect | A backtesting platform with licensed data |
| [Trial Folio](https://github.com/promptedportfolio/trialfolio) | This organization's tool for Portfolio123 research. Its roadmap plans descriptive return analytics (0.5.0), statistical evaluation (0.6.0), and grid search (0.7.0), and it doesn't import results produced elsewhere |

Neither Assayon nor BacktestProof appears to offer portfolios of backtests or Monte Carlo reports.

## Decisions

### Decided by owner

1. **The name: Proofstone** (2026-10-22). Chosen over Cupelwork and Luckproof. It was free on PyPI, and no company or product using it was found. A trademark search remains to be done.
2. **The repository: `promptedportfolio/proofstone`, private for now** (2026-10-22).
3. **Version 1 is free** (2026-10-22).

### Open decisions

1. **The form of version 1.** A command-line tool that writes a self-contained HTML report adds no time and is easy to share. A localhost app adds about a week and allows live re-optimization. A desktop app adds 2 weeks or more, plus code signing and testing on three platforms.
   **Proposed default:** the command-line tool and HTML report, with localhost in 1.1.0.
2. **The license.** Apache-2.0 keeps a later paid layer possible and includes a patent grant. MIT is the simplest. AGPL keeps hosted copies open. The Nathan Slaughter Personal Research License 1.1, which Trial Folio uses, is source-available rather than open source.
   **Proposed default:** Apache-2.0.
3. **The chart library, embedded so the report works offline.** Observable Plot is small, with handsome defaults that are easy to theme. Vega-Lite charts are JSON that Python can write directly. ECharts has polished interactions but a large file. Plotly looks generic and is about 3.5 MB.
   **Proposed default:** Observable Plot.
4. **Who reviews design mockups.** The mockups are thrown away, and the owner's eye is the right check for looks. Agent review would add rounds to the design phase.
   **Proposed default:** the owner only; agent review stays on production code.
5. **The relationship with Trial Folio's statistics.** Trial Folio's 0.5.0 to 0.7.0 plan descriptive analytics, the deflated Sharpe ratio, the probability of backtest overfitting, and grid search, which Proofstone's engine would also build. One shared library avoids building them twice, but it would have to meet Trial Folio's methods ADR and could slow Proofstone's 1.0.0.
   **Proposed default:** keep them separate for Proofstone's 1.0.0, and revisit when Trial Folio specifies 0.6.0.
6. **When the repository becomes public.**
   **Proposed default:** at 1.0.0.
