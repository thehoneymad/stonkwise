# stonkwise

A simple command line tool for learning technical trading analysis and visualization.

## Overview

stonkwise is a learning tool for technical trading that:
- Analyzes stock tickers (like MSFT, AMZN)
- Supports different time periods (day, week, 4 hours)
- Will include various trading strategies as you learn
- Visualizes results to help understand market patterns

## Installation

```bash
# Install using Poetry
poetry install
```

## Usage

```bash
# Basic usage
poetry run stonkwise analyze --ticker MSFT --period day

# Multiple tickers
poetry run stonkwise analyze --ticker MSFT AMZN GOOGL --period week

# Different time periods
poetry run stonkwise analyze --ticker AAPL --period 4h
```

## Development

This project uses Poetry for dependency management and task running:

```bash
# Format code
poetry run format

# Lint code
poetry run lint

# Run tests
poetry run test

# Clean build artifacts
poetry run clean

# Run an example analysis
poetry run example --ticker=MSFT --period=day
```

## Project Structure

```
stonkwise/
├── stonkwise/           # Main package code
│   ├── __init__.py
│   ├── analyzer.py      # Analysis functionality
│   ├── cli.py           # Command line interface
│   ├── data_sources/    # Data source modules
│   ├── strategies/      # Trading strategies
│   └── utils/           # Utility functions
├── tests/               # Test directory
└── poetry_scripts.py    # Script functions for Poetry commands
```

This is a learning project to explore:
- Technical analysis concepts
- Backtesting trading strategies
- Data visualization for financial markets
- Command line tool development in Python
