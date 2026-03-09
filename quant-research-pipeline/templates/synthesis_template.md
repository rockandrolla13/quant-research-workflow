# Synthesis Template

Used by Claude (Stage 2) to produce `synth/strategy.md` and `synth/formula.md`
from `artifacts/01-extraction.md`.

---

## strategy.md sections (all required)

### 1. Core Claim
One sentence: what does this paper actually contribute? What market inefficiency
does it exploit and why should it persist?

### 2. Thesis / Intuition
2-4 sentences. WHY does this work? What participant behaviour or structural
feature creates the opportunity? Be opinionated — if the thesis is weak, say so.

### 3. Data Requirements
Table format:
| Field | Value |
|-------|-------|
| Asset class | ... |
| Instruments | ... |
| Universe | ... |
| Frequency | ... |
| History required | ... |
| Vendors | ... |
| Additional data | ... |
| Transaction costs | ... |

### 4. Signal Decomposition
Break the approach into independent algorithmic components. For each:
- Name and one-sentence description
- Inputs and outputs
- Which [SIG:n] and [EQ:n] tags from extraction it implements
- Dependencies on other components

### 5. Dependency Graph
Mermaid diagram showing which components depend on which.
Data flows left-to-right, signals flow into portfolio construction.

### 6. Execution Assumptions
How would this trade? Rebalance frequency, execution model (T+0/T+1),
position sizing, leverage, notional assumptions.

### 7. Risk Controls
Position limits, drawdown stops, concentration limits, kill switches.
Note which are from the paper vs which you're adding.

### 8. Implementation Decisions
Where does the paper leave choices open? For each open choice:
- What the paper says (or doesn't say)
- 2-3 concrete approaches with trade-offs
- Recommended default

Must surface at least 3 open decisions.

### 9. What's Missing
What does the paper assume the reader knows or will figure out?
- Numerical stability concerns
- Edge cases not addressed
- Scaling considerations
- Data that may be hard to source

### 10. Failure Modes
When does this break? Be specific:
- Market regime changes
- Data quality issues
- Parameter sensitivity
- Capacity constraints

### 11. Stress Test
Which component is most likely to fail or underperform in practice? Why?

### 12. Minimal Backtest Plan
Simplest confirmatory/rejecting test. Which signals first, what date ranges,
what constitutes pass/fail.

---

## formula.md sections (all required)

### 1. Scope
IN-SCOPE: which signals/equations are being implemented in this version.
OUT-OF-SCOPE: which are documented but deferred.

### 2. Symbol Table
| Symbol | Meaning | Type | Units |
|--------|---------|------|-------|
Every symbol used in any equation. No ambiguity.

### 3. Equations
All equations in LaTeX with numbered subsections (Eq. 0, Eq. 1, ...).
Each equation MUST have a "Where:" block defining every variable.
Cross-reference [EQ:n] tags from extraction.

### 4. Computation Steps
Ordered algorithm for each signal. Pseudocode-level, step by step.
Reference equations by number.

### 5. Edge Cases
Missing data handling, stale quotes, look-ahead bias risks, division-by-zero
guards, boundary conditions.
