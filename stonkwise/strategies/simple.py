"""
A simple trading strategy for learning purposes.
"""

from typing import Optional

import backtrader as bt


class SimpleStrategy(bt.Strategy):
    """
    A simple trading strategy that demonstrates the basic structure of a backtrader
    strategy.

    This strategy is meant as a learning example and doesn't implement any specific
    trading logic yet. It simply prints the closing price of the asset each day.
    """

    def __init__(self) -> None:
        """Initialize the strategy."""
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def log(self, txt: str, dt: Optional[bt.datetime.date] = None) -> None:
        """Logging function for the strategy."""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def next(self) -> None:
        """
        Define what will be done in each iteration when new data arrives.

        This method is called for each bar of data and is where the main
        trading logic should be implemented.
        """
        # Simply log the closing price of the series
        self.log(f"Close: {self.dataclose[0]:.2f}")

        # Here is where you would implement your trading logic
        # For example, checking indicators, placing orders, etc.
