"""
Main analyzer module for stonkwise.
"""

import datetime
from typing import List, Optional

import backtrader as bt

from stonkwise.data_sources import get_yahoo_data
from stonkwise.strategies import SimpleStrategy


def analyze_ticker(
    ticker: str,
    period: str = "day",
    strategy: str = "simple",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> None:
    """
    Analyze a stock ticker using the specified strategy and period.

    Args:
        ticker: Stock ticker symbol (e.g., 'MSFT')
        period: Time period ('day', 'week', or '4h')
        strategy: Trading strategy to apply
        start_date: Start date for analysis (YYYY-MM-DD), defaults to 1 year ago
        end_date: End date for analysis (YYYY-MM-DD), defaults to today
    """
    # Set default dates if not provided
    if start_date is None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime(
            "%Y-%m-%d"
        )
    if end_date is None:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add the strategy
    if strategy == "simple":
        cerebro.addstrategy(SimpleStrategy)
    else:
        # Default to SimpleStrategy for now
        cerebro.addstrategy(SimpleStrategy)

    # Get and add the data
    data = get_yahoo_data(ticker, start_date, end_date, period)
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Print out the starting conditions
    print(f"Starting Portfolio Value: ${cerebro.broker.getvalue():.2f}")

    # Run the backtest
    cerebro.run()

    # Print out the final result
    print(f"Final Portfolio Value: ${cerebro.broker.getvalue():.2f}")

    # Plot the result
    cerebro.plot(style="candlestick")


def analyze_tickers(
    tickers: List[str],
    period: str = "day",
    strategy: str = "simple",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> None:
    """
    Analyze multiple stock tickers.

    Args:
        tickers: List of stock ticker symbols
        period: Time period ('day', 'week', or '4h')
        strategy: Trading strategy to apply
        start_date: Start date for analysis (YYYY-MM-DD), defaults to 1 year ago
        end_date: End date for analysis (YYYY-MM-DD), defaults to today
    """
    for ticker in tickers:
        print(f"\nAnalyzing {ticker}...")
        analyze_ticker(ticker, period, strategy, start_date, end_date)
