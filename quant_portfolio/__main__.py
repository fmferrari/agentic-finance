"""Run an auditable, deterministic and entirely synthetic research experiment."""
import json
from dataclasses import replace
from pathlib import Path
from .dataset import synthetic_prices, manifest
from .backtest import Assumptions, trades, scorecard
from .agent_contract import parse_proposal


def run():
    config = json.loads((Path(__file__).resolve().parent.parent / "config" / "research_protocol.json").read_text())
    seed = config["seed"]
    prices = synthetic_prices(config["observations"], seed)
    train_end = int(len(prices) * 0.6)
    valid_end = int(len(prices) * 0.8)
    candidates = [parse_proposal(item) for item in config["proposals"]]
    costs = Assumptions(**config["assumptions"])
    # Select using TRAIN scores exclusively; validation and holdout are not used for tuning.
    scored = [(scorecard(trades(prices, 0, train_end, x["fast"], x["slow"], costs)), x) for x in candidates]
    scored.sort(key=lambda item: item[0]["expectancy_bps"] if item[0]["expectancy_bps"] is not None else -1e12, reverse=True)
    _, winner = scored[0]
    f, s = winner["fast"], winner["slow"]
    valid = scorecard(trades(prices, train_end, valid_end, f, s, costs))
    holdout = scorecard(trades(prices, valid_end, len(prices), f, s, costs))
    doubled = replace(costs, fee_bps_per_side=costs.fee_bps_per_side*2,
                      slippage_bps_per_side=costs.slippage_bps_per_side*2)
    stresses = {
        "double_costs": scorecard(trades(prices, valid_end, len(prices), f, s, doubled)),
        "one_extra_bar_delay": scorecard(trades(prices, valid_end, len(prices), f, s, costs, delay=2))
    }
    # Illustrative accept/reject gate. Never promote to live or treat as statistically significant.
    passed = (valid["trades"] >= config["min_trades_per_partition"] and
              holdout["trades"] >= config["min_trades_per_partition"] and
              all(x["expectancy_bps"] is not None and x["expectancy_bps"] > 0 for x in [valid, holdout, *stresses.values()]))
    return {"label": "SYNTHETIC RESEARCH DEMO — NOT ALPHA EVIDENCE", "manifest": manifest(prices, seed),
            "partition_signal_bars": {"train": [0, train_end], "validation": [train_end, valid_end], "holdout": [valid_end, len(prices)]},
            "selection_policy": "highest training expectancy; no validation/holdout tuning",
            "selected_hypothesis": winner,
            "train": scored[0][0], "validation": valid, "holdout": holdout,
            "stress_holdout": stresses,
            "gate": "DEMO_PASS_NOT_LIVE_AUTHORIZATION" if passed else "REJECT_OR_INCONCLUSIVE"}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
