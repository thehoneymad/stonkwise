"""
Plotting module for stonkwise.

This module provides functionality for plotting historical price data
with various customization options.
"""

import datetime
import os
import pathlib
from typing import List, Optional

import backtrader as bt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from stonkwise.data_sources import get_yahoo_data


def plot_tickers(
    tickers: List[str],
    period: str = "day",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    input_file: Optional[str] = None,
    output_path: Optional[str] = None,
    show_ma: bool = False,
    show_trend: bool = False,
    show_zones: bool = False,
) -> None:
    """
    Plot historical price data for one or more tickers.

    Args:
        tickers: List of stock ticker symbols
        period: Time period ('day', 'week', or '4h')
        start_date: Start date for plotting (YYYY-MM-DD), defaults to 1 year ago
        end_date: End date for plotting (YYYY-MM-DD), defaults to today
        input_file: Path to input CSV or Parquet file (instead of Yahoo Finance)
        output_path: Path to save the plot (defaults to tmp directory)
        show_ma: Whether to show moving averages on the plot
        show_trend: Whether to show trend direction on the plot
        show_zones: Whether to show supply and demand zones on the plot
    """
    for ticker in tickers:
        print(f"\nPlotting {ticker}...")
        plot_ticker(
            ticker=ticker,
            period=period,
            start_date=start_date,
            end_date=end_date,
            input_file=input_file,
            output_path=output_path,
            show_ma=show_ma,
            show_trend=show_trend,
            show_zones=show_zones,
        )


def plot_ticker(
    ticker: str,
    period: str = "day",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    input_file: Optional[str] = None,
    output_path: Optional[str] = None,
    show_ma: bool = False,
    show_trend: bool = False,
    show_zones: bool = False,
) -> None:
    """
    Plot historical price data for a single ticker.

    Args:
        ticker: Stock ticker symbol
        period: Time period ('day', 'week', or '4h')
        start_date: Start date for plotting (YYYY-MM-DD), defaults to 1 year ago
        end_date: End date for plotting (YYYY-MM-DD), defaults to today
        input_file: Path to input CSV or Parquet file (instead of Yahoo Finance)
        output_path: Path to save the plot (defaults to tmp directory)
        show_ma: Whether to show moving averages on the plot
        show_trend: Whether to show trend direction on the plot
        show_zones: Whether to show supply and demand zones on the plot
    """
    # Set default dates if not provided
    if start_date is None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
    if end_date is None:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Get data from file or Yahoo Finance
    if input_file:
        # Determine file type from extension
        if input_file.endswith(".csv"):
            data = load_csv_data(input_file)
        elif input_file.endswith(".parquet"):
            data = load_parquet_data(input_file)
        else:
            raise ValueError(f"Unsupported file format: {input_file}")
    else:
        # Get data from Yahoo Finance
        data = get_yahoo_data(ticker, start_date, end_date, period)

    # Add the data to cerebro
    cerebro.adddata(data)

    # Add moving average indicators if requested
    if show_ma:
        # Add SMA indicators with different periods and colors
        sma50 = bt.indicators.SimpleMovingAverage(
            data,
            period=50,
            plotname="SMA(50)",
        )
        sma50.plotlines.sma.color = "blue"

        sma100 = bt.indicators.SimpleMovingAverage(
            data,
            period=100,
            plotname="SMA(100)",
        )
        sma100.plotlines.sma.color = "orange"

        sma200 = bt.indicators.SimpleMovingAverage(
            data,
            period=200,
            plotname="SMA(200)",
        )
        sma200.plotlines.sma.color = "red"

    # Get the data as a pandas DataFrame for market structure analysis
    df = None
    if show_trend or show_zones:
        # Run cerebro once to load the data
        cerebro.run()

        # Convert data to pandas DataFrame
        df = pd.DataFrame()
        df["Open"] = np.array(data.open)
        df["High"] = np.array(data.high)
        df["Low"] = np.array(data.low)
        df["Close"] = np.array(data.close)
        df["Volume"] = np.array(data.volume)
        df.index = pd.to_datetime([data.num2date(x) for x in data.datetime])

    # Add trend detection if requested
    trend = None
    if show_trend and df is not None:
        # Import here to avoid circular imports
        from stonkwise.market_structure import MarketStructureDetector

        # Create a detector and analyze the data
        detector = MarketStructureDetector()
        trend = detector.detect_structure(df)

        print(f"Detected market structure: {trend.value}")

    # Add supply/demand zones if requested
    zones = None
    if show_zones and df is not None:
        # Import here to avoid circular imports
        from stonkwise.market_structure import MarketStructureDetector

        # Create a detector and analyze the data
        detector = MarketStructureDetector()
        if trend is None:
            detector.detect_structure(df)
        zones = detector.get_supply_demand_zones(df)

        print(f"Detected {len(zones['supply'])} supply zones and {len(zones['demand'])} demand zones")

    # Run the backtest (required for plotting)
    cerebro.run()

    # Create and save the plot
    plot_path = create_plot(
        cerebro=cerebro,
        ticker=ticker,
        period=period,
        strategy="analysis",
        output_path=output_path,
        zones=zones,
    )

    print(f"Plot saved to: {plot_path}")


