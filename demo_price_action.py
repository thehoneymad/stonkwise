#!/usr/bin/env python3
"""
Demonstration of the Price Action Trading Strategy.

This script shows how to use the price action strategy to backtest
trades based on supply/demand zones and reversal patterns.
"""

from datetime import datetime, timedelta

import pandas as pd

from stonkwise.market_structure import MarketStructureDetector, TrendType
from stonkwise.patterns import CandlestickPattern, PatternDetector


def demo_pattern_detection():
    """Demonstrate candlestick pattern detection."""
    print("=== Candlestick Pattern Detection Demo ===")
    
    # Create sample data with engulfing patterns
    data = pd.DataFrame({
        'Open': [100.5, 99.0, 101.0, 102.5],
        'High': [101.0, 102.0, 101.5, 102.8],
        'Low': [99.0, 98.5, 100.5, 101.8],
        'Close': [99.5, 101.5, 102.0, 102.0],
    })
    
    detector = PatternDetector()
    
    # Check for bullish engulfing at index 1
    bullish = detector.detect_bullish_engulfing(data, 1)
    print(f"Bullish engulfing at index 1: {bullish}")
    
    # Check for bearish engulfing at index 3
    bearish = detector.detect_bearish_engulfing(data, 3)
    print(f"Bearish engulfing at index 3: {bearish}")
    
    # Scan all patterns
    patterns = detector.scan_patterns(data)
    print(f"All patterns found: {patterns}")
    print()


def demo_market_structure():
    """Demonstrate market structure detection."""
    print("=== Market Structure Detection Demo ===")
    
    # Create uptrend data
    dates = [datetime.now() - timedelta(days=i) for i in range(20, 0, -1)]
    uptrend_data = pd.DataFrame({
        'Open': [100 + i * 0.5 for i in range(20)],
        'High': [101 + i * 0.5 for i in range(20)],
        'Low': [99 + i * 0.5 for i in range(20)],
        'Close': [100.5 + i * 0.5 for i in range(20)],
        'Volume': [1000000] * 20,
    }, index=dates)
    
    detector = MarketStructureDetector(
        swing_lookback=2,
        atr_swing_threshold_multiplier=0.1,
        trend_strength_threshold=0.6
    )
    
    trend = detector.detect_structure(uptrend_data)
    print(f"Detected trend: {trend.value}")
    
    zones = detector.get_supply_demand_zones(uptrend_data)
    print(f"Supply zones: {len(zones['supply'])}")
    print(f"Demand zones: {len(zones['demand'])}")
    
    for i, zone in enumerate(zones['demand'][:2]):
        print(f"Demand zone {i+1}: Price={zone['price']:.2f}, "
              f"Range=[{zone['lower']:.2f}, {zone['upper']:.2f}], "
              f"Strength={zone['strength']:.2f}")
    print()


def demo_strategy_parameters():
    """Demonstrate strategy parameter configuration."""
    print("=== Price Action Strategy Parameters ===")
    
    from stonkwise.strategies.price_action import PriceActionStrategy

    # Note: This creates the strategy class but doesn't instantiate it
    # since that requires a Cerebro context
    params = dict(PriceActionStrategy.params)
    
    print("Market Structure Parameters:")
    print(f"  - Swing lookback: {params['swing_lookback']}")
    print(f"  - ATR threshold multiplier: {params['atr_swing_threshold_multiplier']}")
    print(f"  - Trend strength threshold: {params['trend_strength_threshold']}")
    
    print("\nPattern Parameters:")
    print(f"  - Engulfing threshold: {params['engulfing_threshold']}")
    print(f"  - Require pattern confirmation: {params['require_pattern_confirmation']}")
    print(f"  - Allowed patterns: {params['allowed_patterns']}")
    
    print("\nRisk Management:")
    print(f"  - Risk-reward ratio: {params['risk_reward_ratio']}")
    print(f"  - Stop loss ATR multiplier: {params['stop_loss_atr_mult']}")
    print(f"  - Max risk per trade: {params['max_risk_per_trade']*100}%")
    
    print("\nTrade Management:")
    print(f"  - Max concurrent trades: {params['max_concurrent_trades']}")
    print(f"  - ATR period: {params['atr_period']}")
    print()


def demo_backtesting_integration():
    """Demonstrate how to use the strategy in backtesting."""
    print("=== Backtesting Integration Demo ===")
    
    print("To use the price action strategy in backtesting:")
    print()
    print("1. Using the CLI:")
    print("   python -m stonkwise backtest AAPL --strategy price_action")
    print()
    print("2. Using the Python API:")
    print("   from stonkwise.backtester import backtest_ticker")
    print("   result = backtest_ticker(")
    print("       ticker='AAPL',")
    print("       strategy='price_action',")
    print("       start_date='2023-01-01',")
    print("       end_date='2023-12-31'")
    print("   )")
    print()
    print("3. The strategy will:")
    print("   - Detect market structure (uptrend/downtrend/range)")
    print("   - Identify supply and demand zones")
    print("   - Monitor price retracements to zones")
    print("   - Confirm entries with bullish/bearish engulfing patterns")
    print("   - Use ATR-based stop-loss and risk-reward ratios")
    print("   - Log detailed trade reasoning")
    print()


if __name__ == "__main__":
    print("Price Action Trading Strategy Demonstration")
    print("=" * 50)
    print()
    
    try:
        demo_pattern_detection()
        demo_market_structure() 
        demo_strategy_parameters()
        demo_backtesting_integration()
        
        print("✓ All demos completed successfully!")
        print("\nThe price action strategy is ready to use!")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
