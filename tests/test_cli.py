"""
Tests for the CLI module.
"""

import pytest
from stonkwise.cli import parse_args


def test_parse_args_analyze():
    """Test parsing analyze command arguments."""
    args = parse_args(["analyze", "--ticker", "MSFT", "--period", "day"])
    assert args.command == "analyze"
    assert args.ticker == ["MSFT"]
    assert args.period == "day"
    assert args.strategy == "simple"  # Default value


def test_parse_args_multiple_tickers():
    """Test parsing multiple ticker arguments."""
    args = parse_args(["analyze", "--ticker", "MSFT", "AAPL", "--period", "week"])
    assert args.command == "analyze"
    assert args.ticker == ["MSFT", "AAPL"]
    assert args.period == "week"


def test_parse_args_with_strategy():
    """Test parsing with a specified strategy."""
    args = parse_args(["analyze", "--ticker", "MSFT", "--strategy", "custom"])
    assert args.command == "analyze"
    assert args.ticker == ["MSFT"]
    assert args.strategy == "custom"
