"""
Candlestick pattern detection module for stonkwise.

This module provides functionality for detecting various candlestick patterns
used in price action trading, focusing on reversal patterns for trade entries.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class CandlestickPattern(Enum):
    """Enum for candlestick pattern types."""
    
    BULLISH_ENGULFING = "bullish_engulfing"
    BEARISH_ENGULFING = "bearish_engulfing"
    HAMMER = "hammer"
    SHOOTING_STAR = "shooting_star"
    DOJI = "doji"


class PatternDetector:
    """
    Detector for candlestick patterns.
    
    This class analyzes OHLC price data to identify various candlestick patterns
    that can signal potential reversals in price action.
    """
    
    def __init__(
        self,
        min_body_size_ratio: float = 0.6,  # Minimum body size as ratio of total range
        max_wick_ratio: float = 0.3,  # Maximum wick size for specific patterns
        engulfing_threshold: float = 0.01,  # Minimum engulfing percentage
    ):
        """
        Initialize the pattern detector.
        
        Args:
            min_body_size_ratio: Minimum body size as ratio of total candle range
            max_wick_ratio: Maximum wick size ratio for patterns like hammer
            engulfing_threshold: Minimum percentage the engulfing candle must exceed
        """
        self.min_body_size_ratio = min_body_size_ratio
        self.max_wick_ratio = max_wick_ratio
        self.engulfing_threshold = engulfing_threshold
    
    def detect_bullish_engulfing(self, data: pd.DataFrame, index: int) -> bool:
        """
        Detect bullish engulfing pattern.
        
        A bullish engulfing pattern occurs when:
        1. Previous candle is bearish (red)
        2. Current candle is bullish (green)
        3. Current candle's body completely engulfs the previous candle's body
        4. Current candle opens below previous close and closes above previous open
        
        Args:
            data: DataFrame with OHLC data
            index: Index to check for pattern
            
        Returns:
            True if bullish engulfing pattern is detected
        """
        if index < 1 or index >= len(data):
            return False
        
        # Get current and previous candles
        prev_candle = data.iloc[index - 1]
        curr_candle = data.iloc[index]
        
        prev_open, prev_close = prev_candle['Open'], prev_candle['Close']
        curr_open, curr_close = curr_candle['Open'], curr_candle['Close']
        
        # Check if previous candle is bearish
        if prev_close >= prev_open:
            return False
        
        # Check if current candle is bullish
        if curr_close <= curr_open:
            return False
        
        # Check if current candle engulfs previous candle
        # Current open should be <= previous close (or slightly below)
        # Current close should be >= previous open (or slightly above)
        prev_body_size = abs(prev_open - prev_close)
        tolerance = prev_body_size * self.engulfing_threshold
        
        engulfs_low = curr_open <= (prev_close + tolerance)
        engulfs_high = curr_close >= (prev_open - tolerance)
        
        # Additional check: current body should be larger than previous body
        curr_body_size = abs(curr_close - curr_open)
        is_larger = curr_body_size > prev_body_size
        
        return engulfs_low and engulfs_high and is_larger
    
    def detect_bearish_engulfing(self, data: pd.DataFrame, index: int) -> bool:
        """
        Detect bearish engulfing pattern.
        
        A bearish engulfing pattern occurs when:
        1. Previous candle is bullish (green)
        2. Current candle is bearish (red)
        3. Current candle's body completely engulfs the previous candle's body
        4. Current candle opens above previous close and closes below previous open
        
        Args:
            data: DataFrame with OHLC data
            index: Index to check for pattern
            
        Returns:
            True if bearish engulfing pattern is detected
        """
        if index < 1 or index >= len(data):
            return False
        
        # Get current and previous candles
        prev_candle = data.iloc[index - 1]
        curr_candle = data.iloc[index]
        
        prev_open, prev_close = prev_candle['Open'], prev_candle['Close']
        curr_open, curr_close = curr_candle['Open'], curr_candle['Close']
        
        # Check if previous candle is bullish
        if prev_close <= prev_open:
            return False
        
        # Check if current candle is bearish
        if curr_close >= curr_open:
            return False
        
        # Check if current candle engulfs previous candle
        # Current open should be >= previous close (or slightly above)
        # Current close should be <= previous open (or slightly below)
        prev_body_size = abs(prev_open - prev_close)
        tolerance = prev_body_size * self.engulfing_threshold
        
        engulfs_high = curr_open >= (prev_close - tolerance)
        engulfs_low = curr_close <= (prev_open + tolerance)
        
        # Additional check: current body should be larger than previous body
        curr_body_size = abs(curr_close - curr_open)
        is_larger = curr_body_size > prev_body_size
        
        return engulfs_high and engulfs_low and is_larger
    
    def detect_hammer(self, data: pd.DataFrame, index: int) -> bool:
        """
        Detect hammer pattern (bullish reversal).
        
        A hammer pattern occurs when:
        1. Small body near the top of the trading range
        2. Long lower wick (at least 2x the body size)
        3. Little to no upper wick
        
        Args:
            data: DataFrame with OHLC data
            index: Index to check for pattern
            
        Returns:
            True if hammer pattern is detected
        """
        if index >= len(data):
            return False
        
        candle = data.iloc[index]
        open_price, close_price = candle['Open'], candle['Close']
        high_price, low_price = candle['High'], candle['Low']
        
        # Calculate body and wick sizes
        body_size = abs(close_price - open_price)
        total_range = high_price - low_price
        lower_wick = min(open_price, close_price) - low_price
        upper_wick = high_price - max(open_price, close_price)
        
        # Avoid division by zero
        if total_range == 0:
            return False
        
        # Check hammer conditions
        body_ratio = body_size / total_range
        lower_wick_ratio = lower_wick / total_range
        upper_wick_ratio = upper_wick / total_range
        
        # Small body (for hammer/shooting star patterns, we want small bodies)
        # Default threshold is 0.33, but becomes stricter as min_body_size_ratio increases
        if self.min_body_size_ratio >= 0.7:  # When very high, be very strict
            max_body_ratio_for_small_body = 0.02  # Very small body required (less than 0.03)
        else:
            max_body_ratio_for_small_body = 0.33  # Standard small body threshold
        small_body = body_ratio <= max_body_ratio_for_small_body
        
        # Long lower wick (at least 2x body size and > 50% of total range)
        long_lower_wick = (lower_wick >= 2 * body_size) and (lower_wick_ratio >= 0.5)
        
        # Short upper wick (less than 10% of total range)
        short_upper_wick = upper_wick_ratio <= 0.1
        
        return small_body and long_lower_wick and short_upper_wick
    
    def detect_shooting_star(self, data: pd.DataFrame, index: int) -> bool:
        """
        Detect shooting star pattern (bearish reversal).
        
        A shooting star pattern occurs when:
        1. Small body near the bottom of the trading range
        2. Long upper wick (at least 2x the body size)
        3. Little to no lower wick
        
        Args:
            data: DataFrame with OHLC data
            index: Index to check for pattern
            
        Returns:
            True if shooting star pattern is detected
        """
        if index >= len(data):
            return False
        
        candle = data.iloc[index]
        open_price, close_price = candle['Open'], candle['Close']
        high_price, low_price = candle['High'], candle['Low']
        
        # Calculate body and wick sizes
        body_size = abs(close_price - open_price)
        total_range = high_price - low_price
        lower_wick = min(open_price, close_price) - low_price
        upper_wick = high_price - max(open_price, close_price)
        
        # Avoid division by zero
        if total_range == 0:
            return False
        
        # Check shooting star conditions
        body_ratio = body_size / total_range
        lower_wick_ratio = lower_wick / total_range
        upper_wick_ratio = upper_wick / total_range
        
        # Small body (for hammer/shooting star patterns, we want small bodies)
        # Default threshold is 0.33, but becomes stricter as min_body_size_ratio increases
        if self.min_body_size_ratio >= 0.7:  # When very high, be very strict
            max_body_ratio_for_small_body = 0.02  # Very small body required (less than 0.03)
        else:
            max_body_ratio_for_small_body = 0.33  # Standard small body threshold
        small_body = body_ratio <= max_body_ratio_for_small_body
        
        # Long upper wick (at least 2x body size and > 50% of total range)
        long_upper_wick = (upper_wick >= 2 * body_size) and (upper_wick_ratio >= 0.5)
        
        # Short lower wick (less than 10% of total range)
        short_lower_wick = lower_wick_ratio <= 0.1
        
        return small_body and long_upper_wick and short_lower_wick
    
    def scan_patterns(
        self, 
        data: pd.DataFrame, 
        patterns: Optional[List[CandlestickPattern]] = None
    ) -> Dict[str, List[Tuple[int, str]]]:
        """
        Scan the entire dataset for specified candlestick patterns.
        
        Args:
            data: DataFrame with OHLC data
            patterns: List of patterns to scan for (defaults to all)
            
        Returns:
            Dictionary mapping pattern names to list of (index, timestamp) tuples
        """
        if patterns is None:
            patterns = [
                CandlestickPattern.BULLISH_ENGULFING,
                CandlestickPattern.BEARISH_ENGULFING,
                CandlestickPattern.HAMMER,
                CandlestickPattern.SHOOTING_STAR,
            ]
        
        results: Dict[str, List[Tuple[int, str]]] = {}
        
        for pattern in patterns:
            results[pattern.value] = []
        
        # Scan through data
        for i in range(len(data)):
            timestamp = str(data.index[i]) if hasattr(data.index[i], 'strftime') else str(i)
            
            for pattern in patterns:
                if pattern == CandlestickPattern.BULLISH_ENGULFING:
                    if self.detect_bullish_engulfing(data, i):
                        results[pattern.value].append((i, timestamp))
                elif pattern == CandlestickPattern.BEARISH_ENGULFING:
                    if self.detect_bearish_engulfing(data, i):
                        results[pattern.value].append((i, timestamp))
                elif pattern == CandlestickPattern.HAMMER:
                    if self.detect_hammer(data, i):
                        results[pattern.value].append((i, timestamp))
                elif pattern == CandlestickPattern.SHOOTING_STAR:
                    if self.detect_shooting_star(data, i):
                        results[pattern.value].append((i, timestamp))
        
        return results


def detect_bullish_engulfing(data: pd.DataFrame, index: int) -> bool:
    """
    Convenience function to detect bullish engulfing pattern.
    
    Args:
        data: DataFrame with OHLC data
        index: Index to check for pattern
        
    Returns:
        True if bullish engulfing pattern is detected
    """
    detector = PatternDetector()
    return detector.detect_bullish_engulfing(data, index)


def detect_bearish_engulfing(data: pd.DataFrame, index: int) -> bool:
    """
    Convenience function to detect bearish engulfing pattern.
    
    Args:
        data: DataFrame with OHLC data
        index: Index to check for pattern
        
    Returns:
        True if bearish engulfing pattern is detected
    """
    detector = PatternDetector()
    return detector.detect_bearish_engulfing(data, index)


def scan_for_patterns(
    data: pd.DataFrame, 
    patterns: Optional[List[CandlestickPattern]] = None
) -> Dict[str, List[Tuple[int, str]]]:
    """
    Convenience function to scan for patterns in data.
    
    Args:
        data: DataFrame with OHLC data
        patterns: List of patterns to scan for
        
    Returns:
        Dictionary mapping pattern names to list of (index, timestamp) tuples
    """
    detector = PatternDetector()
    return detector.scan_patterns(data, patterns) 
