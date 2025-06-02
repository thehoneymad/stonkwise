# 📈 Stonkwise

> *Because "stonks only go up" needed a Python library to prove it.*

Stonkwise is a Python library for backtesting trading strategies using [Backtrader](https://www.backtrader.com/). It provides a simple CLI for analyzing historical price data and backtesting trading strategies.

## 🚀 Features

- 📊 **Price Action Analysis**: Detect market structure, supply/demand zones, and reversal patterns
- 📉 **Technical Indicators**: Moving averages, trend detection, and more
- 🧪 **Backtesting**: Test your strategies on historical data
- 📋 **Performance Metrics**: Get detailed statistics on your strategy's performance
- 🔄 **Flexible Data Loading**: Use Yahoo Finance, CSV, or Parquet files
- 💾 **Results Export**: Save your backtest results for further analysis

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stonkwise.git
cd stonkwise

# Install with Poetry
poetry install

# Or with pip
pip install -e .
```

## 📖 Usage

### 📊 Analyze Stock Data

```bash
# Basic analysis
stonkwise analyze --ticker MSFT

# Analysis with a specific date range
stonkwise analyze --ticker AAPL --start-date 2023-01-01 --end-date 2023-12-31

# Analysis with moving averages
stonkwise analyze --ticker TSLA --show-ma

# Analysis with trend detection
stonkwise analyze --ticker AMZN --show-trend

# Analysis with supply/demand zones
stonkwise analyze --ticker NVDA --show-zones
```

### 🧪 Backtest Trading Strategies

```bash
# Basic backtest
stonkwise analyze --ticker MSFT --backtest

# Backtest with custom parameters
stonkwise analyze --ticker AAPL --backtest --cash 100000 --commission 0.0005

# Backtest with a specific strategy
stonkwise analyze --ticker TSLA --backtest --strategy ma_cross

# Backtest with result export
stonkwise analyze --ticker AMZN --backtest --output results.csv
```

## 📝 Strategies

### Simple Moving Average Crossover

A classic strategy that uses the crossing of two moving averages to generate buy and sell signals:

- Buy when the fast moving average crosses above the slow moving average (golden cross)
- Sell when the fast moving average crosses below the slow moving average (death cross)

### Price Action Strategy

A more advanced strategy that uses market structure, supply/demand zones, and reversal patterns:

- Identify market structure (uptrend, downtrend, or range)
- Detect supply and demand zones
- Enter trades when price revisits these zones and forms reversal patterns

## 🤔 Why "Stonkwise"?

Because in the world of meme stocks and Reddit traders, we needed a tool that's both powerful and doesn't take itself too seriously. Stonkwise helps you make wise decisions about your stonks. 

Remember: Past performance is not indicative of future results, but it's all we've got to go on unless you have a time machine (in which case, we should talk).

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Backtrader](https://www.backtrader.com/) for the amazing backtesting framework
- [yfinance](https://github.com/ranaroussi/yfinance) for easy access to Yahoo Finance data
- All the diamond-handed HODLers who inspired this project
