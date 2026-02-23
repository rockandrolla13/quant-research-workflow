# SPEC_CHANGE_REQUEST_v1.3

## Clarifications Requested

1) **EWMA decay mapping**
   - Please specify how `decay_diag` and `decay_offdiag` map to EWMA alpha.
   - Implemented assumption: `alpha = 1 - exp(-1 / decay)`.
   - If a different convention is intended (e.g., halflife or span), update spec to define it explicitly.

2) **3-day non-overlapping returns definition**
   - Please clarify whether 3-day returns are computed as:
     - sum of daily returns, or
     - compounded return over 3 days.
   - Implemented assumption: **sum** of daily returns for each 3-day block.

3) **Offset definition**
   - Please explicitly define offsets as starting indices 0, 1, 2 for the 3-day blocks.
   - Implemented assumption: compute three block series with offsets 0/1/2 and average their EWMA covariance matrices elementwise.
