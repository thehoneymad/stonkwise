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
# Format code (removes unused imports, formats with black, sorts imports)
poetry run format

# Lint code (flake8 and mypy)
poetry run lint

# Run tests
poetry run test

# Clean build artifacts
poetry run clean

# Run an example analysis
poetry run example --ticker=MSFT --period=day

# Verify and build (format + lint + build)
poetry run verify
```

## Project Structure

```
stonkwise/              # Project root
├── stonkwise/          # Actual package code
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py
│   ├── cli.py
│   ├── data_sources/
│   │   ├── __init__.py
│   │   └── yahoo.py
│   ├── strategies/
│   │   ├── __init__.py
│   │   └── simple.py
│   └── utils/
│       ├── __init__.py
│       └── plotting.py
├── tests/              # Test directory
├── poetry_scripts.py   # Script functions for Poetry commands
└── pyproject.toml      # Project configuration
```

This is a learning project to explore:
- Technical analysis concepts
- Backtesting trading strategies
- Data visualization for financial markets
- Command line tool development in Python
