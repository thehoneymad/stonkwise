"""
A simple moving average crossover trading strategy.
"""

from typing import Dict, Optional

import backtrader as bt


class SimpleStrategy(bt.Strategy):
    """
    A simple moving average crossover strategy.

    This strategy uses three moving averages:
    - 50-day SMA (blue line)
    - 100-day SMA (orange line)
    - 200-day SMA (red line)

    Trading signals:
    - Buy when the 50-day SMA crosses above the 200-day SMA (golden cross)
    - Sell when the 50-day SMA crosses below the 200-day SMA (death cross)
    """

    params = (
        ("fast_period", 50),  # Fast moving average period (50-day)
        ("mid_period", 100),  # Middle moving average period (100-day)
        ("slow_period", 200),  # Slow moving average period (200-day)
    )

    def __init__(self) -> None:
        """Initialize the strategy with moving averages."""
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # Create the moving average indicators
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.dataclose,
            period=self.params.fast_period,
            plotname=f"SMA({self.params.fast_period})",
        )

        self.sma_mid = bt.indicators.SimpleMovingAverage(
            self.dataclose,
            period=self.params.mid_period,
            plotname=f"SMA({self.params.mid_period})",
        )

        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.dataclose,
            period=self.params.slow_period,
            plotname=f"SMA({self.params.slow_period})",
        )

        # Set the plotting colors for the indicators
        # This is done by setting the plotlines attributes
        self.sma_fast.plotlines.sma.color = "blue"
        self.sma_mid.plotlines.sma.color = "orange"
        self.sma_slow.plotlines.sma.color = "red"

        # Create a crossover indicator
        self.crossover = bt.indicators.CrossOver(
            self.sma_fast,
            self.sma_slow,
            plotname="Crossover",
        )

        # To keep track of pending orders
        self.order = None

        # To keep track of whether we are in the market
        self.in_market = False

    def log(self, txt: str, dt: Optional[bt.datetime.date] = None) -> None:
        """Logging function for the strategy."""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order: bt.Order) -> None:
        """
        Receive notifications for orders.

        This method is called when an order is submitted, accepted, completed, etc.
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - nothing to do
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED, Price: {order.executed.price:.2f}")
            elif order.issell():
                self.log(f"SELL EXECUTED, Price: {order.executed.price:.2f}")

            # Record the size & price of the execution
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Reset orders
        self.order = None

    def next(self) -> None:
        """
        Define what will be done in each iteration when new data arrives.

        This method is called for each bar of data and is where the main
        trading logic is implemented.
        """
        # Check if an order is pending - if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to ENTER

            # If the fast MA crosses above the slow MA
            if self.crossover > 0:  # Golden cross
                self.log(f"BUY SIGNAL (Golden Cross), Close: {self.dataclose[0]:.2f}")

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()
                self.in_market = True

        else:
            # We are already in the market, look for a signal to EXIT

            # If the fast MA crosses below the slow MA
            if self.crossover < 0:  # Death cross
                self.log(f"SELL SIGNAL (Death Cross), Close: {self.dataclose[0]:.2f}")

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
                self.in_market = False
