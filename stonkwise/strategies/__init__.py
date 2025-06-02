"""
Trading strategies for backtesting with backtrader.
"""

# Import strategies so they can be accessed directly from the strategies package
from .simple import SimpleStrategy

__all__ = ["SimpleStrategy"]
