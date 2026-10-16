
import pytest

from app.services.pricing import (
    calculate_api_call_cost,
    calculate_token_cost,
)


def test_api_call_cost():
    assert calculate_api_call_cost(3) == 300


def test_cached_input_costs_less():
    regular = calculate_token_cost(input_tokens=1000)
    cached = calculate_token_cost(
        input_tokens=1000,
        cached_input_tokens=1000,
    )
    assert cached < regular


def test_output_tokens_are_counted_once():
    assert calculate_token_cost(
        input_tokens=0,
        output_tokens=1000,
    ) == 8000


def test_cached_tokens_cannot_exceed_total_input():
    with pytest.raises(ValueError):
        calculate_token_cost(
            input_tokens=100,
            cached_input_tokens=101,
        )


def test_negative_tokens_are_rejected():
    with pytest.raises(ValueError):
        calculate_token_cost(input_tokens=-1)
