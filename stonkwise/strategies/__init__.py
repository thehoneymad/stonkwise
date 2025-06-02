"""
Strategies module for stonkwise.

This module contains various trading strategies for the stonkwise platform.
"""

from stonkwise.strategies.price_action import PriceActionStrategy
from stonkwise.strategies.simple import SimpleStrategy

__all__ = ["SimpleStrategy", "PriceActionStrategy"]
