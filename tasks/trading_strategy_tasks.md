
# Trading Strategy Implementation Tasks (Inspired by YouTube Strategy)

This document outlines a series of tasks for an intern or an AI assistant to implement a price action trading strategy based on the video: ["The Only Trading Strategy You'll Ever Need"](https://youtu.be/e-QmGJU1XYc?si=H0SAnUqvyxp-t_AB).

---

## Objective

Implement a price action-based trading strategy that:
- Identifies market structure (uptrend, downtrend, or range)
- Detects supply and demand zones based on price behavior
- Executes trades based on reversal candlestick patterns when price revisits those zones

---

## Task: Define and Detect Market Structure

### Description
Analyze a series of historical price bars consisting of open, high, low, close, and volume (OHLCV) to determine whether the market is currently in an uptrend, downtrend, or ranging state, using only the sequence of highs and lows. No technical indicators may be used.

### Acceptance Criteria
- **MUST** identify an uptrend when the price forms consecutive higher highs and higher lows.
- **MUST** identify a downtrend when the price forms consecutive lower highs and lower lows.
- **MUST** return one of the following labels: 'uptrend', 'downtrend', or 'range', based on recent price behavior.
- **MUST** exclude the use of any technical indicators such as moving averages or oscillators.
- **SHOULD** use a configurable number of recent price swings to determine the trend direction.
- **SHOULD** expose the computed trend direction to downstream components of the strategy.
- **MAY** include documentation with visual examples of valid trend conditions.
- **MAY** log sequences of highs and lows used in determining the trend, for transparency and debugging.

---

## Task Breakdown

### 1. **Set Up Environment**
- [x] Python environment and dependencies are already configured.
- [x] Project structure and version control are already set up.

### 2. **Load Historical Data**
- [ ] Load OHLCV data from a CSV file.
- [ ] Convert it into a format suitable for iterative analysis over time.
- [ ] Ensure correct parsing of dates and chronological ordering of records.

### 3. **Market Structure Detection**
- [ ] Track the sequence of recent highs and lows.
- [ ] Determine trend direction based on defined rules.
- [ ] Provide access to the current trend state for other components.

### 4. **Supply and Demand Zone Detection**
- [ ] For an uptrend, identify the most recent higher low as a demand zone.
- [ ] For a downtrend, identify the most recent lower high as a supply zone.
- [ ] Represent each zone as a price range using average true range (ATR)-like logic (e.g., price ± a configurable buffer).
- [ ] Plot or record these zones for each relevant time step.

### 5. **Trade Entry Logic**
- [ ] Monitor price retracements to previously identified zones.
- [ ] Detect bullish reversal patterns (e.g., bullish engulfing) for potential long entries.
- [ ] Detect bearish reversal patterns (e.g., bearish engulfing) for potential short entries.
- [ ] Configure stop-loss and take-profit rules using a fixed or dynamic risk-reward ratio.

### 6. **Backtest Framework**
- [ ] Set up a backtesting engine to simulate trades over historical data.
- [ ] Run the strategy on a test dataset and collect performance metrics.
- [ ] Output summary statistics: total trades, win/loss ratio, cumulative profit or loss.
- [ ] Generate visualizations of trades and price zones over time.

### 7. **Optional Enhancements**
- [ ] Add logging for each trade decision including reasoning and zone conditions.
- [ ] Parameterize zone width, reversal pattern criteria, and risk management thresholds.
- [ ] Extend strategy to support multiple timeframes (e.g., hourly and daily).
- [ ] Export backtest results to a CSV file for review and analysis.

---

## Deliverables
- A Python module implementing the trading logic.
- A `README.md` explaining setup, execution, and interpretation of results.
- Screenshots or visual artifacts showing demand/supply zones and entry signals.

---

## Timeline
- **Day 1–2**: Environment setup and data ingestion.
- **Day 3–4**: Market structure and zone detection logic.
- **Day 5–6**: Entry criteria and backtest framework.
- **Day 7**: Review, enhancements, and final documentation.

---

Please confirm any assumptions with your mentor before implementing critical logic.
