# Module 1 — Returns

## Learning objectives

After this module, you should be able to distinguish a price from a return, calculate one-period
and multi-period arithmetic returns, calculate log returns, implement each operation with NumPy,
and explain common return-data mistakes.

## 1. Theory

A **price** is a level measured in currency. A **return** is the gain or loss relative to capital
at risk. Comparing a $5 price increase in a $20 asset with a $5 increase in a $500 asset is
misleading; returns put both moves on a common scale.

For price `P[t-1]` followed by `P[t]`, the simple or arithmetic return is

```text
r[t] = P[t] / P[t-1] - 1 = (P[t] - P[t-1]) / P[t-1]
```

A value of `0.03` means `+3%`; `-0.03` means `-3%`. There are `n-1` returns for `n` prices.

Wealth compounds multiplicatively. If returns are `r[1], ..., r[T]`, then

```text
growth factor = product(1 + r[t])
cumulative return = product(1 + r[t]) - 1
wealth[t] = initial_wealth * product from i=1 to t of (1 + r[i])
```

Do not add multi-period arithmetic returns except as an approximation for very small moves.
A `+50%` move followed by `-50%` is not flat: `1.50 * 0.50 - 1 = -25%`.

The continuously compounded or **log return** is

```text
g[t] = ln(P[t] / P[t-1]) = ln(1 + r[t])
```

Log returns add across time:

```text
sum(g[t]) = ln(P[T] / P[0])
```

Convert between the two with `g = log1p(r)` and `r = expm1(g)`. Simple returns cannot be below
`-100%`. Log return is undefined when a price is zero or negative.

### Which return should we use?

- Use simple returns for actual portfolio wealth and cross-sectional portfolio aggregation:
  `portfolio_return = weights @ asset_simple_returns` for fixed beginning-of-period weights.
- Log returns are convenient for time aggregation and some statistical models.
- Neither choice repairs bad data. Split-unadjusted prices can create fictitious crashes, while
  missing dividends cause total return to be understated.

## 2. Manual example

Suppose adjusted prices are `[100, 110, 99, 108.90]`.

Simple returns:

```text
day 1: 110 / 100 - 1 =  0.10 =  10%
day 2:  99 / 110 - 1 = -0.10 = -10%
day 3: 108.90 / 99 - 1 = 0.10 =  10%
```

Cumulative growth is not `10% - 10% + 10% = 10%` by addition. It is

```text
(1.10)(0.90)(1.10) - 1 = 1.089 - 1 = 0.089 = 8.9%
```

The endpoint check gives the same answer: `108.90 / 100 - 1 = 8.9%`.

Log returns (rounded) are `[0.09531, -0.10536, 0.09531]`. Their sum is `0.08526`, and
`exp(0.08526) - 1 = 8.9%`.

### Two-asset one-period example

An equally weighted portfolio starts with $50 in A and $50 in B. A returns `+10%`; B returns
`-4%`. Its return is `0.5(0.10) + 0.5(-0.04) = 0.03`, or `3%`, and wealth becomes $103.

This weighted-sum rule uses **simple**, same-period asset returns. Adding weighted log returns
does not exactly reproduce portfolio wealth.

## 3. NumPy implementation

```python
import numpy as np


def simple_returns(prices: np.ndarray) -> np.ndarray:
    prices = np.asarray(prices, dtype=float)
    if prices.ndim != 1 or prices.size < 2:
        raise ValueError("prices must be a 1D array with at least two values")
    if np.any(~np.isfinite(prices)) or np.any(prices <= 0):
        raise ValueError("prices must be finite and positive")
    return prices[1:] / prices[:-1] - 1.0


def cumulative_returns(returns: np.ndarray) -> np.ndarray:
    returns = np.asarray(returns, dtype=float)
    if np.any(~np.isfinite(returns)) or np.any(returns < -1.0):
        raise ValueError("simple returns must be finite and at least -1")
    return np.cumprod(1.0 + returns) - 1.0


def log_returns(prices: np.ndarray) -> np.ndarray:
    prices = np.asarray(prices, dtype=float)
    if prices.ndim != 1 or prices.size < 2:
        raise ValueError("prices must be a 1D array with at least two values")
    if np.any(~np.isfinite(prices)) or np.any(prices <= 0):
        raise ValueError("prices must be finite and positive")
    return np.log(prices[1:] / prices[:-1])
```

