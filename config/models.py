"""LLM model aliases and metadata.

All model IDs are defined here. Never hardcode model strings elsewhere —
always import from this module so version changes happen in one place.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInfo:
    id: str
    input_cost_per_1m: float   # USD
    output_cost_per_1m: float  # USD
    context_window: int        # tokens
    supports_thinking: bool


# ─── Current models ───────────────────────────────────────────────────────────

OPUS = ModelInfo(
    id="claude-opus-4-6",
    input_cost_per_1m=5.00,
    output_cost_per_1m=25.00,
    context_window=200_000,
    supports_thinking=True,
)

SONNET = ModelInfo(
    id="claude-sonnet-4-6",
    input_cost_per_1m=3.00,
    output_cost_per_1m=15.00,
    context_window=200_000,
    supports_thinking=True,
)

HAIKU = ModelInfo(
    id="claude-haiku-4-5",
    input_cost_per_1m=1.00,
    output_cost_per_1m=5.00,
    context_window=200_000,
    supports_thinking=False,
)

# Default for agents — change here to affect all agents unless overridden
DEFAULT_MODEL = OPUS

# Use for high-volume, latency-sensitive tasks where cost matters
FAST_MODEL = HAIKU