def create_plot(
    cerebro: bt.Cerebro,
    ticker: str,
    period: str,
    strategy: str = "analysis",
    output_path: Optional[str] = None,
    show_ma: bool = False,
    show_trend: bool = False,
    show_zones: bool = False,
    zones: Optional[dict] = None,
) -> str:
    """
    Create and save a plot from a cerebro instance.

    Args:
        cerebro: Backtrader cerebro instance
        ticker: Stock ticker symbol
        period: Time period ('day', 'week', or '4h')
        strategy: Strategy name for the filename
        output_path: Path to save the plot (defaults to tmp directory)
        show_ma: Whether to show moving averages on the plot
        show_trend: Whether to show trend direction on the plot
        show_zones: Whether to show supply and demand zones on the plot
        zones: Supply and demand zones to plot

    Returns:
        Path to the saved plot
    """
    # Plot the result without blocking
    # Set show=False to prevent the plot from blocking execution
    # Use style='bar' to ensure proper coloring of up/down days
    fig = cerebro.plot(
        style="bar",
        barup="green",
        bardown="red",
        volup="green",
        voldown="red",
        show=False,
    )[
        0
    ][0]

    # TODO: Add visualization of zones if provided
    if zones:
        # This would require more complex matplotlib manipulation
        # which we'll implement in a future update
        pass

    # Determine output path for the plot
    if output_path is None:
        # Save to a file in the tmp directory
        project_root = pathlib.Path(__file__).parent.parent.parent
        tmp_dir = project_root / "tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        plot_path = tmp_dir / f"{ticker}_{period}_{strategy}_{timestamp}_plot.png"
    else:
        # Use the provided output path for the plot
        plot_path = pathlib.Path(output_path)

        # If it's a directory, create a file name
        if plot_path.is_dir():
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            plot_path = plot_path / f"{ticker}_{period}_{strategy}_{timestamp}_plot.png"

    # Save the plot
    fig.savefig(plot_path)

    # Close the figure to free up memory
    plt.close(fig)

    return str(plot_path)


def load_csv_data(file_path: str) -> bt.feeds.GenericCSVData:
    """
    Load data from a CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        backtrader data feed object
    """
    # TODO: Implement CSV loading with proper column detection
    # For now, we'll assume a standard format
    return bt.feeds.GenericCSVData(
        dataname=file_path,
        dtformat="%Y-%m-%d",
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
    )


def load_parquet_data(file_path: str) -> bt.feeds.PandasData:
    """
    Load data from a Parquet file.

    Args:
        file_path: Path to the Parquet file

    Returns:
        backtrader data feed object
    """
    # Load the parquet file into a pandas DataFrame
    df = pd.read_parquet(file_path)

    # Create a backtrader data feed from the DataFrame
    return bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # Use the index as datetime
        open="Open",
        high="High",
        low="Low",
        close="Close",
        volume="Volume",
        openinterest=-1,  # No open interest data
    )
