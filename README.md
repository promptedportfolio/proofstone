# Proofstone

Brought to you by [The Prompted Portfolio](https://promptedportfolio.com).

Proofstone builds and runs backtests from your own data, keeps a record of every study tried for each strategy, and shows how much of each result is real. It also shows how to combine several backtests into a portfolio within limits you set. You bring the data, or the return series from any backtester or spreadsheet, and Proofstone reports:

- each strategy's trades and returns: winners and losers, the average win and loss, and monthly returns on the capital at risk, on the sleeve and on the whole account;
- every study run for each strategy: the strategy at its best case, then each test, with its return, volatility, Sharpe ratio, worst drawdown, t-statistic, and the t-statistic it needs given how many tests were tried;
- whether each backtest beats chance, given how many versions were tried to find it;
- the best mix of backtests for a return goal under a Sharpe floor or a drawdown cap, with the band of mixes that can't be told apart from the best;
- the history, and thousands of simulated futures, in an app on your machine and in a report you open in a browser.

A touchstone was the stone used to test gold by the streak it left, and the word now means the standard something is judged by. Proofstone is meant to be that standard for backtests.

## Status

**Planning. Nothing is built yet.** The repository is public but not promoted. Version 1 will be free. This README is the working plan; the [open decisions](#open-decisions) at the end each have a proposed default.

On 2026-10-24 the owner widened the plan: Proofstone also becomes the backtesting tool for the owner's own strategy research. It adds the data catalog, the strategy engine, the study tracker, strategy reports and the screens that set up tests. Nothing was dropped from the earlier plan.

## What it does

### Data

You add the data, and Proofstone ships none (see [Principles](#principles)).

- **Series:** prices or returns of indexes, funds, rates and implied-volatility indexes, in CSV or Excel files, daily or monthly, starting on different dates, and the risk-free rate from FRED.
- **Option chains:** end-of-day or intraday quotes for every expiration and strike, with the bid, ask, last price, sizes, implied volatility and the underlying's price. They come from vendors' files or from recorded snapshots of delayed quotes. Import adapters turn each vendor's format into one chain store.
- **Runs from other tools:** return series, trades and the number of tries, from other backtesters.
- **The data catalog:** every file added gets a manifest entry with its source, when it was retrieved, its SHA-256, the dates it covers, and a note of the source's terms. A run records the entries it read, so each result can be traced to the exact files behind it, and a changed file is flagged instead of silently changing a result.

### Strategies

A strategy is a type with parameters, and the types take their parameters with no recommended values (open decision 10). Version 1's types cover every test in the owner's research:

| Type | What it does | Its parameters include |
|---|---|---|
| Hold | Holds a series | Costs, leverage and its financing rate |
| Timing rule | Holds a series while a signal is on, and something else, such as T-bills or a bond series, while it's off | The signal (for example the close against its moving average), its length, entry and exit bands, how many closes confirm a switch, switching costs, and volatility targeting |
| Option spreads | Sells put or call credit spreads on an index, or both as condors | The schedule (for example one rung a month, with a set number of rungs held), the days to expiration, the short strike by delta, moneyness or a minimum credit as a share of the width, the width, exits by time left, a profit target or a stop, entry filters such as an implied-volatility percentile window or a trend filter, and the amount at risk |
| Long options | Buys puts or calls, for example as a hedge | When to buy (for example when implied volatility is low against its past year), the strike and expiration, the budget, and when to sell (for example half on doubling and the rest at a set time left) |
| Sleeve from a series | Uses a return series as it stands: a fund, a simulation or a factor dataset | A return cut and a fee |
| Portfolio | Combines sleeves | Weights, rebalancing, where cash sits, margin and its rate, after-tax returns by tax bracket and account type, and the account's size, with options in whole contracts |

**Pricing options.** On days with a recorded chain, a trade fills at its quotes: the mid, or the mid less a set share of the half-spread. On days without one, a model prices it: Black-Scholes-Merton on a volatility surface built from implied-volatility indexes, with its skew, level and financing rate fitted to recorded chains. Each model is versioned, its fit error is measured on dates it wasn't fitted on, and every run records the model version it used.

**Sizing.** A position's size is a share of its sleeve at risk, or a number of contracts at a given account size. A sizing study finds the share of a sleeve to risk that maximizes long-run growth (Kelly sizing) with the edge discounted (below), and where growth stops rising.

### Discounts when a model is less certain

A run can carry a discount: a set cut to its return each year, or keeping only a share of its edge over the benchmark, such as three quarters, half or a quarter. A discount can belong to a model version (for example a pricing model with a large fit error), to a data source (for example a simulation designed on the same history), or to one run. Every discounted figure is shown beside the raw one, with which discount applied and why. This extends the return cut for data mining in [Statistics for one backtest](#statistics-for-one-backtest), which stays as it is.

### Studies and the tries behind them

The study tracker keeps every run, grouped by strategy:

- **Every run counts as a try,** including failed and abandoned ones, and a parameter sweep counts each combination. A run's settings, data manifest entries, model version and discount are stored with its results, and two runs can be compared by the settings that differ between them.
- **Planned experiments:** a baseline and its variants run under one approval and one budget of tries, and can be resumed safely after a stop.
- **Registration:** a study can be registered before it runs. Its specification is frozen with a hash, the run uses exactly that specification, and the decision is recorded beside the result. A registered study changed after its registration is shown as changed.
- **Forward records:** a strategy's out-of-sample record, from data added after its rules were fixed, such as recorded option chains or live returns, kept apart from the history it was designed on.
- **Decisions:** what became of each test, such as kept, dropped or kept as insurance, and when.

**The strategies page** shows each strategy at its best case (open decision 9), with its return, volatility, Sharpe ratio, worst drawdown, t-statistic, and the t-statistic required for the tests tried. **Each strategy's page** lists all of its tests with the same measures. The required t-statistic rises with the number of tests. At 5%, two-sided, with Bonferroni's correction:

| Tests tried | t-statistic required |
|---:|---:|
| 1 | 1.96 |
| 10 | 2.81 |
| 100 | 3.48 |
| 1,000 | 4.06 |

Which correction applies, and which tries count against a strategy, are open decisions 7 and 8.

### A strategy's report

For any run:

- **Trades:** the number of winners and losers, the average win and loss, the largest of each, the share that won, and how long trades were held.
- **Returns on three bases:** on the capital at risk (for a spread, its width less the credit), on the sleeve's total, and on the whole account. Each comes in monthly and yearly tables, beside a benchmark such as the S&P 500.
- **Risk statistics:** volatility, downside deviation, the worst drawdown and its length, time under water, the worst month and year, skew and tails, and named stress periods, slow declines as well as crashes.
- **Discounts** applied, beside the raw figures.
- The sections in [History and Monte Carlo](#history-and-monte-carlo) and [Statistics for one backtest](#statistics-for-one-backtest).

### Comparing a rule with its baseline

For a rule added to a strategy, such as a timing filter or an exit, Proofstone tests the difference it makes:

- a paired block bootstrap of the difference in Sharpe ratio and in worst decline;
- a Newey-West t-statistic of the difference in returns;
- a sign test across the separate episodes where the rule acts, with how many of them carry the result;
- the difference in each named stress period;
- robustness: the result across neighboring parameter values, and across every start day instead of one schedule.

### Statistics for one backtest

| You provide | Proofstone reports |
|---|---|
| The return series, the number of versions tried, and an estimate of how much their Sharpe ratios varied | The probabilistic Sharpe ratio, the deflated Sharpe ratio, the minimum track record length, the Harvey-Liu haircut, and bootstrap confidence intervals |
| Every version's return series | All of the above, plus the probability of backtest overfitting (by combinatorially symmetric cross-validation), White's Reality Check or Hansen's SPA test, and an effective number of tries, since 500 near-identical versions count for less than 500 independent ones |

You can also cut a backtest's return by a set amount before anything else uses it, for a backtest that came from data mining. A run made in Proofstone brings its number of tries from the study tracker.

### Portfolios of backtests

Proofstone treats each backtest's return series as an asset and solves for the weights within limits you set, such as weight bounds, long only, or a leverage cap. Two goals:

- **Maximize return with Sharpe ≥ X.** This is a convex problem: the Sharpe floor is a second-order cone constraint, so a solver finds the true optimum for any number of backtests. The floor applies to the deflated Sharpe ratio, not the raw one.
- **Maximize return with drawdown ≤ Y.** This isn't convex, because drawdown depends on the order of returns. A grid or random search handles a handful of backtests. For more, a limit on conditional drawdown at risk (CDaR, the average of the worst drawdowns) makes it a linear program.

Three things set it apart from existing optimizers:

1. **Drawdown limits apply to simulated drawdowns by default**, such as the 95th-percentile drawdown across resampled paths, with the historical maximum shown beside it. The historical maximum is a single sample: whichever crash happens to be in the data.
2. **The frontier is a band, not a line.** An optimizer piles weight on whichever backtest got luckiest. Re-running it on resampled histories shows the set of mixes that can't be told apart from the best one.
3. **The optimization counts as more tries.** Choosing weights is itself a search, so the report says how much of the best mix's edge holds up when the weights are fit on one half of the history and tested on the other. The study tracker counts each search's portfolios as tries.

### History and Monte Carlo

- **History:** growth, drawdowns, rolling returns and Sharpe ratio, calendar returns, and the longest time under water.
- **Monte Carlo:** block bootstrap resampling, fan charts, the distribution of ending wealth and of drawdowns, and the chance of breaching a limit.

### The app and the report

**The app** runs on your machine and opens in a browser (open decision 1). It sets up runs, sweeps and planned experiments from the strategy types, shows the strategies page and each strategy's tests and reports, and re-optimizes portfolios live as limits change. Results already computed open at once, and a run shows its progress while it computes.

**The report** is one self-contained HTML file that works offline and can be sent as a file. It has interactive charts (hover, toggles, and sliders over results computed in advance, such as frontiers at a grid of Sharpe floors and drawdown caps), light and dark themes, and prints to PDF. The app exports any of its pages as this report.

## Principles

- **Local first, bring your own data.** Proofstone runs on your machine and ships no market data. Most free market data, such as Yahoo's and exchange and index providers' sites, is licensed for personal use only, and licenses to redistribute it cost far more. You supply series and option chains from your own sources, accounts, or other backtesters. Where Proofstone offers a download, it runs on your machine, under your own terms with the source (open decision 11). Examples use simulated series and public-domain FRED series.
- **A calculator, not an adviser.** You supply the strategies and the limits. Proofstone ships no recommended funds, weights, parameters, or presets, doesn't ask about your finances, and isn't marketed as finding your best portfolio. The Advisers Act's definition of an adviser includes being paid, and ads, affiliate links, or a paid upgrade can count, so a securities lawyer reviews the line before any paid version.
- **Adjusted beside unadjusted.** Every adjusted or discounted figure is shown next to the raw one, and "doesn't beat chance" is a normal result.
- **Every run counts.** Making variants cheap to try also makes data mining cheap, so the study tracker records every run as a try, and nothing can be deleted from the count.
- **Nothing private comes in.** No data, results, or account details from the owner's private research enter this repository. Code from that research is rewritten for general inputs, not copied with its assumptions. The owner's research uses Proofstone as any user would: on the owner's machine, its series and runs are exported into Proofstone's input formats, and its results check the engine (see [Process](#process)). None of that enters this repository.

## Architecture

```text
data files ──▶ data catalog ──▶ strategy engine ──▶ runs ──▶ study tracker ──▶ engine ──────▶ results.json ──▶ report renderer ──▶ report.html
(series,       (manifests,      (strategy types,    (settings,  (strategies,      (statistics,   (versioned        (layout, charts,
 option         checksums,       option pricing,     trades,     tests, tries,     Monte Carlo,   schema)           themes)
 chains)        alignment)       sizing, accounts)   returns)    registrations)    optimizer)          │
                                                                                                       └──────▶ app (localhost)
runs from other tools ─────────────────────────────▶ runs
```

- **Inputs:** return or price series in CSV or Excel files, daily or monthly, starting on different dates, and the risk-free rate from FRED; option chains through import adapters; runs from other tools.
- **Data catalog:** each file's manifest entry, and the series aligned across dates and frequencies.
- **Strategy engine:** a Python library holding the strategy types, option pricing at quotes or on a model, sizing, accounts and taxes.
- **Runs and the study tracker:** a local database of runs, with each run's settings, trades, daily returns on the three bases, and tries, grouped into strategies, studies and registrations.
- **Engine:** a Python library for the statistics, Monte Carlo and the optimizer.
- **Results file:** JSON with a versioned schema, the only contract between the engine and the report or the app. After the design phase, changes to the schema are additions only.
- **Report renderer:** builds the HTML from a results file alone, so the report can be designed and built before the engine exists.
- **App:** a local server over the same libraries and results files, with a browser front end (open decisions 1 and 6).
- **Command line:** commands that write a report or run a specification, for example `proofstone report` for one backtest, `proofstone frontier` for a portfolio of them, `proofstone run` for a run from a specification file, and `proofstone serve` for the app.

Later shells over the same engine and report: a browser-only version and a desktop app.

## Plan: design first

The report is built first, against made-up results, and the engine fills it in section by section. The app's screens follow the same path: designed on sample results, then made real slice by slice. Design runs on the owner's fast review while the engine's code goes through the slower agent review.

### Phases

1. **Contract and sample data (days 1–2).** The results schema, and a throwaway script that writes sample results from simulated strategies. The samples are difficult on purpose: histories that start on different dates, one extreme month, a strategy that fails, long names, and both 2 and 12 strategies. They also include sample runs with trades, a sweep, a registered study, and an option strategy priced partly from quotes and partly from a model.
2. **Design rounds (days 2–7).** Two or three visual directions rendered from the samples, for the report and the app's main screens: the strategies page, a strategy's tests, a strategy's report, and setting up a run. The owner picks one and refines it over 3 or 4 rounds. The mockups are thrown away afterward.
3. **Production report and a thin real slice (week 2).** The chosen design becomes the report's components. Beside it, the first slice runs end to end: CSV in, growth and drawdowns out, in the real report.
4. **Slices (weeks 3–5).** Each engine slice switches one report section from sample data to real results, in a report that already looks finished.
5. **The tracker, strategy reports and the app (weeks 6–9).** Runs from files fill the study tracker and the strategy reports, then the app shows them and sets up runs.
6. **The strategy engine (weeks 9–14).** Strategy types arrive in three groups: series strategies, portfolios and accounts, then option strategies, after the chain store and the pricing models. Each group is checked against the owner's research before it's merged (see [Process](#process)).

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
| S13 | Run records: the schema's additions for a run's settings, trades, daily returns on the three bases, manifest entries, model version and tries, read from files | — | S1, S4 |
| S14 | Study tracker: strategies, studies, tries counted automatically, the required t-statistic, the best case, decisions | Strategies page, a strategy's tests | S6, S13 |
| S15 | Strategy reports: trade statistics, monthly and yearly returns on the three bases against a benchmark, risk statistics, stress periods | A strategy's report | S5, S13 |
| S16 | Discounts: return cuts and shares of the edge, by model version, data source or run, beside the raw figures | Discounts, everywhere | S15 |
| S17 | Comparing a rule with its baseline: paired block bootstrap, Newey-West t-statistic, the sign test across episodes, stress periods, neighboring parameters, every start day | Comparisons | S7, S15 |
| S18 | The app's shell: the local server, the strategies page, a strategy's tests and report, live re-optimization, export to the HTML report | The app, on runs from files | S3, S9, S14, S15 |
| S19 | Data catalog: adding files, manifest entries with checksums and terms, flagging a changed file | — | S4 |
| S20 | Engine I, series strategies: hold, timing rules, costs, leverage and its financing, volatility targeting, sleeves from series | Runs made in Proofstone | S13, S19 |
| S21 | Setting up runs in the app: a strategy type's parameters, sweeps that count each combination, planned experiments under one budget, safe resume | The app's setup screens | S18, S20 |
| S22 | Engine II, portfolios and accounts: weights, rebalancing, cash, margin, after-tax returns by tax bracket and account type, account size and whole contracts, sizing studies | Portfolios built in Proofstone | S20 |
| S23 | Option chain store: import adapters for end-of-day and intraday quote files and for snapshots of delayed quotes, normalized and catalogued | — | S19 |
| S24 | Option pricing: fills at quotes, and versioned models for days without quotes, fitted to the chains and checked on dates they weren't fitted on | — | S23 |
| S25 | Engine III, option strategies: credit spreads and ladders of them, condors, long options as hedges, their exits, entry filters, sizing and collateral | Option strategies | S22, S24 |
| S26 | Registration and forward records: frozen specifications with hashes, decisions, and out-of-sample records from data added over time | Registrations, forward records | S14, S21 |
| S27 | Docs II: the strategy types, the data formats and adapters, and the study tracker, with examples on simulated and FRED data | — | S20–S26 |

The critical path is S0, S1, S2, S3, S5, S8, S9, S13, S14, S18, S20, S22, S24, S25, then the release. S4, S6, S7, S10, S11, S12, S15–S17, S19, S21, S23, S26 and S27 run beside it.

### Milestones and versions

| Milestone or version | Target | Done when |
|---|---|---|
| M1: design chosen | End of week 2 | Schema version 1 is merged, and the owner has chosen the design of the report and the app's main screens from mockups on sample data |
| 0.1.0: first real report | Week 2–3 | A CSV of returns produces a finished-looking report; History is real, and the other sections still show sample data |
| 0.2.0: statistics and Monte Carlo | Week 3–4 | S6 and S7 are merged |
| 0.3.0: frontier | Week 4–5 | S8 and S9 are merged |
| 0.4.0: study tracker | Week 6 | S13 and S14 are merged: runs from files show on the strategies page and each strategy's tests, with the required t-statistic |
| 0.5.0: strategy reports | Week 7 | S15, S16 and S17 are merged: trades, returns on the three bases, risk statistics, discounts and comparisons are real |
| 0.6.0: the app and series strategies | Weeks 8–9 | S18, S19, S20 and S21 are merged: the app sets up and runs series strategies and shows every page |
| 0.7.0: portfolios and accounts | Week 10 | S22 is merged, and its results match the owner's research |
| 0.8.0: option chains and pricing | Weeks 11–12 | S23 and S24 are merged, with each model's fit error reported |
| 0.9.0: option strategies and registration | Week 13 | S25 and S26 are merged, and the option strategies' results match the owner's research |
| 1.0.0: free public release | Weeks 13–14 | Every section is real, S10 to S12 and S27 are merged, and the license is chosen |

The earlier plan's 1.0.0, the analysis half (through 0.3.0, with S10 to S12), takes about 3 to 4 weeks, and without S10 and S11 (grid search only, and statistics from the number of tries only) about 2 weeks. Open decision 5 asks whether to release it first.

Later, unscheduled:

- the file connection from Trial Folio, once its 0.5.0 produces normalized return series: its runs' return series and number of tries, in Proofstone's input format;
- imports from other tools' exports, such as Portfolio Visualizer, QuantConnect, and broker statements;
- a browser-only version, served as a static site with the computation on the user's machine;
- a desktop app, only if installing becomes the main complaint;
- a paid layer, after a securities lawyer's review.

After-tax returns by tax bracket and account type, earlier in this list, are now in S22, since the owner's research tests them.

### Timeline

About 3 months to 1.0.0. Review rounds set the pace, not coding: about 14 slices are in sequence, and at two agent review rounds each that's about 28 rounds, or about 14 working days at half a day per round. Getting the statistics right (2 to 3 days), the option pricing and its checks (1 to 2 weeks), the checks against the owner's research (a day or two for each engine slice), and the design rounds (5 to 7 days, overlapping other work) add the rest. The app, rather than a command-line tool with a report, adds about 2 weeks.

### Process

- Production code goes through agent review. Design mockups are reviewed by the owner only, pending the owner's decision.
- Each statistic's expected numbers, taken from published worked examples, are written into the spec before its code, so review checks the code against fixed answers instead of re-deriving the math. Each strategy type's expected trades and returns on simulated data are written in the same way, before its code.
- **Checks against the owner's research.** Each engine slice (S20, S22, S24, S25) is run on the owner's machine against the owner's private research, which already has results for every strategy type, and must match them before it merges. The check, its data and its results stay in the private research. This repository records only that the check passed.
- Pull requests stay small, and slices that don't depend on each other are reviewed at the same time.

## Related tools

| Tool | What it does |
|---|---|
| [Assayon](https://strategy-platform-web.onrender.com/) | A free stock backtester that adjusts its t-statistic for the number of tries, counts every combination in a parameter sweep as a try, and requires a blind out-of-sample window |
| [BacktestProof](https://chromewebstore.google.com/detail/hnanggmnenahjfkobmfmjafimdenkicf) | A Chrome extension that scores exports from NinjaTrader, MetaTrader 5, and TradingView from 0 to 100, including for overfitting |
| Portfolio Visualizer, testfol.io | Portfolio backtests and optimizers, with licensed data |
| QuantConnect | A backtesting platform with licensed data |
| [Trial Folio](https://github.com/promptedportfolio/trialfolio) | This organization's tool for Portfolio123 research, kept specialized to it. Its roadmap plans descriptive return analytics (0.5.0), statistical evaluation (0.6.0), and grid search (0.7.0), and it doesn't import results produced elsewhere. The two stay separate and connect through files. For Proofstone it's an example: settings recorded beside results, planned experiments under one approval and budget, safe resume, and runs compared by the settings that differ |

Neither Assayon nor BacktestProof appears to offer portfolios of backtests or Monte Carlo reports.

## Decisions

### Decided by owner

1. **The name: Proofstone** (2026-10-22). Chosen over Cupelwork and Luckproof. It was free on PyPI, and no company or product using it was found. A trademark search remains to be done.
2. **The repository: `promptedportfolio/proofstone`** (2026-10-22), private at first.
3. **Version 1 is free** (2026-10-22).
4. **Proofstone and Trial Folio stay separate** (2026-10-22). Proofstone builds its own statistics rather than sharing a library with Trial Folio's 0.5.0 to 0.7.0, so neither project waits on the other's methods. The two connect through files, added once Trial Folio's 0.5.0 produces normalized return series: Trial Folio writes each run's return series and number of tries in Proofstone's input format, and Trial Folio still imports nothing. On 2026-10-24 the owner added that Trial Folio stays specialized to Portfolio123, and serves Proofstone only as an example.
5. **The repository is public from 2026-10-24, not from 1.0.0**, and isn't promoted. Being public lets GitHub require pull requests on `main` without a paid plan. Anything committed is public for good, so a pre-commit hook (`scripts/check_private.py`, set up in [CONTRIBUTING.md](CONTRIBUTING.md)) keeps the owner's private research out.
6. **Proofstone becomes the backtesting tool too** (2026-10-24). It adds the data catalog, the strategy engine, the study tracker, strategy reports and the screens that set up tests, enough to run every test in the owner's research and to build new ones from added datasets. Nothing is dropped from the earlier plan or from what the owner asked of the tool. The scope grows from about 3 to 4 weeks to about 3 months to 1.0.0, and the form of version 1 needs an app (open decision 1).

### Open decisions

1. **The form of version 1.** A command-line tool that writes a self-contained HTML report adds no time and is easy to share, but it can only show results: setting up tests needs an app. A localhost app, a local server with a browser front end over the Python libraries, adds about 2 weeks and re-optimizes live. A desktop app adds 2 weeks or more on top, plus code signing and testing on three platforms. The earlier default was the command-line tool and HTML report, with localhost in 1.1.0.
   **Proposed default:** the localhost app, which exports the self-contained HTML report, with the command line kept for scripted runs.
2. **The license.** Apache-2.0 keeps a later paid layer possible and includes a patent grant. MIT is the simplest. AGPL keeps hosted copies open. The Nathan Slaughter Personal Research License 1.1, which Trial Folio uses, is source-available rather than open source.
   **Proposed default:** Apache-2.0.
3. **The chart library, embedded so the report works offline.** Observable Plot is small, with handsome defaults that are easy to theme. Vega-Lite charts are JSON that Python can write directly. ECharts has polished interactions but a large file. Plotly looks generic and is about 3.5 MB. The app uses the same library.
   **Proposed default:** Observable Plot.
4. **Who reviews design mockups.** The mockups are thrown away, and the owner's eye is the right check for looks. Agent review would add rounds to the design phase.
   **Proposed default:** the owner only; agent review stays on production code.
5. **What 1.0.0 contains.** Everything above makes 1.0.0 about 3 months away. Releasing the analysis half as 1.0.0 in about 3 to 4 weeks, with the engine, tracker and app as 2.0.0, gets public feedback sooner, but on the part the owner's own research needs least.
   **Proposed default:** everything in 1.0.0.
6. **The app's front end.** React with TypeScript is what Portfolio Workbench, this organization's desktop app, uses, and it has the most components and help. Svelte is smaller and quick, with fewer libraries. Pages rendered by the Python server with htmx keep everything in Python, with the fewest moving parts, but suit live charts and sliders less well. Under any of them, the speed comes mostly from computing results in advance and caching runs.
   **Proposed default:** React with TypeScript.
7. **The correction behind the required t-statistic.** Bonferroni's is the strictest, and for the best test it equals Holm's. Benjamini, Hochberg and Yekutieli's false discovery rate is less strict and needs every test's p-value. Harvey, Liu and Zhu's thresholds come from the factor literature.
   **Proposed default:** Holm's (Bonferroni's for the best test), with Benjamini-Hochberg-Yekutieli's beside it, and the deflated Sharpe ratio as in Statistics.
8. **Which tries count against a strategy.** A strategy's own tests give the count that matches the question asked of it. Every test run on the same history counts the whole search, which is stricter. The effective number of tries (S10) discounts near-identical versions but needs every version's return series.
   **Proposed default:** the strategy's own tests, with the whole tracker's count and, where it can be computed, the effective number beside it.
9. **A strategy's best case.** The version you kept reflects the decision actually made. The best-scoring version is the one the required t-statistic discounts.
   **Proposed default:** the kept version, marked, with the best-scoring one beside it, or the best-scoring one when none was kept.
10. **Defaults for the strategy types' parameters.** Defaults make the app quicker to try, but they read as presets, which "a calculator, not an adviser" rules out.
    **Proposed default:** every parameter required, with no defaults; examples on simulated data show their parameters as examples only.
11. **Downloads.** File import works for every source. FRED's series are in the public domain. Downloads from other free sources, such as exchanges' delayed quotes, index providers and Yahoo, would run on the user's machine under the user's own terms with each source.
    **Proposed default:** file import and FRED in version 1, and other downloads later, each after a check of its source's terms.
