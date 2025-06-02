"""
Yahoo Finance data source for fetching stock data.

This module provides functionality to download historical price data from Yahoo Finance
using the yfinance package and convert it into a format that can be used by backtrader
for backtesting trading strategies.
"""

import datetime
import os
import pathlib
from typing import Optional, Union

import backtrader as bt
import pandas as pd
import yfinance as yf


def get_yahoo_data(
    ticker: str,
    start_date: Union[str, datetime.datetime],
    end_date: Optional[Union[str, datetime.datetime]] = None,
    period: str = "day",
) -> bt.feeds.GenericCSVData:
    """
    Get stock data from Yahoo Finance using yfinance package.

    This function downloads historical price data for a given ticker symbol from
    Yahoo Finance using the yfinance package. It then converts the data into a
    backtrader data feed that can be used for backtesting trading strategies.

    Args:
        ticker: Stock ticker symbol (e.g., 'MSFT', 'AAPL', 'GOOGL')
        start_date: Start date for data (YYYY-MM-DD string or datetime object)
        end_date: End date for data (YYYY-MM-DD string or datetime object)
                 If None, defaults to today's date
        period: Time period for the data. Options are:
                - 'day': Daily data (default)
                - 'week': Weekly data
                - '4h': 4-hour data (will be resampled from hourly data)

    Returns:
        backtrader data feed object that can be added to a Cerebro instance

    Notes:
        - The function handles both string and datetime objects for date parameters
        - For 4-hour data, it downloads hourly data and resamples it
        - The returned data feed can be directly used with backtrader's Cerebro engine
    """
    # Convert string dates to datetime objects if needed
    # This ensures consistent date handling regardless of input format
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

    if end_date is None:
        # Default to current date if end_date is not provided
        end_date = datetime.datetime.now()
    elif isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # Map our period values to yfinance interval parameter values
    # yfinance uses different terminology for time intervals
    yf_period_map = {
        "day": "1d",  # Daily data
        "week": "1wk",  # Weekly data
        "4h": "1h",  # For 4h, we'll download hourly and resample
    }

    # Get the appropriate interval value for yfinance
    interval = yf_period_map.get(period, "1d")  # Default to daily if unknown period

    # Download data using yfinance
    # The yfinance.download function fetches historical market data from Yahoo Finance
    print(f"Downloading {ticker} data from Yahoo Finance...")
    data_df = yf.download(
        ticker,  # The stock ticker symbol
        start=start_date,  # Start date for data
        end=end_date,  # End date for data
        interval=interval,  # Time interval between data points
        auto_adjust=True,  # Adjust all OHLC automatically (for splits, dividends)
    )

    # Handle 4h period by resampling if needed
    # If we requested 4-hour data, we need to resample from the hourly data
    if period == "4h" and len(data_df) > 0:
        print("Resampling hourly data to 4-hour intervals...")
        # Resample using pandas functionality
        # For each 4-hour period:
        # - Open: Use the first value in the period
        # - High: Use the maximum value in the period
        # - Low: Use the minimum value in the period
        # - Close: Use the last value in the period
        # - Volume: Sum all values in the period
        data_df = (
            data_df.resample("4H")
            .agg(
                {
                    "Open": "first",  # First price in the interval
                    "High": "max",  # Highest price in the interval
                    "Low": "min",  # Lowest price in the interval
                    "Close": "last",  # Last price in the interval
                    "Volume": "sum",  # Total volume in the interval
                }
            )
            .dropna()
        )  # Remove any rows with NaN values

    # Clean up the DataFrame to ensure it's in the right format for backtrader
    # Reset the multi-level column headers that yfinance sometimes returns
    if isinstance(data_df.columns, pd.MultiIndex):
        data_df.columns = data_df.columns.droplevel(0)

    # Ensure tmp directory exists for storing temporary CSV files
    project_root = pathlib.Path(__file__).parent.parent.parent
    tmp_dir = project_root / "tmp"
    os.makedirs(tmp_dir, exist_ok=True)

    # Save to a temporary CSV file in the project's tmp directory
    # This is needed because GenericCSVData requires a file path
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    temp_file = tmp_dir / f"{ticker}_{period}_{timestamp}.csv"

    # Save the DataFrame to CSV, ensuring the date index is included
    data_df.to_csv(temp_file)
    print(f"Data saved to temporary file: {temp_file}")

    # Create a backtrader data feed from the CSV file
    # bt.feeds.GenericCSVData creates a backtrader data feed from a CSV file
    data = bt.feeds.GenericCSVData(
        dataname=str(temp_file),  # Path to the CSV file
        dtformat="%Y-%m-%d",  # Format of date/time column
        datetime=0,  # Column index for date/time (0 = first column)
        open=1,  # Column index for Open price
        high=2,  # Column index for High price
        low=3,  # Column index for Low price
        close=4,  # Column index for Close price
        volume=5,  # Column index for Volume
        openinterest=-1,  # No open interest data available (-1 means not used)
    )

    # Return the backtrader data feed
    return data
