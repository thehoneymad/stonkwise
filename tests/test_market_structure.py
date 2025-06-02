"""
Tests for the market structure detection module.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from assertpy import assert_that

from stonkwise.market_structure import MarketStructureDetector, TrendType


class TestMarketStructureDetector:
    """Test cases for the MarketStructureDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a detector with test-specific parameters."""
        return MarketStructureDetector(
            swing_lookback=1,  # Smaller lookback for testing
            atr_swing_threshold_multiplier=0.01,  # Very low threshold for testing
            trend_strength_threshold=0.5,  # Lower threshold for easier testing
        )

    def test_detect_uptrend(self):
        """Test detection of an uptrend."""
        # Create a dataframe with a clear uptrend (higher highs and higher lows)
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]

        # Create higher highs and higher lows pattern with actual swing points
        np.random.seed(42)  # For reproducibility

        # Create an uptrend with pullbacks to generate actual swing points
        base_trend = [100 + i * 2 for i in range(30)]  # Strong uptrend base
        volatility = [np.random.normal(0, 3) for _ in range(30)]  # Add volatility

        closes = [base + vol for base, vol in zip(base_trend, volatility)]
        highs = [c + abs(np.random.normal(0, 1)) for c in closes]
        lows = [c - abs(np.random.normal(0, 1)) for c in closes]
        opens = [c + np.random.normal(0, 0.5) for c in closes]

        df = pd.DataFrame(
            {
                "Open": opens,
                "High": highs,
                "Low": lows,
                "Close": closes,
                "Volume": [1000000] * 30,
            },
            index=dates,
        )

        # Create a detector with more relaxed parameters for testing
        test_detector = MarketStructureDetector(
            swing_lookback=1,  # Smaller lookback
            atr_swing_threshold_multiplier=0.01,  # Much lower threshold
            trend_strength_threshold=0.5,  # Lower threshold for easier testing
        )

        # Detect the trend
        trend = test_detector.detect_structure(df)

        # Print debug info
        print(f"Detected {len(test_detector.swing_highs)} swing highs")
        print(f"Detected {len(test_detector.swing_lows)} swing lows")
        if test_detector.swing_highs:
            print(f"Swing highs: {[high[1] for high in test_detector.swing_highs[-5:]]}")
        if test_detector.swing_lows:
            print(f"Swing lows: {[low[1] for low in test_detector.swing_lows[-5:]]}")

        # Assert that an uptrend is detected
        assert_that(trend).is_equal_to(TrendType.UPTREND)

    def test_detect_downtrend(self):
        """Test detection of a downtrend."""
        # Create a dataframe with a clear downtrend (lower highs and lower lows)
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]

        # Create lower highs and lower lows pattern with actual swing points
        np.random.seed(42)  # For reproducibility

        # Create a downtrend with pullbacks to generate actual swing points
        base_trend = [150 - i * 2 for i in range(30)]  # Strong downtrend base
        volatility = [np.random.normal(0, 3) for _ in range(30)]  # Add volatility

        closes = [base + vol for base, vol in zip(base_trend, volatility)]
        highs = [c + abs(np.random.normal(0, 1)) for c in closes]
        lows = [c - abs(np.random.normal(0, 1)) for c in closes]
        opens = [c + np.random.normal(0, 0.5) for c in closes]

        df = pd.DataFrame(
            {
                "Open": opens,
                "High": highs,
                "Low": lows,
                "Close": closes,
                "Volume": [1000000] * 30,
            },
            index=dates,
        )

        # Create a detector with more relaxed parameters for testing
        test_detector = MarketStructureDetector(
            swing_lookback=1,  # Smaller lookback
            atr_swing_threshold_multiplier=0.01,  # Much lower threshold
            trend_strength_threshold=0.5,  # Lower threshold for easier testing
        )

        # Detect the trend
        trend = test_detector.detect_structure(df)

        # Print debug info
        print(f"Detected {len(test_detector.swing_highs)} swing highs")
        print(f"Detected {len(test_detector.swing_lows)} swing lows")
        if test_detector.swing_highs:
            print(f"Swing highs: {[high[1] for high in test_detector.swing_highs[-5:]]}")
        if test_detector.swing_lows:
            print(f"Swing lows: {[low[1] for low in test_detector.swing_lows[-5:]]}")

        # Assert that a downtrend is detected
        assert_that(trend).is_equal_to(TrendType.DOWNTREND)

    def test_detect_range(self):
        """Test detection of a range."""
        # Create a dataframe with a range (no clear trend)
        dates = [datetime.now() - timedelta(days=i) for i in range(50, 0, -1)]

        # Create oscillating pattern with no clear trend
        np.random.seed(42)  # For reproducibility
        highs = []
        lows = []
        base = 100
        for i in range(50):
            # Create a range-bound pattern with oscillations
            cycle = np.sin(i * 0.5) * 10
            highs.append(base + cycle + 5 + np.random.normal(0, 0.5))
            lows.append(base + cycle - 5 + np.random.normal(0, 0.5))

        closes = [(h + l) / 2 for h, l in zip(highs, lows)]
        opens = [c + (np.random.random() - 0.5) for c in closes]

        df = pd.DataFrame(
            {
                "Open": opens,
                "High": highs,
                "Low": lows,
                "Close": closes,
                "Volume": [1000000] * 50,
            },
            index=dates,
        )

        # Create a detector with more relaxed parameters for testing
        test_detector = MarketStructureDetector(
            swing_lookback=1,  # Smaller lookback
            atr_swing_threshold_multiplier=0.01,  # Much lower threshold
            trend_strength_threshold=0.5,  # Lower threshold for easier testing
        )

        # Detect the trend
        trend = test_detector.detect_structure(df)

        # Print debug info
        print(f"Detected {len(test_detector.swing_highs)} swing highs")
        print(f"Detected {len(test_detector.swing_lows)} swing lows")
        if test_detector.swing_highs:
            print(f"Swing highs: {[high[1] for high in test_detector.swing_highs[-5:]]}")
        if test_detector.swing_lows:
            print(f"Swing lows: {[low[1] for low in test_detector.swing_lows[-5:]]}")

        # Assert that a range is detected
        assert_that(trend).is_equal_to(TrendType.RANGE)

    def test_not_enough_swings(self, detector):
        """Test when there are not enough swings detected."""
        # Create a dataframe with very little price movement
        dates = [datetime.now() - timedelta(days=i) for i in range(10, 0, -1)]

        # Create flat price pattern with minimal variation
        price = 100
        variation = 0.1  # Very small variation

        highs = [price + variation for _ in range(10)]
        lows = [price - variation for _ in range(10)]
        closes = [price for _ in range(10)]
        opens = [price for _ in range(10)]

        df = pd.DataFrame(
            {
                "Open": opens,
                "High": highs,
                "Low": lows,
                "Close": closes,
                "Volume": [1000000] * 10,
            },
            index=dates,
        )

        # Detect the trend
        trend = detector.detect_structure(df)

        # Print debug info
        print(f"Detected {len(detector.swing_highs)} swing highs")
        print(f"Detected {len(detector.swing_lows)} swing lows")

        # Assert that the trend is unknown due to insufficient swings
        assert_that(trend).is_equal_to(TrendType.UNKNOWN)

    def test_real_world_data(self):
        """Test with a more realistic price pattern."""
        # Create a dataframe with a more realistic price pattern
        dates = [datetime.now() - timedelta(days=i) for i in range(100, 0, -1)]

        # Start with a base price and add some randomness and trend
        base_price = 100
        trend = 0.5  # Upward trend

        # Generate prices with trend and randomness
        np.random.seed(42)  # For reproducibility

        closes = [base_price + trend * i + np.random.normal(0, 2) for i in range(100)]
        highs = [c + abs(np.random.normal(0, 1)) for c in closes]
        lows = [c - abs(np.random.normal(0, 1)) for c in closes]
        opens = [c + np.random.normal(0, 0.5) for c in closes]

        df = pd.DataFrame(
            {
                "Open": opens,
                "High": highs,
                "Low": lows,
                "Close": closes,
                "Volume": [1000000] * 100,
            },
            index=dates,
        )

        # Create a detector with more relaxed parameters for testing
        test_detector = MarketStructureDetector(
            swing_lookback=1,  # Smaller lookback
            atr_swing_threshold_multiplier=0.01,  # Much lower threshold
            trend_strength_threshold=0.5,  # Lower threshold for easier testing
        )

        # Detect the trend
        trend = test_detector.detect_structure(df)

        # Print debug info
        print(f"Detected {len(test_detector.swing_highs)} swing highs")
        print(f"Detected {len(test_detector.swing_lows)} swing lows")
        if test_detector.swing_highs:
            print(f"Swing highs: {[high[1] for high in test_detector.swing_highs[-5:]]}")
        if test_detector.swing_lows:
            print(f"Swing lows: {[low[1] for low in test_detector.swing_lows[-5:]]}")

        # We don't assert a specific trend here, just that it's not unknown
        assert_that(trend).is_not_equal_to(TrendType.UNKNOWN)
