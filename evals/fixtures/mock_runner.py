#!/usr/bin/env python3
"""Deterministic protocol smoke runner; it does not measure skill quality."""

import json
import sys


job = json.load(sys.stdin)
print(json.dumps({
    "outcome": "protocol-smoke-pass",
    "response": f"accepted {job['case']['id']} under condition {job['condition']}",
    "tool_calls": [],
    "metrics": {"input_tokens": 0, "output_tokens": 0},
}))
