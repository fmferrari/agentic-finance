"""Reproducible synthetic closing prices; not genuine market observations."""
import hashlib
import json
import math
import random

def synthetic_prices(n=900, seed=42):
    if n < 50:
        raise ValueError("n must be at least 50")
    rng = random.Random(seed)
    price = 100.0
    prices = [price]
    for i in range(n - 1):
        # Artificial regime shifts. These are not calibrated to real markets.
        drift = (0.0003 if (i // 150) % 3 == 0 else (-0.0002 if (i // 150) % 3 == 1 else 0))
        volatility = 0.007 if (i // 120) % 2 == 0 else 0.017
        price *= math.exp(drift + rng.gauss(0, volatility))
        prices.append(round(price, 10))
    return prices

def manifest(prices, seed=42):
    raw = json.dumps(prices, separators=(",", ":"), ensure_ascii=True)
    return {"source": "synthetic", "seed": seed, "observations": len(prices),
            "sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "real_market_data": False}
