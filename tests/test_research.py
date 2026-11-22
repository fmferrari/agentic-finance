import json
import unittest
from quant_portfolio.dataset import synthetic_prices, manifest
from quant_portfolio.strategy import signal_at
from quant_portfolio.backtest import Assumptions, trades, scorecard
from quant_portfolio.agent_contract import parse_proposal
from quant_portfolio.risk import size_from_stop, RiskPolicy
from quant_portfolio.__main__ import run

class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.prices = synthetic_prices(200, 12)
    def test_deterministic_data(self):
        self.assertEqual(self.prices, synthetic_prices(200, 12))
        self.assertEqual(manifest(self.prices, 12)["sha256"], manifest(synthetic_prices(200, 12), 12)["sha256"])
    def test_causal_signal(self):
        t = 55
        mutated = self.prices[:]
        mutated[t+1:] = [p * 100 for p in mutated[t+1:]]
        self.assertEqual(signal_at(self.prices, t, 5, 20), signal_at(mutated, t, 5, 20))
    def test_no_cross_boundary_fills(self):
        records = trades(self.prices, 100, 150, 5, 20)
        self.assertTrue(records)
        self.assertTrue(all(100 <= r["signal_index"] < r["entry_index"] < r["exit_index"] < 150 for r in records))
    def test_cost_stress_is_monotone(self):
        base = scorecard(trades(self.prices, 100, 199, 5, 20, Assumptions(1,1)))
        expensive = scorecard(trades(self.prices, 100, 199, 5, 20, Assumptions(4,4)))
        self.assertGreater(base["expectancy_bps"], expensive["expectancy_bps"])
    def test_guard_rejects_invalid_agent_output(self):
        for bad in ['{"fast":5,"slow":20,"hypothesis":"valid enough text", "read_future":true}',
                    '{"fast":false,"slow":20,"hypothesis":"valid enough text"}',
                    '{"fast":80,"slow":20,"hypothesis":"valid enough text"}']:
            with self.assertRaises(ValueError): parse_proposal(bad)
    def test_stop_sizing_fails_closed(self):
        self.assertEqual(size_from_stop(100, 98, 1, RiskPolicy()), 25)
        for stop, side in [(101,1),(99,-1),(100,1)]:
            with self.assertRaises(ValueError): size_from_stop(100, stop, side)
    def test_nonfinite_inputs_fail_closed(self):
        for value in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                trades(self.prices, 100, 150, 5, 20, Assumptions(value, 1))
            with self.assertRaises(ValueError):
                size_from_stop(100, 98, 1, RiskPolicy(equity=value))

    def test_reproducible_report(self):
        self.assertEqual(run(), run())
        self.assertEqual(run()["manifest"]["source"], "synthetic")

if __name__ == "__main__": unittest.main()
