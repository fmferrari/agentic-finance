"""Independent pre-trade sizing demonstration. No live order or stop execution."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class RiskPolicy:
    equity: float = 10000.0
    risk_fraction: float = 0.005
    max_notional_fraction: float = 0.50


def size_from_stop(entry, stop, direction, policy=RiskPolicy()):
    if direction not in (-1, 1):
        raise ValueError("Direction must be long (+1) or short (-1)")
    if entry <= 0 or stop <= 0 or not math.isfinite(entry) or not math.isfinite(stop):
        raise ValueError("Entry and stop must be finite positive prices")
    if (not all(math.isfinite(x) for x in (policy.equity, policy.risk_fraction, policy.max_notional_fraction))
            or policy.equity <= 0 or not (0 < policy.risk_fraction <= 0.05)
            or not (0 < policy.max_notional_fraction <= 1)):
        raise ValueError("Invalid risk policy")
    if direction == 1 and stop >= entry or direction == -1 and stop <= entry:
        raise ValueError("Stop must be on the loss side of entry")
    risk_per_unit = abs(entry - stop)
    max_risk_units = math.floor(policy.equity * policy.risk_fraction / risk_per_unit)
    max_notional_units = math.floor(policy.equity * policy.max_notional_fraction / entry)
    return min(max_risk_units, max_notional_units)
