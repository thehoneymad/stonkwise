"""
Yahoo Finance data source for fetching stock data.
"""

import datetime
from typing import Optional, Union

import backtrader as bt


def get_yahoo_data(
    ticker: str,
    start_date: Union[str, datetime.datetime],
    end_date: Optional[Union[str, datetime.datetime]] = None,
    period: str = "day",
) -> bt.feeds.YahooFinanceData:
    """
    Get stock data from Yahoo Finance.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'MSFT')
        start_date: Start date for data (YYYY-MM-DD or datetime object)
        end_date: End date for data (YYYY-MM-DD or datetime object), defaults to today
        period: Time period ('day', 'week', or '4h')
        
    Returns:
        backtrader data feed object
        
    Notes:
        The Yahoo Finance data feed in backtrader connects to Yahoo Finance's API
        to download historical price data. It provides OHLCV (Open, High, Low, Close, Volume)
        data for stocks, ETFs, and other financial instruments. The data quality and
        availability depend on Yahoo Finance's service, which is free but may have
        limitations on request frequency and historical depth.
    """
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    
    if end_date is None:
        end_date = datetime.datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    # Map period to Yahoo Finance timeframe
    timeframe_map = {
        "day": bt.TimeFrame.Days,
        "week": bt.TimeFrame.Weeks,
        "4h": bt.TimeFrame.Minutes,  # Will need special handling
    }
    
    # The compression parameter defines how many base time units to combine into one data point
    # For example:
    # - compression=1 with timeframe=Days means each data point represents 1 day
    # - compression=7 with timeframe=Days would create weekly bars from daily data
    # - compression=240 with timeframe=Minutes creates 4-hour bars (240 minutes = 4 hours)
    # This allows for flexible time aggregation without needing separate data sources
    compression = 1
    timeframe = timeframe_map.get(period, bt.TimeFrame.Days)
    
    # Special case for 4h period
    if period == "4h":
        timeframe = bt.TimeFrame.Minutes
        compression = 240  # 4 hours = 240 minutes
    
    # Create and return the data feed
    data = bt.feeds.YahooFinanceData(
        dataname=ticker,
        fromdate=start_date,
        todate=end_date,
        timeframe=timeframe,
        compression=compression,
    )
    
    return data
