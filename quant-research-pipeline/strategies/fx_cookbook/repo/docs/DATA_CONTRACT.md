# Data Contract

## Required columns
- `date` (datetime): observation date
- `currency_pair` (str): e.g., `EURUSD`
- `spot_rate` (float64): spot quote
- `forward_1m` (float64): 1-month forward quote
- `forward_6m` (float64, nullable): 6-month forward quote
- `bid_ask_spread` (float64): spread in quote units
- `total_return` (float64): daily total return (spot + carry)

## Quote convention
- `USD_per_FX`: quote is USD per 1 unit of foreign currency (e.g., 1.10 USD/EUR)
- `FX_per_USD`: quote is FX per 1 USD (e.g., 0.91 EUR/USD)

If `FX_per_USD` is provided, the loader inverts `spot_rate` and `forward_*` to `USD_per_FX` and recomputes `total_return`.

## Calendar
Configured in `config.yaml`:
- `bdays_per_month`: business days per month (default 21)
- `bdays_per_year`: business days per year (default 252)

`total_return` is recomputed as:
- `spot_return = spot_rate.pct_change()`
- `carry = (spot_rate - forward_1m) / forward_1m / bdays_per_month`
- `total_return = spot_return + carry`
