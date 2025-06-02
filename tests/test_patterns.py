"""
Tests for the candlestick pattern detection module.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from assertpy import assert_that

from stonkwise.patterns import CandlestickPattern, PatternDetector, detect_bearish_engulfing, detect_bullish_engulfing, scan_for_patterns


class TestPatternDetector:
    """Test cases for the PatternDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a detector with default parameters."""
        return PatternDetector()

    def test_detect_bullish_engulfing_valid(self, detector):
        """Test detection of a valid bullish engulfing pattern."""
        # Create test data with a clear bullish engulfing pattern
        # Previous candle: bearish (open > close)
        # Current candle: bullish (close > open) and engulfs previous
        
        data = pd.DataFrame({
            'Open': [100.5, 99.0],    # Prev bearish, curr opens lower
            'High': [101.0, 102.0],   # Highs
            'Low': [99.0, 98.5],      # Lows  
            'Close': [99.5, 101.5],   # Prev bearish, curr bullish and higher
        })
        
        # Should detect bullish engulfing at index 1
        result = detector.detect_bullish_engulfing(data, 1)
        assert_that(result).is_true()

    def test_detect_bullish_engulfing_invalid_prev_bullish(self, detector):
        """Test that bullish engulfing is not detected when previous candle is bullish."""
        data = pd.DataFrame({
            'Open': [99.0, 99.0],     # Previous is bullish (open < close)
            'High': [101.0, 102.0],
            'Low': [98.5, 98.5],
            'Close': [100.5, 101.5],  # Previous bullish, current bullish
        })
        
        result = detector.detect_bullish_engulfing(data, 1)
        assert_that(result).is_false()

    def test_detect_bullish_engulfing_invalid_curr_bearish(self, detector):
        """Test that bullish engulfing is not detected when current candle is bearish."""
        data = pd.DataFrame({
            'Open': [100.5, 100.0],   # Previous bearish, current bearish
            'High': [101.0, 100.5],
            'Low': [99.0, 98.5],
            'Close': [99.5, 99.0],    # Both bearish
        })
        
        result = detector.detect_bullish_engulfing(data, 1)
        assert_that(result).is_false()

    def test_detect_bullish_engulfing_insufficient_engulfing(self, detector):
        """Test that bullish engulfing is not detected when engulfing is insufficient."""
        data = pd.DataFrame({
            'Open': [100.5, 100.0],   # Previous bearish
            'High': [101.0, 101.0],
            'Low': [99.5, 99.5],
            'Close': [99.8, 100.2],   # Current doesn't fully engulf previous
        })
        
        result = detector.detect_bullish_engulfing(data, 1)
        assert_that(result).is_false()

    def test_detect_bearish_engulfing_valid(self, detector):
        """Test detection of a valid bearish engulfing pattern."""
        data = pd.DataFrame({
            'Open': [99.0, 101.0],    # Previous bullish, current opens higher
            'High': [100.5, 101.5],
            'Low': [98.5, 98.0],
            'Close': [100.5, 98.5],   # Previous bullish, current bearish and engulfs
        })
        
        result = detector.detect_bearish_engulfing(data, 1)
        assert_that(result).is_true()

    def test_detect_bearish_engulfing_invalid_prev_bearish(self, detector):
        """Test that bearish engulfing is not detected when previous candle is bearish."""
        data = pd.DataFrame({
            'Open': [100.5, 101.0],   # Previous bearish
            'High': [101.0, 101.5],
            'Low': [99.0, 98.0],
            'Close': [99.5, 98.5],    # Previous bearish, current bearish
        })
        
        result = detector.detect_bearish_engulfing(data, 1)
        assert_that(result).is_false()

    def test_detect_hammer_valid(self, detector):
        """Test detection of a valid hammer pattern."""
        # Hammer: small body at top, long lower wick, short upper wick
        data = pd.DataFrame({
            'Open': [100.0],
            'High': [100.2],    # Short upper wick
            'Low': [97.0],      # Long lower wick
            'Close': [99.8],    # Small body near top
        })
        
        result = detector.detect_hammer(data, 0)
        assert_that(result).is_true()

    def test_detect_hammer_invalid_large_body(self, detector):
        """Test that hammer is not detected with large body."""
        data = pd.DataFrame({
            'Open': [100.0],
            'High': [102.0],
            'Low': [97.0],
            'Close': [97.5],    # Large body
        })
        
        result = detector.detect_hammer(data, 0)
        assert_that(result).is_false()

    def test_detect_shooting_star_valid(self, detector):
        """Test detection of a valid shooting star pattern."""
        # Shooting star: small body at bottom, long upper wick, short lower wick
        data = pd.DataFrame({
            'Open': [100.0],
            'High': [103.0],    # Long upper wick
            'Low': [99.8],      # Short lower wick
            'Close': [100.2],   # Small body near bottom
        })
        
        result = detector.detect_shooting_star(data, 0)
        assert_that(result).is_true()

    def test_detect_shooting_star_invalid_large_body(self, detector):
        """Test that shooting star is not detected with large body."""
        data = pd.DataFrame({
            'Open': [100.0],
            'High': [103.0],
            'Low': [99.8],
            'Close': [102.5],   # Large body
        })
        
        result = detector.detect_shooting_star(data, 0)
        assert_that(result).is_false()

    def test_boundary_conditions(self, detector):
        """Test boundary conditions for pattern detection."""
        # Test with insufficient data
        data = pd.DataFrame({
            'Open': [100.0],
            'High': [101.0],
            'Low': [99.0],
            'Close': [100.5],
        })
        
        # Should return False for engulfing patterns with only one candle
        assert_that(detector.detect_bullish_engulfing(data, 0)).is_false()
        assert_that(detector.detect_bearish_engulfing(data, 0)).is_false()
        
        # Should handle out-of-bounds indices gracefully
        assert_that(detector.detect_bullish_engulfing(data, 10)).is_false()
        assert_that(detector.detect_bearish_engulfing(data, 10)).is_false()

    def test_scan_patterns_comprehensive(self, detector):
        """Test comprehensive pattern scanning."""
        # Create data with multiple pattern types
        dates = [datetime.now() - timedelta(days=i) for i in range(10, 0, -1)]
        
        data = pd.DataFrame({
            'Open': [100.0, 100.5, 99.0, 101.0, 100.0, 102.0, 100.0, 99.5, 101.0, 100.0],
            'High': [101.0, 101.0, 102.0, 101.5, 100.2, 102.5, 103.0, 100.0, 101.5, 101.0],
            'Low': [99.0, 99.5, 98.5, 98.0, 97.0, 101.5, 99.8, 98.0, 98.5, 99.0],
            'Close': [100.5, 99.5, 101.5, 98.5, 99.8, 101.8, 100.2, 98.2, 98.8, 100.5],
        }, index=dates)
        
        patterns = [
            CandlestickPattern.BULLISH_ENGULFING,
            CandlestickPattern.BEARISH_ENGULFING,
            CandlestickPattern.HAMMER,
            CandlestickPattern.SHOOTING_STAR,
        ]
        
        results = detector.scan_patterns(data, patterns)
        
        # Verify structure of results
        assert_that(results).is_instance_of(dict)
        assert_that(results).contains_key('bullish_engulfing')
        assert_that(results).contains_key('bearish_engulfing')
        assert_that(results).contains_key('hammer')
        assert_that(results).contains_key('shooting_star')
        
        # Each pattern should have a list of (index, timestamp) tuples
        for pattern_name, occurrences in results.items():
            assert_that(occurrences).is_instance_of(list)
            for occurrence in occurrences:
                assert_that(occurrence).is_instance_of(tuple)
                assert_that(occurrence).is_length(2)  # (index, timestamp)

    def test_zero_range_candles(self, detector):
        """Test behavior with zero-range candles (all OHLC equal)."""
        data = pd.DataFrame({
            'Open': [100.0, 100.0],
            'High': [100.0, 100.0],
            'Low': [100.0, 100.0],
            'Close': [100.0, 100.0],
        })
        
        # Should handle zero-range candles without errors
        assert_that(detector.detect_hammer(data, 0)).is_false()
        assert_that(detector.detect_shooting_star(data, 0)).is_false()
        assert_that(detector.detect_bullish_engulfing(data, 1)).is_false()
        assert_that(detector.detect_bearish_engulfing(data, 1)).is_false()


class TestConvenienceFunctions:
    """Test the convenience functions."""

    def test_detect_bullish_engulfing_function(self):
        """Test the convenience function for bullish engulfing detection."""
        data = pd.DataFrame({
            'Open': [100.5, 99.0],
            'High': [101.0, 102.0],
            'Low': [99.0, 98.5],
            'Close': [99.5, 101.5],
        })
        
        result = detect_bullish_engulfing(data, 1)
        assert_that(result).is_true()

    def test_detect_bearish_engulfing_function(self):
        """Test the convenience function for bearish engulfing detection."""
        data = pd.DataFrame({
            'Open': [99.0, 101.0],
            'High': [100.5, 101.5],
            'Low': [98.5, 98.0],
            'Close': [100.5, 98.5],
        })
        
        result = detect_bearish_engulfing(data, 1)
        assert_that(result).is_true()

    def test_scan_for_patterns_function(self):
        """Test the convenience function for pattern scanning."""
        data = pd.DataFrame({
            'Open': [100.0, 100.5, 99.0],
            'High': [101.0, 101.0, 102.0],
            'Low': [99.0, 99.5, 98.5],
            'Close': [100.5, 99.5, 101.5],
        })
        
        results = scan_for_patterns(data)
        assert_that(results).is_instance_of(dict)
        assert_that(results).contains_key('bullish_engulfing')


class TestPatternDetectorCustomParameters:
    """Test PatternDetector with custom parameters."""

    def test_custom_engulfing_threshold(self):
        """Test pattern detection with custom engulfing threshold."""
        detector = PatternDetector(engulfing_threshold=0.05)  # 5% threshold
        
        data = pd.DataFrame({
            'Open': [100.5, 99.8],    # Marginal engulfing
            'High': [101.0, 101.2],
            'Low': [99.8, 99.0],
            'Close': [100.0, 100.2],
        })
        
        # With higher threshold, this marginal engulfing should not be detected
        result = detector.detect_bullish_engulfing(data, 1)
        # The exact result depends on the specific calculation, but test should not crash
        assert_that(result).is_false()

    def test_custom_body_size_ratio(self):
        """Test pattern detection with custom body size ratio."""
        detector = PatternDetector(min_body_size_ratio=0.8)  # Require large bodies
        
        data = pd.DataFrame({
            'Open': [100.0],
            'High': [100.3],
            'Low': [97.0],      # Long wick
            'Close': [100.1],   # Very small body
        })
        
        # With high body size requirement, small body patterns should not be detected
        result = detector.detect_hammer(data, 0)
        # The function returns False as expected for small body with high ratio requirement
        assert_that(result).is_false() 
