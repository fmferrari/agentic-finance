"""One-bar deterministic research simulation, explicitly NOT a broker simulator."""
from dataclasses import dataclass
import math
from .strategy import signal_at

@dataclass(frozen=True)
class Assumptions:
    fee_bps_per_side: float = 2.0
    slippage_bps_per_side: float = 3.0
    reference_stop_fraction: float = 0.01


def trades(prices, start, end, fast, slow, assumptions=Assumptions(), delay=1):
    """Signal uses close t, entry close t+delay, exit next close.

    Entries are delayed by >=1 full bar. Indices [start,end) denote
    signal bars, NOT trades' exit bars. Both fills must fall within end.
    Every signal is a new 1-bar research trade (no overlapping positions).
    """
    if delay < 1 or start < 0 or end > len(prices) or start >= end:
        raise ValueError("Invalid simulation window")
    if (not all(math.isfinite(x) for x in (assumptions.fee_bps_per_side, assumptions.slippage_bps_per_side, assumptions.reference_stop_fraction))
            or min(assumptions.fee_bps_per_side, assumptions.slippage_bps_per_side) < 0
            or assumptions.reference_stop_fraction <= 0):
        raise ValueError("Invalid costs or reference risk")
    results = []
    # No fill (including exit) crosses the evaluation partition boundary.
    for t in range(start, end - delay - 1, delay + 1):
        side = signal_at(prices, t, fast, slow)
        if not side:
            continue
        entry = prices[t + delay]
        exit_ = prices[t + delay + 1]
        gross_bps = side * (exit_ / entry - 1) * 10000
        cost_bps = 2 * (assumptions.fee_bps_per_side + assumptions.slippage_bps_per_side)
        net_bps = gross_bps - cost_bps
        # R here is a fixed normalization, not evidence a stop filled.
        results.append({"signal_index": t, "entry_index": t + delay,
                        "exit_index": t + delay + 1, "side": side,
                        "gross_bps": round(gross_bps, 6),
                        "net_bps": round(net_bps, 6),
                        "net_r_proxy": round(net_bps / (10000 * assumptions.reference_stop_fraction), 6)})
    return results


def scorecard(records):
    if not records:
        return {"trades": 0, "expectancy_bps": None, "win_rate": None, "max_drawdown_bps": None, "net_r_proxy": None}
    total, peak, worst_dd, wins = 0.0, 0.0, 0.0, 0
    for rec in records:
        x = rec["net_bps"]
        total += x
        peak = max(peak, total)
        worst_dd = max(worst_dd, peak - total)
        wins += x > 0
    return {"trades": len(records), "expectancy_bps": round(total / len(records), 6),
            "win_rate": round(wins / len(records), 6),
            "max_drawdown_bps": round(worst_dd, 6),
            "net_r_proxy": round(sum(r["net_r_proxy"] for r in records), 6)}
