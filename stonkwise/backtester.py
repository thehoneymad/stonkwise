"""
Backtesting module for stonkwise.

This module provides functionality for backtesting trading strategies
on historical price data.
"""

import datetime
import os
import pathlib
from typing import Dict, List, Optional, Union

import backtrader as bt
import matplotlib.pyplot as plt
import pandas as pd

from stonkwise.data_sources import get_yahoo_data
from stonkwise.strategies import SimpleStrategy


def backtest_tickers(
    tickers: List[str],
    period: str = "day",
    strategy: str = "simple",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    input_file: Optional[str] = None,
    output_path: Optional[str] = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
    show_ma: bool = False,
    show_trend: bool = False,
    show_zones: bool = False,
) -> None:
    """
    Backtest trading strategies on multiple tickers.

    Args:
        tickers: List of stock ticker symbols
        period: Time period ('day', 'week', or '4h')
        strategy: Trading strategy to apply
        start_date: Start date for backtesting (YYYY-MM-DD), defaults to 1 year ago
        end_date: End date for backtesting (YYYY-MM-DD), defaults to today
        input_file: Path to input CSV or Parquet file (instead of Yahoo Finance)
        output_path: Path to save the backtest results (defaults to tmp directory)
        initial_cash: Initial cash for backtesting
        commission: Commission rate for trades
    """
    for ticker in tickers:
        print(f"\nBacktesting {ticker}...")
        backtest_ticker(
            ticker=ticker,
            period=period,
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            input_file=input_file,
            output_path=output_path,
            initial_cash=initial_cash,
            commission=commission,
        )


def backtest_ticker(
    ticker: str,
    period: str = "day",
    strategy: str = "simple",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    input_file: Optional[str] = None,
    output_path: Optional[str] = None,
    initial_cash: float = 10000.0,
    commission: float = 0.001,
    show_ma: bool = False,
    show_trend: bool = False,
    show_zones: bool = False,
) -> Dict[str, Union[float, int]]:
    """
    Backtest a trading strategy on a single ticker.

    Args:
        ticker: Stock ticker symbol
        period: Time period ('day', 'week', or '4h')
        strategy: Trading strategy to apply
        start_date: Start date for backtesting (YYYY-MM-DD), defaults to 1 year ago
        end_date: End date for backtesting (YYYY-MM-DD), defaults to today
        input_file: Path to input CSV or Parquet file (instead of Yahoo Finance)
        output_path: Path to save the backtest results (defaults to tmp directory)
        initial_cash: Initial cash for backtesting
        commission: Commission rate for trades

    Returns:
        Dictionary with backtest results
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
    elif strategy == "ma_cross":
        # This will be implemented later
        cerebro.addstrategy(SimpleStrategy)
    elif strategy == "price_action":
        # This will be implemented as part of Issue #4
        cerebro.addstrategy(SimpleStrategy)
    else:
        # Default to SimpleStrategy
        cerebro.addstrategy(SimpleStrategy)

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

    # Set our desired cash start
    cerebro.broker.setcash(initial_cash)

    # Set the commission
    cerebro.broker.setcommission(commission=commission)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

    # Add market structure detection if requested
    if show_trend or show_zones:
        # Import here to avoid circular imports
        from stonkwise.market_structure import MarketStructureDetector

        # Create a detector and analyze the data
        detector = MarketStructureDetector()

        if show_trend:
            trend = detector.detect_structure(data.dataname)
            print(f"Detected market structure: {trend.value}")

        if show_zones:
            detector.detect_structure(data.dataname)
            zones = detector.get_supply_demand_zones(data.dataname)
            print(
                f"Detected {len(zones['supply'])} supply zones and {len(zones['demand'])} demand zones"
            )

    # Print out the starting conditions
    print(f"Starting Portfolio Value: ${cerebro.broker.getvalue():.2f}")
    print(f"Commission: {commission:.3%}")

    # Run the backtest
    results = cerebro.run()

    # Get the final portfolio value
    final_value = cerebro.broker.getvalue()
    print(f"Final Portfolio Value: ${final_value:.2f}")

    # Get the analyzers results
    strat = results[0]
    sharpe = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    returns = strat.analyzers.returns.get_analysis()
    trades = strat.analyzers.trades.get_analysis()

    # Print the results
    print("\nBacktest Results:")
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 0.0):.3f}")
    print(f"Max Drawdown: {drawdown.get('max', {}).get('drawdown', 0.0):.2%}")
    print(f"Total Return: {returns.get('rtot', 0.0):.2%}")
    print(f"Annual Return: {returns.get('rnorm', 0.0):.2%}")

    # Print trade statistics
    total_trades = trades.get("total", {}).get("total", 0)
    won_trades = trades.get("won", {}).get("total", 0)
    lost_trades = trades.get("lost", {}).get("total", 0)
    win_rate = won_trades / total_trades if total_trades > 0 else 0.0

    print(f"Total Trades: {total_trades}")
    print(f"Won Trades: {won_trades}")
    print(f"Lost Trades: {lost_trades}")
    print(f"Win Rate: {win_rate:.2%}")

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
    )[0][0]

    # Determine output path for the plot
    if output_path is None:
        # Save to a file in the tmp directory
        project_root = pathlib.Path(__file__).parent.parent.parent
        tmp_dir = project_root / "tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        plot_path = tmp_dir / f"{ticker}_{period}_{strategy}_{timestamp}_backtest.png"
    else:
        # Use the provided output path for the plot
        plot_path = pathlib.Path(output_path)

        # If it's a directory, create a file name
        if plot_path.is_dir():
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            plot_path = (
                plot_path / f"{ticker}_{period}_{strategy}_{timestamp}_backtest.png"
            )

    # Save the plot
    fig.savefig(plot_path)
    print(f"Plot saved to: {plot_path}")

    # Close the figure to free up memory
    plt.close(fig)

    # Prepare results dictionary
    results_dict = {
        "initial_value": initial_cash,
        "final_value": final_value,
        "total_return": returns.get("rtot", 0.0),
        "annual_return": returns.get("rnorm", 0.0),
        "sharpe_ratio": sharpe.get("sharperatio", 0.0),
        "max_drawdown": drawdown.get("max", {}).get("drawdown", 0.0),
        "total_trades": total_trades,
        "won_trades": won_trades,
        "lost_trades": lost_trades,
        "win_rate": win_rate,
    }

    # Export results to CSV if output_path is provided
    if output_path:
        export_results(results_dict, ticker, strategy, output_path)

    return results_dict


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


def export_results(
    results: Dict[str, Union[float, int]], ticker: str, strategy: str, output_path: str
) -> None:
    """
    Export backtest results to a file.

    Args:
        results: Dictionary with backtest results
        ticker: Stock ticker symbol
        strategy: Trading strategy used
        output_path: Path to save the results
    """
    # Convert the output_path to a Path object
    path = pathlib.Path(output_path)

    # If it's a directory, create a file name
    if path.is_dir():
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        path = path / f"{ticker}_{strategy}_{timestamp}_results.csv"

    # Create a DataFrame from the results
    df = pd.DataFrame([results])

    # Add ticker and strategy columns
    df["ticker"] = ticker
    df["strategy"] = strategy
    df["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    df.to_csv(path, index=False)
    print(f"Results exported to: {path}")
