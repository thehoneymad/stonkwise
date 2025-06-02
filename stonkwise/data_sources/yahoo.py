"""
Yahoo Finance data source for fetching stock data.
"""

import datetime
import os
import pathlib
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
        This function uses the yfinance package to download data from Yahoo Finance
        and then creates a backtrader data feed from it. The data is temporarily
        stored in the project's tmp directory and will be cleaned up as part of
        the build artifacts.
    """
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    if end_date is None:
        end_date = datetime.datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # Try using bt.feeds.YahooFinanceData first
    try:
        # Map period to Yahoo Finance timeframe
        timeframe_map = {
            "day": bt.TimeFrame.Days,
            "week": bt.TimeFrame.Weeks,
            "4h": bt.TimeFrame.Minutes,  # Will need special handling
        }

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
        
    except Exception as e:
        print(f"Warning: Built-in YahooFinanceData failed: {e}")
        print("Falling back to yfinance package...")
        
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
        
        # Ensure tmp directory exists
        project_root = pathlib.Path(__file__).parent.parent.parent
        tmp_dir = project_root / "tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        
        # Save to a temporary CSV file in the project's tmp directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        temp_file = tmp_dir / f"{ticker}_{period}_{timestamp}.csv"
        data_df.to_csv(temp_file)
        
        # Create a backtrader data feed from the CSV file
        data = bt.feeds.GenericCSVData(
            dataname=str(temp_file),
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
