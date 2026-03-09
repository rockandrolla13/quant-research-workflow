# Review of fx_cookbook Strategy Contract

This review assesses the consistency and clarity of the strategy specification based on the provided files: `spec.yaml`, `formula.md`, and `SPEC.md`.

| Category | Verdict |
| :--- | :--- |
| 1. Units/annualisation | FAIL |
| 2. Calendar assumptions | FAIL |
| 3. Quote convention | WARN |
| 4. Cost model | FAIL |
| 5. Ambiguous symbols/lookbacks | WARN |

---

### Concrete Edit Suggestions

*   **File:** `strategies/fx_cookbook/synth/formula.md`
    *   **Section:** `Core Equations`
    *   **Change:** Add equation for Annualized Sharpe Ratio: `Annualized Sharpe Ratio = \frac{E[R_p] - R_f}{\sigma_p} \times \sqrt{252}`
*   **File:** `strategies/fx_cookbook/synth/formula.md`
    *   **Section:** `Core Equations`
    *   **Change:** Add equation for Annualized Volatility: `\sigma_{ann} = \sigma_{daily} \times \sqrt{252}`
*   **File:** `strategies/fx_cookbook/spec/spec.yaml`
    *   **Section:** `success_criteria.metrics`
    *   **Change:** Add `annualized: true` to each relevant metric.
*   **File:** `strategies/fx_cookbook/synth/formula.md`
    *   **Section:** `Numerical Constants`
    *   **Change:** Add constant for trading days: `TRADING_DAYS_PER_YEAR`, `252`, `Assumed number of trading days for annualization`.
*   **File:** `strategies/fx_cookbook/spec/SPEC.md`
    *   **Section:** (New) `Assumptions`
    *   **Change:** Add section detailing calendar assumptions: "We assume 252 trading days per year for all annualization calculations."
*   **File:** `strategies/fx_cookbook/spec/spec.yaml`
    *   **Section:** `data_schema.universe`
    *   **Change:** Change `"S&P 500 constituents"` to `"G10 Currencies quoted against USD"`.
*   **File:** `strategies/fx_cookbook/spec/SPEC.md`
    *   **Section:** (New) `Data and Quote Conventions`
    *   **Change:** Add section specifying quote convention: "All currency pairs are quoted as `CCY/USD` (FX_per_USD)."
*   **File:** `strategies/fx_cookbook/spec/spec.yaml`
    *   **Section:** (New) `execution`
    -   **Change:** Add new section for cost model: `execution:\n  cost_model:\n    spread_bps: 0.5\n    slippage_bps: 0.2`.
*   **File:** `strategies/fx_cookbook/synth/formula.md`
    *   **Section:** (New) `Cost Model`
    -   **Change:** Add section defining the cost model: `Execution Price = Market Price \times (1 + \frac{Slippage_{bps}}{10000})`.
*   **File:** `strategies/fx_cookbook/synth/formula.md`
    *   **Section:** `Symbol Table`
    -   **Change:** Add note to `$V_t$` description: "Volume at time $t$ (for future use in volume-weighted strategies)".
*   **File:** `strategies/fx_cookbook/synth/formula.md`
    *   **Section:** `Symbol Table`
    -   **Change:** Change `$N$` description to: "Lookback period (e.g., `rsi_period` from parameters)".