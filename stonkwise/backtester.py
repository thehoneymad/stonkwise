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
import numpy as np
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
        show_ma: Whether to show moving averages on the plot
        show_trend: Whether to show trend direction on the plot
        show_zones: Whether to show supply and demand zones on the plot
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
            show_ma=show_ma,
            show_trend=show_trend,
            show_zones=show_zones,
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
        show_ma: Whether to show moving averages on the plot
        show_trend: Whether to show trend direction on the plot
        show_zones: Whether to show supply and demand zones on the plot
        
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
        # Import here to avoid circular imports
        from stonkwise.plotter import load_csv_data, load_parquet_data
        
        # Determine file type from extension
        if input_file.endswith('.csv'):
            data = load_csv_data(input_file)
        elif input_file.endswith('.parquet'):
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
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # Add market structure detection if requested
    trend = None
    zones = None
    if show_trend or show_zones:
        # Run cerebro once to load the data
        cerebro.run()
        cerebro = bt.Cerebro()  # Create a new cerebro instance
        cerebro.adddata(data)   # Re-add the data
        
        if strategy == "simple":
            cerebro.addstrategy(SimpleStrategy)
        elif strategy == "ma_cross":
            cerebro.addstrategy(SimpleStrategy)
        elif strategy == "price_action":
            cerebro.addstrategy(SimpleStrategy)
        else:
            cerebro.addstrategy(SimpleStrategy)
        
        cerebro.broker.setcash(initial_cash)
        cerebro.broker.setcommission(commission=commission)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        # Import here to avoid circular imports
        from stonkwise.market_structure import MarketStructureDetector
        
        # Create a detector and analyze the data
        detector = MarketStructureDetector()
        
        # Get the data as a pandas DataFrame for market structure analysis
        df = pd.DataFrame()
        df['Open'] = np.array(data.open)
        df['High'] = np.array(data.high)
        df['Low'] = np.array(data.low)
        df['Close'] = np.array(data.close)
        df['Volume'] = np.array(data.volume)
        df.index = pd.to_datetime([data.num2date(x) for x in data.datetime])
        
        if show_trend:
            trend = detector.detect_structure(df)
            print(f"Detected market structure: {trend.value}")
        
        if show_zones:
            if trend is None:
                detector.detect_structure(df)
            zones = detector.get_supply_demand_zones(df)
            print(f"Detected {len(zones['supply'])} supply zones and {len(zones['demand'])} demand zones")
    
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
    total_trades = trades.get('total', {}).get('total', 0)
    won_trades = trades.get('won', {}).get('total', 0)
    lost_trades = trades.get('lost', {}).get('total', 0)
    win_rate = won_trades / total_trades if total_trades > 0 else 0.0
    
    print(f"Total Trades: {total_trades}")
    print(f"Won Trades: {won_trades}")
    print(f"Lost Trades: {lost_trades}")
    print(f"Win Rate: {win_rate:.2%}")
    
    # Plot the result using the plotter module
    from stonkwise.plotter import create_plot
    
    # Create and save the plot
    plot_path = create_plot(
        cerebro=cerebro,
        ticker=ticker,
        period=period,
        strategy=strategy,
        output_path=output_path,
        zones=zones
    )
    
    print(f"Plot saved to: {plot_path}")
    
    # Prepare results dictionary
    results_dict = {
        'initial_value': initial_cash,
        'final_value': final_value,
        'total_return': returns.get('rtot', 0.0),
        'annual_return': returns.get('rnorm', 0.0),
        'sharpe_ratio': sharpe.get('sharperatio', 0.0),
        'max_drawdown': drawdown.get('max', {}).get('drawdown', 0.0),
        'total_trades': total_trades,
        'won_trades': won_trades,
        'lost_trades': lost_trades,
        'win_rate': win_rate,
    }
    
    # Export results to CSV if output_path is provided
    if output_path:
        export_results(results_dict, ticker, strategy, output_path)
    
    return results_dict


def export_results(
    results: Dict[str, Union[float, int]],
    ticker: str,
    strategy: str,
    output_path: str
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
    df['ticker'] = ticker
    df['strategy'] = strategy
    df['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save to CSV
    df.to_csv(path, index=False)
    print(f"Results exported to: {path}")
