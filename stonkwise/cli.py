#!/usr/bin/env python3
"""
Command line interface for stonkwise - a tool for learning technical trading.
"""

import argparse
from typing import List, Optional

from stonkwise.analyzer import analyze_tickers


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="A tool for learning technical trading analysis"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze stock tickers")
    analyze_parser.add_argument(
        "--ticker",
        "-t",
        nargs="+",
        required=True,
        help="Stock ticker symbols (e.g., MSFT, AMZN)",
    )
    analyze_parser.add_argument(
        "--period",
        "-p",
        choices=["day", "week", "4h"],
        default="day",
        help="Time period for analysis (day, week, or 4 hours)",
    )
    analyze_parser.add_argument(
        "--strategy", "-s", default="simple", help="Trading strategy to apply"
    )
    analyze_parser.add_argument(
        "--start-date",
        help="Start date for analysis (YYYY-MM-DD), defaults to 1 year ago",
    )
    analyze_parser.add_argument(
        "--end-date", help="End date for analysis (YYYY-MM-DD), defaults to today"
    )

    return parser.parse_args(args)


def main() -> int:
    """Main entry point for the CLI."""
    args = parse_args()

    if args.command == "analyze":
        print(
            f"Analyzing {', '.join(args.ticker)} with {args.period} period "
            f"using {args.strategy} strategy"
        )

        try:
            analyze_tickers(
                tickers=args.ticker,
                period=args.period,
                strategy=args.strategy,
                start_date=args.start_date,
                end_date=args.end_date,
            )
            return 0
        except Exception as e:
            print(f"Error during analysis: {e}")
            return 1
    else:
        print("Please specify a command. Use --help for more information.")
        return 1
