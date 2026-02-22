# Strategy Synthesis: FX Cookbook

> Source: Deutsche Bank Quantcraft, "FX Cookbook: A Recipe for Systematic Investing in Currency Markets", Jan 2019
> Authors: Vivek Anand, Caio Natividade, George Saravelos, Jose Gonzalez, Shreyas Gopal, Rohini Grover

## Thesis / Intuition

FX markets contain non-profit-seeking participants (corporate hedgers, central banks, passive flows) whose activity creates persistent, exploitable inefficiencies across multiple horizons. The paper exploits this via 7 signals spanning short-term (positioning/flow), medium-term (momentum/carry), and long-term (value) factors. The key insight is that the USD is the dominant factor (PC1 explains ~54% of cross-sectional variance), and every signal must handle USD directionality explicitly — either capturing it (time-series) or neutralising it (cross-sectional via beta constraints).

This is a credible thesis. The factor zoo risk is mitigated by the paper's PCA and panel regression pre-screening, which confirms carry and momentum as the only robust predictors. The short-term signals (COFFEE, CFTC) rely on proprietary-ish data and shorter histories, which weakens their out-of-sample case.

## Data Requirements

- **Asset class**: FX (G10 + select EM), 24 USD/FX pairs
- **Instruments**: 1-month FX forwards (spot + carry embedded)
- **Currencies**: AUD, EUR, GBP, CHF, SEK, NOK, NZD, CAD, JPY, BRL, CZK, KRW, MXN, PLN, RUB, SGD, TRY, TWD, ZAR, HUF, ILS, INR, THB
- **Frequency**: Daily (3-day non-overlapping for risk estimation)
- **Additional data**:
  - 6-month FX forwards (carry signal)
  - BIS REER and PPP data (value signal)
  - GDP per capita, terms of trade by country (value signal)
  - DTCC options flow data (COFFEE signal — may be hard to source)
  - CFTC Commitment of Traders weekly (positioning signals)
  - Implied volatility (CVIX or proxy)
- **History**: 1980+ for momentum/carry, 1994+ for value (BIS REER), 2014+ for COFFEE (short)
- **Vendors**: Bloomberg, BIS, CFTC, national statistics offices
- **Transaction costs**: Fixed bid-ask spread = 1.5x long-term historical average

## Signal Definition

The paper defines 7 signals, each with time-series (TS) and/or cross-sectional (CS) portfolio implementations:

1. **Momentum** (medium-term): Sign-based trend signal averaged over lookback windows h ∈ {21,...,252} bdays. Deflated by signal dispersion. See formula.md Eq. 1–4.
2. **Carry** (medium-term): Forward-spot spread normalised by volatility. Reflects interest rate differentials. See formula.md Eq. 5–7.
3. **Value** (long-term): REER misalignment from DOLS panel regression on productivity differentials and terms of trade. See formula.md Eq. 8–11.
4. **Momentum Spill-Over / MSO** (short-term): Change in interest rate spread normalised by its volatility, averaged over 21/42/63 day windows. See formula.md Eq. 12.
5. **COFFEE** (short-term): DTCC high-delta option volume imbalance (calls − puts), standardised. See formula.md Eq. 13.
6. **CFTC Continuation** (short-term): 4-week sum of non-commercial net positioning, normalised. See formula.md Eq. 14.
7. **CFTC Reversal** (short-term): Z-score of net positioning (averaged over 1/2/3 month windows), volatility-adjusted, sign-flipped. Cross-sectional only. See formula.md Eq. 15.

All signals feed into either:
- **Time-series portfolios**: IVW (inverse volatility weighted), directional USD exposure
- **Cross-sectional portfolios**: Long top half / short bottom half, beta-neutralised to USD (PC1)

## Execution Assumptions

- **Rebalancing**: Monthly with daily tranches (20 tranches) for momentum/carry/value. Weekly for short-term signals.
- **Execution**: T+1 at NY close. Positions calculated end-of-day, executed next business day close.
- **Position limits**: Max |w_i| = min(15%, 2% of avg daily volume for $1bn portfolio)
- **Absolute weights sum to 100%** (no leverage in base case)
- **Latency**: Not latency-sensitive. Daily/weekly signals.
- **Notional**: Paper assumes $1bn reference portfolio for liquidity constraints.

## Risk Controls

- **Position limits**: Per-asset caps at min(15%, 2% of avg daily volume)
- **Beta neutralisation**: Cross-sectional portfolios target zero beta to USD PC1 via constrained optimisation
- **Signal dispersion deflation**: Final signal divided by signal volatility (prevents hyper-inflation during low-dispersion regimes)
- **Hysteresis noise control**: If |raw signal| < 1/3 threshold, keep previous signal (reduces turnover from ~5.9% to ~5.7% daily)
- **No explicit drawdown stops** mentioned — this is a weakness
- **No explicit kill switch** — another weakness for production

## Failure Modes

- **Carry crash**: EM carry trades are heavily exposed to risk-off events. The beta-neutral construct mitigates but doesn't eliminate this.
- **Trend reversal regimes**: Post-2008 QE regimes compressed FX vol and weakened momentum signals. The paper acknowledges declining carry contribution since 2010.
- **Value signal overfitting**: DOLS panel regressions on macro data (GDP, ToT) are inherently subject to data revision, look-ahead bias, and parameter instability. The paper's 5-panel structure adds degrees of freedom.
- **COFFEE data dependency**: DTCC data has short history (2014+) and limited accessibility. MIC levels may be overstated.
- **CFTC discretisation risk**: The paper explicitly tests and warns that weekly CFTC snapshots introduce material discretisation error, especially for the reversal signal (Section 4.6.6).
- **Correlation regime shifts**: IVW vs MCW choice hinges on average cross-asset correlation staying below ~50%. If FX correlations spike (e.g., USD crisis), IVW underperforms.
- **Transaction cost sensitivity**: Some short-term signals show Sharpe degradation after costs (MSO: 0.33 before, lower after).

## Minimal Backtest Plan

For a confirmatory/rejecting test, implement the **two highest-conviction signals** first:
1. **Carry (cross-sectional, max Sharpe)** — reported SR: 0.79, longest history, most robust MICs
2. **Momentum (time-series, IVW)** — reported SR: 0.60, well-documented factor

**Test protocol**:
- Reproduce signals on 2000–2015 (train), validate on 2015–2018 (validate)
- Hold out 2019–2024 (holdout — DO NOT TOUCH)
- Compare backtested Sharpe, turnover, max drawdown against paper's reported values
- If Sharpe within 0.1 of reported and sign-consistent, proceed to remaining signals
- If Sharpe < 0.3 or sign-inconsistent, investigate data/implementation differences before adding more signals
