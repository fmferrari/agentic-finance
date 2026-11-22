"""Causal signal calculated from history ending at bar t."""

def signal_at(prices, t, fast, slow):
    if fast < 2 or slow <= fast:
        raise ValueError("Need 2 <= fast < slow")
    if t < slow - 1:
        return 0
    # No forward indexing: both averages use closes at or before t.
    fast_ma = sum(prices[t-fast+1:t+1]) / fast
    slow_ma = sum(prices[t-slow+1:t+1]) / slow
    return 1 if fast_ma > slow_ma else -1