Understand every array operation:

- `prices[1:]` selects every price except the first.
- `prices[:-1]` selects every price except the last.
- Elementwise division aligns each ending price with its preceding price.
- `np.cumprod` applies compounding in chronological order.
- `np.log` is elementwise. `@`, matrix multiplication, is not needed yet.

## 4. Exercises

Do exercises 1–5 on paper before using Python.

1. Prices are `[80, 84, 79.80, 87.78]`. Calculate all three simple returns.
2. Compound those returns and verify the answer using only the first and last price.
3. An asset falls 20%. What return is needed to recover to its starting value? Explain why it
   is not 20%.
4. Compare `+25%` followed by `-20%` with `-20%` followed by `+25%`. Does order affect terminal
   wealth? Does it affect the path?
5. A portfolio has beginning weights `[0.50, 0.30, 0.20]` and same-period asset returns
   `[0.04, -0.02, 0.01]`. Calculate its return and ending value from $10,000.
6. Reimplement `simple_returns` without `np.diff` or a loop. Test its output shape.
7. Implement terminal cumulative return using `np.prod`, then the full cumulative path with
   `np.cumprod`.
8. Implement simple-to-log and log-to-simple conversions using `np.log1p` and `np.expm1`.
9. Assert that summed log returns equal `log(last_price / first_price)` within floating-point
   tolerance using `np.testing.assert_allclose`.
10. Use a 2D price matrix with rows as dates and columns as assets. Compute returns along the
    time axis. State the output shape before running it.
11. Write validation tests for one price, a zero price, `NaN`, a `-100%` return, and a return
    below `-100%`. Decide which cases are mathematically valid and which should fail.
12. Explain in three sentences why a daily mean return multiplied by 252 is not the same as a
    guaranteed annual return.

### NumPy challenge skeleton

```python
import numpy as np

prices = np.array(
    [
        [100.0, 50.0],
        [102.0, 49.0],
        [101.0, 51.0],
        [104.0, 50.0],
    ]
)

# TODO: calculate simple returns down rows (time), preserving both columns.
asset_returns = ...

# Beginning-of-period weights. Assume rebalanced to these weights each period.
weights = np.array([0.60, 0.40])

# TODO: calculate the portfolio return for every row using matrix multiplication.
portfolio_returns = ...

# TODO: calculate a $10,000 wealth path, including $10,000 as the first observation.
wealth = ...
```

Expected shapes are `(3, 2)`, `(3,)`, and `(4,)`. Do not inspect numerical answers until your
shapes and formulas are written down.

## 5. Answer checks

Use these after completing the work:

1. `[+5%, -5%, +10%]`.
2. `+9.725%`; endpoint: `87.78 / 80 - 1`.
3. `+25%`, because `0.8 * 1.25 = 1`.
4. Both finish flat because `1.25 * 0.8 = 1`; the intermediate wealth paths differ.
5. `1.6%`, ending wealth `$10,160`.

Challenge values (rounded):

```text
asset returns:
[[ 0.020000, -0.020000],
 [-0.009804,  0.040816],
 [ 0.029703, -0.019608]]

portfolio returns: [0.004000, 0.010444, 0.009978]
wealth: [10000.00, 10040.00, 10144.86, 10246.09]
```

## 6. Project implementation and review gate

The repository already has a Polars `prices_to_returns` adapter. Before changing it, verify:

- observations are sorted within each asset;
- price validation happens before division;
- the first return per asset is absent rather than fabricated as zero;
- `available_at` remains attached for point-in-time filtering;
- adjusted-price and dividend policy is documented when a real data source is selected.

Module 1 is complete when you can derive the equations without notes, pass your edge-case tests,
explain why returns compound, and identify whether a calculation calls for simple or log returns.
Do not begin portfolio covariance or optimization until those checks are comfortable.
