
from decimal import Decimal, ROUND_CEILING

# Demo rates, expressed in micro-USD ($0.000001 units).
# These are project rates, not claims about a real AI provider.
PRICING_VERSION = "demo-v1"

API_CALL_COST_MICRO_USD = 100
INPUT_COST_PER_MILLION_MICRO_USD = 2_000_000
CACHED_INPUT_COST_PER_MILLION_MICRO_USD = 200_000
OUTPUT_COST_PER_MILLION_MICRO_USD = 8_000_000


def calculate_token_cost(
    input_tokens: int,
    cached_input_tokens: int = 0,
    output_tokens: int = 0,
) -> int:
    """Return token cost in whole micro-USD units.

    cached_input_tokens are a subset of input_tokens.
    output_tokens must already include reasoning tokens.
    """
    if min(input_tokens, cached_input_tokens, output_tokens) < 0:
        raise ValueError("Token quantities cannot be negative.")

    if cached_input_tokens > input_tokens:
        raise ValueError("Cached input cannot exceed total input tokens.")

    regular_input_tokens = input_tokens - cached_input_tokens

    cost = (
        Decimal(regular_input_tokens)
        * INPUT_COST_PER_MILLION_MICRO_USD
        / 1_000_000
        + Decimal(cached_input_tokens)
        * CACHED_INPUT_COST_PER_MILLION_MICRO_USD
        / 1_000_000
        + Decimal(output_tokens)
        * OUTPUT_COST_PER_MILLION_MICRO_USD
        / 1_000_000
    )

    return int(cost.to_integral_value(rounding=ROUND_CEILING))


def calculate_api_call_cost(quantity: int = 1) -> int:
    """Return API-call cost in whole micro-USD units."""
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    return quantity * API_CALL_COST_MICRO_USD
