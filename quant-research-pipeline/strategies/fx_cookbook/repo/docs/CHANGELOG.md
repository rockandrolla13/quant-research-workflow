# Changelog

## v1.4
- Multi-asset adapter layer: `ReturnsAdapter` protocol with FX and credit implementations.
- Canonical schema `(date, asset, total_return, bid_ask_spread)` decouples domain stack from asset-specific data.
- Credit adapter: excess return from spread changes + carry, configurable spread units.
- Deep clean: refactored signals (4 helpers), extracted backtest primitives, parameterised bdays_per_year.
- 54 tests (29 original + 13 FX adapter + 12 credit adapter).

## v1.3
- Implementation tag: `fx_cookbook-impl-v1.3`
- Adds EWMA covariance with 3-offset averaging and expanded risk tests.
- Adds real data adapter, outputs pipeline, and replication docs.

## v1.2
- Spec tag: `spec-fx_cookbook-v1.2`
- Base implementation for signals/portfolio/risk/backtest/validation.
