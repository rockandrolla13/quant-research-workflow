# Extraction Prompt Template

This prompt is used by `tools/ingest.py` (Gemini pass) to extract structured content
from quant research PDFs. Variables in `{{braces}}` are filled by the tool.

---

You are extracting a quantitative research paper for implementation as a trading strategy.

## Instructions

Extract ALL structured content from this PDF. This is a sell-side quant research paper
(DB, JPM, or similar). Preserve the paper's section structure as markdown headings.

Tag every extractable element with the appropriate label:

| Tag | Use for | Example |
|-----|---------|---------|
| `[SIG:n]` | Signal definitions (entry/exit rules, alpha factors) | "Momentum signal: sign of rolling returns averaged over lookbacks" |
| `[EQ:n]` | Equations — preserve LaTeX notation | `$S_t = \frac{1}{K}\sum_{h} \text{sign}(r_{t-h,t})$` |
| `[PORT:n]` | Portfolio construction rules (weighting, rebalancing) | "Inverse volatility weights, absolute sum = 100%" |
| `[RISK:n]` | Risk controls and constraints | "Max position 15%, beta-neutral to USD PC1" |
| `[DATA:n]` | Data requirements, schemas, sources | "Daily spot and 1M forward rates for 24 USD/FX pairs" |
| `[ASSUMP:n]` | Assumptions and constraints stated by authors | "Transaction costs = 1.5x historical average bid-ask" |
| `[PARAM:n]` | Parameters, hyperparameters, tunable constants | "Lookback range: 21 to 252 business days" |
| `[TABLE:n]` | Tables — reproduce as markdown tables | Backtest results, signal performance |
| `[FIG:n]` | Figures — describe content, note what they show | "Cumulative return of momentum TS portfolio 2000-2018" |
| `[PERF:n]` | Reported performance metrics | "Sharpe 0.60, Max DD 15%, turnover 5.7%" |

## Rules

1. Preserve ALL equations as LaTeX (`$$` for display, `$` for inline)
2. Preserve ALL tables as markdown tables
3. Preserve section headings with `#` hierarchy matching the paper
4. Do NOT summarise — extract EVERYTHING
5. Tag elements inline where they appear in the text
6. Number tags sequentially within each type (EQ:1, EQ:2, ...)
7. If an element fits multiple tags, use the most specific one
8. Preserve figure/table captions and cross-references
9. Note when reported results use specific date ranges or universes

## Output

Write structured markdown. Begin with a metadata block:

```yaml
---
title: "{{paper_title}}"
authors: [{{authors}}]
date: "{{date}}"
source: "{{source_institution}}"
pages: {{n_pages}}
extraction_method: "{{method}}"
tags_found:
  SIG: {{n_sig}}
  EQ: {{n_eq}}
  PORT: {{n_port}}
  RISK: {{n_risk}}
  DATA: {{n_data}}
  ASSUMP: {{n_assump}}
  PARAM: {{n_param}}
  TABLE: {{n_table}}
  FIG: {{n_fig}}
  PERF: {{n_perf}}
---
```

Then the full paper content with tags.
