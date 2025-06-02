# stonkwise

A simple command line tool for learning technical trading analysis and visualization.

## Overview

stonkwise is a learning tool for technical trading that:
- Analyzes stock tickers (like MSFT, AMZN)
- Supports different time periods (day, week, 4 hours)
- Will include various trading strategies as you learn
- Visualizes results to help understand market patterns

## Usage

```bash
# Basic usage
stonkwise analyze --ticker MSFT --period day --strategy simple

# Multiple tickers
stonkwise analyze --ticker MSFT AMZN GOOGL --period week

# Different time periods
stonkwise analyze --ticker AAPL --period 4h
```

## Development

This is a learning project to explore:
- Technical analysis concepts
- Backtesting trading strategies
- Data visualization for financial markets
- Command line tool development in Python
