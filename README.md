# Agentic Quant Research — Evidence-First Demonstrator

**A public-safe, independently written portfolio example by Felipe Ferrari.**

This is a self-contained Python demonstration of a workflow inspired by lessons from my private projects, **Quant Swarm** and **Intraday Desk**. It is **not** a copy, fork, code export or performance report from those projects. It uses only seeded synthetic price observations, no private datasets, keys, agents, brokers or live capital.

## Why this exists

An LLM can suggest a plausible trading strategy. A useful research system must force that suggestion through a deterministic, inspectable contract: hypothesis -> bounded parameters -> frozen partitions -> causal signal -> conservative costs -> stress -> pass/fail, with clear limits on what the evidence establishes.

## Quick start

```bash
python3 -m unittest discover -s tests -v
python3 -m quant_portfolio > experiment.json
```

Python 3.11+; standard library only. No account, API key, network call or external dependency.

## Demonstrated concepts

| Boundary | What the demo implements | What it does NOT claim |
| --- | --- | --- |
| Agent output | Strict JSON contract rejecting unknown keys and invalid parameters | No actual LLM model orchestration or RL training |
| Market data | Deterministic seeded synthetic series, SHA-256 manifest | No real market provenance, ingestion or forecasting performance |
| Research | Training-only selection from a fixed preregistered candidate set | No statistically valid discovery from these toy prices |
| Validation | Chronological train/validation/holdout, delayed entries, partitions with no cross-boundary exits | No formal purged walk-forward protocol or multiple-testing correction |
| Costs | Explicit two-sided fees and slippage; doubling-cost stress | No order book, queue modelling or realistic fill simulation |
| Safety | Pre-trade stop-derived position sizing, fail-closed examples | Stops are **not executed** in backtest and no broker orders exist |
| Decision | Reject/inconclusive vs illustrative demo-pass; never enables orders | No production readiness, investment advice or proven alpha |

**Timing convention:** signal calculated at the end of close `t` from historical closes at or before `t`. Illustrative entry at close `t+1`, exit at close `t+2`; two-sided costs charged. This intentionally incurs a full-bar delay. Returns are synthetic and a `net_r_proxy` is only a fixed-risk normalization, **not actual realized R**. Trade records are simplified independent one-bar simulations.

## Background and scope

This independently written demo draws on lessons from Quant Swarm and Intraday Desk, two separate, agent-assisted research projects. It does not reproduce their private code or data, and it is not evidence of live trading performance.

## Recruiter tour (2 minutes)

1. Read `config/research_protocol.json`: the candidate space and costs are defined before the test.
2. Read `quant_portfolio/agent_contract.py`: untrusted model output cannot change research constraints.
3. Read `quant_portfolio/backtest.py`: signals precede entry; exits remain inside a partition; both-side costs.
4. Run the experiment and observe that a **rejection is a successful safety outcome**, not a failed software demo.
5. Run tests including look-ahead resistance, cost stress, invalid agent payloads, risk sizing and reproducibility.

For possible enhancements, see `docs/NEXT_STEPS.md`.
