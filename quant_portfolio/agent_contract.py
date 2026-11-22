"""Guard the boundary between agent suggestions and deterministic research."""
import json

ALLOWED_KEYS = {"fast", "slow", "hypothesis"}

def parse_proposal(payload):
    obj = json.loads(payload) if isinstance(payload, str) else payload
    if not isinstance(obj, dict) or set(obj) != ALLOWED_KEYS:
        raise ValueError("Proposal must have exactly fast, slow, hypothesis")
    if type(obj["fast"]) is not int or type(obj["slow"]) is not int:
        raise ValueError("Moving average windows must be integers")
    if not 2 <= obj["fast"] < obj["slow"] <= 100:
        raise ValueError("Proposal outside the pre-registered parameter space")
    if not isinstance(obj["hypothesis"], str) or not 12 <= len(obj["hypothesis"].strip()) <= 300:
        raise ValueError("Hypothesis must be explanatory and bounded")
    return obj
