#!/usr/bin/env python3
"""
Command line interface for stonkwise - a tool for learning technical trading.

This module provides a CLI built with Click for analyzing and backtesting
trading strategies on historical price data.
"""

from typing import Optional, Tuple

import click


# Define common options as function decorators to avoid repetition
def ticker_option(required=True):
    return click.option(
        "--ticker",
        "-t",
        multiple=True,
        required=required,
        help="Stock ticker symbol(s) (e.g., MSFT, AMZN)",
    )


def period_option():
    return click.option(
        "--period",
        "-p",
        type=click.Choice(["day", "week", "4h"]),
        default="day",
        help="Time period for analysis (day, week, or 4 hours)",
    )


def date_options():
    def decorator(f):
        f = click.option(
            "--start-date",
            help="Start date for analysis (YYYY-MM-DD), defaults to 1 year ago",
        )(f)
        f = click.option(
            "--end-date", help="End date for analysis (YYYY-MM-DD), defaults to today"
        )(f)
        return f

    return decorator


def input_output_options():
    def decorator(f):
        f = click.option(
            "--input-file",
            type=click.Path(exists=True, readable=True),
            help="Path to input CSV or Parquet file (instead of Yahoo Finance)",
        )(f)
        f = click.option(
            "--output",
            type=click.Path(writable=True),
            help="Path to save the output (defaults to tmp directory)",
        )(f)
        return f

    return decorator


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Stonkwise: A tool for learning technical trading analysis.

    This CLI provides commands for analyzing and backtesting
    trading strategies on historical price data.
    """


@cli.command()
@ticker_option()
@period_option()
@click.option(
    "--strategy",
    "-s",
    default="simple",
    type=click.Choice(["simple", "ma_cross", "price_action"]),
    help="Trading strategy to apply",
)
@date_options()
@input_output_options()
@click.option("--backtest/--no-backtest", default=False, help="Enable backtesting mode")
@click.option(
    "--cash",
    type=float,
    default=10000.0,
    help="Initial cash for backtesting (default: 10000)",
)
@click.option(
    "--commission",
    type=float,
    default=0.001,
    help="Commission rate for trades (default: 0.001 = 0.1%)",
)
@click.option(
    "--show-ma/--no-ma", default=False, help="Show moving averages on the plot"
)
@click.option(
    "--show-trend/--no-trend", default=False, help="Show trend direction on the plot"
)
@click.option(
    "--show-zones/--no-zones",
    default=False,
    help="Show supply and demand zones on the plot",
)
def analyze(
    ticker: Tuple[str],
    period: str,
    strategy: str,
    start_date: Optional[str],
    end_date: Optional[str],
    input_file: Optional[str],
    output: Optional[str],
    backtest: bool,
    cash: float,
    commission: float,
    show_ma: bool,
    show_trend: bool,
    show_zones: bool,
):
    """
    Analyze stock tickers and optionally run backtests.

    This command provides a unified interface for analyzing price data,
    visualizing charts, and running backtests with various strategies.
    """
    if backtest:
        click.echo(
            f"Analyzing and backtesting {', '.join(ticker)} with {period} period using {strategy} strategy"
        )
    else:
        click.echo(
            f"Analyzing {', '.join(ticker)} with {period} period using {strategy} strategy"
        )

    try:
        # Import here to avoid circular imports
        if backtest:
            from stonkwise.backtester import backtest_tickers

            backtest_tickers(
                tickers=list(ticker),
                period=period,
                strategy=strategy,
                start_date=start_date,
                end_date=end_date,
                input_file=input_file,
                output_path=output,
                initial_cash=cash,
                commission=commission,
                show_ma=show_ma,
                show_trend=show_trend,
                show_zones=show_zones,
            )
        else:
            from stonkwise.plotter import plot_tickers

            plot_tickers(
                tickers=list(ticker),
                period=period,
                start_date=start_date,
                end_date=end_date,
                input_file=input_file,
                output_path=output,
                show_ma=show_ma,
                show_trend=show_trend,
                show_zones=show_zones,
            )
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        return 1

    return 0


def main():
    """Entry point for the CLI."""
    return cli()
