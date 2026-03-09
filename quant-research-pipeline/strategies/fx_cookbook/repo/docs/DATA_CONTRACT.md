# Data Contract

## Canonical Schema

All adapters produce a DataFrame with these columns. The domain stack (signals, portfolio, risk, backtest, validation) consumes only this schema.

| Column | Type | Nullable | Description |
|---|---|---|---|
| `date` | datetime | no | Observation date |
| `asset` | str | no | Asset identifier (e.g. `EURUSD`, `AAPL_5Y`) |
| `total_return` | float64 | yes | Daily total return (first obs per asset is NaN) |
| `bid_ask_spread` | float64 | no | Transaction cost proxy |

Adapters may pass through additional columns (e.g. `spot_rate`, `duration`), but the domain stack ignores them.

## Adapters

### FX (`adapter.name: "fx"`)

**Raw input columns:** `date`, `currency_pair`, `spot_rate`, `forward_1m`, `bid_ask_spread` (required); `forward_6m`, `total_return` (optional)

**Parameters:**
- `quote_convention`: `"USD_per_FX"` (default) or `"FX_per_USD"` (inverts rates)
- `bdays_per_month`: business days per month for carry annualisation (default 21)

**Return computation:**
- `spot_return = spot_rate.pct_change()`
- `carry = (spot_rate - forward_1m) / forward_1m / bdays_per_month`
- `total_return = spot_return + carry`

**Column mapping:** `currency_pair` → `asset`

### Credit (`adapter.name: "credit"`)

**Raw input columns:** `date`, `bond_id`, `spread`, `duration`, `bid_ask` (all required)

**Parameters:**
- `bdays_per_year`: business days per year (default 252)
- `spread_unit`: multiplier to convert spread to decimal (default 0.0001 for bp input)

**Return computation:**
- `excess_return = -duration × Δspread + carry`
- `carry = spread × spread_unit / bdays_per_year`

**Column mapping:** `bond_id` → `asset`, `bid_ask × spread_unit` → `bid_ask_spread`

## Calendar

Configured in `config.yaml`:
- `bdays_per_month`: business days per month (default 21) — used by FX adapter
- `bdays_per_year`: business days per year (default 252) — used by backtest metrics and validation

## Adding a New Asset Class

1. Create `adapters/<asset>.py` with a dataclass implementing `ReturnsAdapter.adapt()`
2. Register in `adapters/__init__.py` registry
3. Set `adapter.name` and `adapter.params` in `config.yaml`

No other files need to change.
