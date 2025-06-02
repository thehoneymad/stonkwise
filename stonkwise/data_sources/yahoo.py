"""
Yahoo Finance data source for fetching stock data.
"""

import datetime
from typing import Optional, Union

import backtrader as bt
import yfinance as yf


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
        to download historical price data.
        It provides OHLCV (Open, High, Low, Close, Volume)
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

    # Use yfinance to download data
    yf_period_map = {
        "day": "1d",
        "week": "1wk",
        "4h": "1h",  # We'll need to resample this
    }
    
    # Download data using yfinance
    data_df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval=yf_period_map.get(period, "1d"),
        auto_adjust=True
    )
    
    # Save to a temporary CSV file
    temp_file = f"/tmp/{ticker}_{period}_{datetime.datetime.now().timestamp()}.csv"
    data_df.to_csv(temp_file)
    
    # Create a backtrader data feed from the CSV file
    data = bt.feeds.GenericCSVData(
        dataname=temp_file,
        dtformat="%Y-%m-%d",
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
    )

    return data
