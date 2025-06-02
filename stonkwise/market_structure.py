"""
Market structure detection module for stonkwise.

This module provides functionality for detecting market
structure (uptrend, downtrend, or range) based on price
action, specifically by analyzing the sequence of highs
and lows.
"""

from enum import Enum
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


class TrendType(Enum):
    """Enum for trend types."""

    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    RANGE = "range"
    UNKNOWN = "unknown"


class MarketStructureDetector:
    """
    Detector for market structure based on price action.

    This class analyzes price data to determine the market structure
    (uptrend, downtrend, or range) based on the sequence of highs and lows.
    """

    def __init__(
        self,
        swing_lookback: int = 5,
        atr_swing_threshold_multiplier: float = 1.0,  # Multiplier for ATR to define swing significance
        trend_strength_threshold: float = 0.66, # Min proportion of swings confirming trend (e.g. 0.66 for 2/3)
    ):
        """
        Initialize the market structure detector.

        Args:
            swing_lookback: Number of bars to look back/forward for swing fractal detection.
            atr_swing_threshold_multiplier: ATR multiplier for swing significance.
            trend_strength_threshold: Proportion of recent swings that must confirm a trend.
        """
        if not 0 < trend_strength_threshold <= 1:
            raise ValueError("trend_strength_threshold must be between 0 (exclusive) and 1 (inclusive)")
        self.swing_lookback = swing_lookback
        self.atr_swing_threshold_multiplier = atr_swing_threshold_multiplier
        self.trend_strength_threshold = trend_strength_threshold

        # Store detected swings
        self.swing_highs: List[Tuple[int, float]] = []  # (index, price)
        self.swing_lows: List[Tuple[int, float]] = []  # (index, price)

        # Store current trend
        self.current_trend = TrendType.UNKNOWN

    def detect_structure(self, data: pd.DataFrame) -> TrendType:
        """
        Detect market structure from price data.

        Args:
            data: DataFrame with OHLC price data

        Returns:
            Detected trend type (uptrend, downtrend, or range)
        """
        # Reset stored swings
        self.swing_highs = []
        self.swing_lows = []

        # Detect swing highs and lows
        self._detect_swings(data)

        # Analyze the sequence of swings to determine market structure
        trend = self._analyze_swings()

        # Store the current trend
        self.current_trend = trend

        return trend

    def _detect_swings(self, data: pd.DataFrame) -> None:
        """
        Detect swing highs and lows in the price data.

        A swing high is formed when a high is higher than the highs of the
        surrounding bars within the lookback period.
        A swing low is formed when a low is lower than the lows of the
        surrounding bars within the lookback period.
        Swings are then filtered based on ATR to ensure significance.

        Args:
            data: DataFrame with OHLC price data
        """
        # Ensure we have enough data for lookback periods on both sides
        required_data_length = 2 * self.swing_lookback + 1
        if len(data) < required_data_length:
            print(
                f"Not enough data: {len(data)} bars, "
                f"need at least {required_data_length}"
            )
            return

        highs = data["High"].to_numpy()  # Convert to numpy array
        lows = data["Low"].to_numpy()    # Convert to numpy array
        close_prices = data["Close"].to_numpy() # Use .to_numpy() for clarity
        
        # Calculate ATR once for the whole dataset, using a common period like 14
        atr = self._calculate_atr(data, period=14)
        if atr <= 0: # Handle cases where ATR might be zero or negative (e.g. flat price)
            # Fallback to a small percentage of the average price if ATR is not usable
            average_price = 1.0 # Default average price
            if len(close_prices) > 0:
                average_price = np.mean(close_prices)
            atr = average_price * 0.001 # Default to 0.1% of avg price as min threshold base
            if atr <= 0: # Ensure atr is positive
                atr = 0.0001 

        # For swing highs - find local maxima
        for i in range(self.swing_lookback, len(data) - self.swing_lookback):
            # Check if highs[i] is the maximum in the window [i-lookback, i+lookback]
            window_highs = highs[i - self.swing_lookback : i + self.swing_lookback + 1]
            if highs[i] >= np.max(window_highs): # Using >= to catch plateaus
                # Check if it's significantly different from the previous swing high using ATR
                is_significant_swing = True
                if self.swing_highs:
                    price_diff = abs(highs[i] - self.swing_highs[-1][1])
                    if price_diff < atr * self.atr_swing_threshold_multiplier:
                        is_significant_swing = False
                
                if is_significant_swing:
                    self.swing_highs.append((i, highs[i]))

        # For swing lows - find local minima
        for i in range(self.swing_lookback, len(data) - self.swing_lookback):
            # Check if lows[i] is the minimum in the window [i-lookback, i+lookback]
            window_lows = lows[i - self.swing_lookback : i + self.swing_lookback + 1]
            if lows[i] <= np.min(window_lows): # Using <= to catch plateaus
                # Check if it's significantly different from the previous swing low using ATR
                is_significant_swing = True
                if self.swing_lows:
                    price_diff = abs(lows[i] - self.swing_lows[-1][1])
                    if price_diff < atr * self.atr_swing_threshold_multiplier:
                        is_significant_swing = False

                if is_significant_swing:
                    self.swing_lows.append((i, lows[i]))

        print(
            f"Detected {len(self.swing_highs)} swing highs and {len(self.swing_lows)} swing lows "
            f"with lookback {self.swing_lookback}, ATR mult {self.atr_swing_threshold_multiplier}"
        )

    def _analyze_swings(self) -> TrendType:
        """
        Analyze the sequence of swing highs and lows to determine market structure
        using trend_strength_threshold.

        Returns:
            Detected trend type (uptrend, downtrend, or range)
        """
        # If we don't have enough distinct swings for comparison, trend is unknown
        if len(self.swing_highs) < 2 or len(self.swing_lows) < 2:
            print(
                f"Not enough swings for trend analysis: {len(self.swing_highs)} highs, "
                f"{len(self.swing_lows)} lows"
            )
            return TrendType.UNKNOWN

        # Consider the last N swings for trend determination (e.g., last 3-4 pairs)
        num_recent_swings_to_consider = 3 # Check last 3 highs and 3 lows
        recent_highs = self.swing_highs[-num_recent_swings_to_consider:]
        recent_lows = self.swing_lows[-num_recent_swings_to_consider:]
        
        if len(recent_highs) < 2 or len(recent_lows) < 2: # Still need at least 2 of each for comparisons
             print(
                f"Not enough RECENT swings for trend analysis: {len(recent_highs)} highs, "
                f"{len(recent_lows)} lows"
            )
             return TrendType.UNKNOWN


        # --- Higher Highs and Higher Lows (Uptrend) ---
        higher_highs_count = 0
        comparisons_high = len(recent_highs) - 1
        if comparisons_high > 0:
            for i in range(1, len(recent_highs)):
                if recent_highs[i][1] > recent_highs[i - 1][1]:
                    higher_highs_count += 1

        higher_lows_count = 0
        comparisons_low = len(recent_lows) - 1
        if comparisons_low > 0:
            for i in range(1, len(recent_lows)):
                if recent_lows[i][1] > recent_lows[i - 1][1]:
                    higher_lows_count += 1

        # --- Lower Highs and Lower Lows (Downtrend) ---
        lower_highs_count = 0
        if comparisons_high > 0:
            for i in range(1, len(recent_highs)):
                if recent_highs[i][1] < recent_highs[i - 1][1]:
                    lower_highs_count += 1
        
        lower_lows_count = 0
        if comparisons_low > 0:
            for i in range(1, len(recent_lows)):
                if recent_lows[i][1] < recent_lows[i - 1][1]:
                    lower_lows_count += 1
        
        # --- Determine Trend based on Strength Threshold ---
        # Min number of comparisons that must meet the threshold
        # For threshold of 0.66 (2/3): if 1 comparison, needs 1. if 2, needs 2. if 3, needs 2.
        
        # Uptrend conditions
        making_higher_highs = (higher_highs_count / comparisons_high >= self.trend_strength_threshold) \
            if comparisons_high > 0 else False # Or True if only one high? No, need comparison.
        making_higher_lows = (higher_lows_count / comparisons_low >= self.trend_strength_threshold) \
            if comparisons_low > 0 else False

        # Downtrend conditions
        making_lower_highs = (lower_highs_count / comparisons_high >= self.trend_strength_threshold) \
            if comparisons_high > 0 else False
        making_lower_lows = (lower_lows_count / comparisons_low >= self.trend_strength_threshold) \
            if comparisons_low > 0 else False

        # Print debug info
        print(
            f"HH: {higher_highs_count}/{comparisons_high}, HL: {higher_lows_count}/{comparisons_low} | "
            f"LH: {lower_highs_count}/{comparisons_high}, LL: {lower_lows_count}/{comparisons_low}"
        )
        print(
            f"Thresholds: HigherHighs: {making_higher_highs}, HigherLows: {making_higher_lows}, "
            f"LowerHighs: {making_lower_highs}, LowerLows: {making_lower_lows}"
        )
        
        is_uptrend = making_higher_highs and making_higher_lows
        is_downtrend = making_lower_highs and making_lower_lows

        if is_uptrend and not is_downtrend: # Clear uptrend
            return TrendType.UPTREND
        elif is_downtrend and not is_uptrend: # Clear downtrend
            return TrendType.DOWNTREND
        elif is_uptrend and is_downtrend: # Conflicting signals (e.g. HH but LL)
            # This can happen if, e.g., strength threshold is low.
            # Could mean a volatile range or a transition.
            # More conservative: if any conflict, it's not a clear trend.
            print("Conflicting trend signals based on threshold, classifying as RANGE")
            return TrendType.RANGE
        else: # Neither clear uptrend nor clear downtrend
            return TrendType.RANGE

    def get_supply_demand_zones(self, data: pd.DataFrame) -> Dict[str, List[Dict[str, float]]]:
        """
        Identify supply and demand zones based on market structure.

        In an uptrend, demand zones are formed at higher lows.
        In a downtrend, supply zones are formed at lower highs.

        Args:
            data: DataFrame with OHLC price data

        Returns:
            Dictionary with supply and demand zones
        """
        # Ensure we have detected market structure
        if self.current_trend == TrendType.UNKNOWN:
            self.detect_structure(data)

        # Initialize zones
        zones: Dict[str, List[Dict[str, float]]] = {"supply": [], "demand": []}

        # Calculate average true range (ATR) for zone width
        atr = self._calculate_atr(data, period=14)

        # Identify zones based on market structure
        if self.current_trend == TrendType.UPTREND:
            # In an uptrend, demand zones are at higher lows
            for i in range(1, min(3, len(self.swing_lows))):
                idx, price = self.swing_lows[-i]
                zones["demand"].append(
                    {
                        "price": price,
                        "lower": price - atr,
                        "upper": price + atr,
                        "strength": 1.0 - (i - 1) * 0.2,  # Strength decreases with age
                    }
                )

        elif self.current_trend == TrendType.DOWNTREND:
            # In a downtrend, supply zones are at lower highs
            for i in range(1, min(3, len(self.swing_highs))):
                idx, price = self.swing_highs[-i]
                zones["supply"].append(
                    {
                        "price": price,
                        "lower": price - atr,
                        "upper": price + atr,
                        "strength": 1.0 - (i - 1) * 0.2,  # Strength decreases with age
                    }
                )

        else:  # RANGE
            # In a range, both supply and demand zones can be identified
            # Supply zones at the upper range
            for i in range(1, min(2, len(self.swing_highs))):
                idx, price = self.swing_highs[-i]
                zones["supply"].append(
                    {
                        "price": price,
                        "lower": price - atr * 0.5,
                        "upper": price + atr * 0.5,
                        "strength": 0.7 - (i - 1) * 0.2,
                    }
                )

            # Demand zones at the lower range
            for i in range(1, min(2, len(self.swing_lows))):
                idx, price = self.swing_lows[-i]
                zones["demand"].append(
                    {
                        "price": price,
                        "lower": price - atr * 0.5,
                        "upper": price + atr * 0.5,
                        "strength": 0.7 - (i - 1) * 0.2,
                    }
                )

        return zones

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR) for determining zone width.

        Args:
            data: DataFrame with OHLC price data
            period: Period for ATR calculation

        Returns:
            ATR value. Returns a small positive value if calculation is not possible.
        """
        if len(data) < 2:
            return 0.0001  # Not enough data for TR calculation

        high = data["High"].to_numpy()
        low = data["Low"].to_numpy()
        close = data["Close"].to_numpy()

        # True Range components
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])

        tr = np.maximum(np.maximum(tr1, tr2), tr3)

        if len(tr) == 0:
            average_price = 1.0
            if len(close) > 0:
                average_price = float(np.mean(close)) # Cast to float
            calculated_atr = average_price * 0.001 
            return calculated_atr if calculated_atr > 0 else 0.0001

        # Calculate ATR as the simple moving average of true range for the defined period
        relevant_tr = tr[-period:] 
        
        if len(relevant_tr) == 0 :
            average_price = 1.0
            if len(close) > 0:
                average_price = float(np.mean(close)) # Cast to float
            calculated_atr = average_price * 0.001
            return calculated_atr if calculated_atr > 0 else 0.0001
            
        atr_value = float(np.mean(relevant_tr)) # Cast to float

        return atr_value if atr_value > 0 else 0.0001 # Ensure ATR is positive


def detect_market_structure(
    data: pd.DataFrame,
    swing_lookback: int = 5,
    atr_swing_threshold_multiplier: float = 1.0,
    trend_strength_threshold: float = 0.66,
) -> TrendType:
    """
    Detect market structure from price data.

    Args:
        data: DataFrame with OHLC price data
        swing_lookback: Number of bars to look back for swing detection.
        atr_swing_threshold_multiplier: ATR multiplier for swing significance.
        trend_strength_threshold: Proportion of recent swings that must confirm a trend.

    Returns:
        Detected trend type (uptrend, downtrend, or range)
    """
    detector = MarketStructureDetector(
        swing_lookback=swing_lookback,
        atr_swing_threshold_multiplier=atr_swing_threshold_multiplier,
        trend_strength_threshold=trend_strength_threshold,
    )

    return detector.detect_structure(data)


def get_supply_demand_zones(
    data: pd.DataFrame,
    swing_lookback: int = 5,
    atr_swing_threshold_multiplier: float = 1.0,
    trend_strength_threshold: float = 0.66, # Added for consistency if detector is reused
) -> Dict[str, List[Dict[str, float]]]:
    """
    Identify supply and demand zones based on market structure.

    Args:
        data: DataFrame with OHLC price data
        swing_lookback: Number of bars to look back for swing detection.
        atr_swing_threshold_multiplier: ATR multiplier for swing significance.
        trend_strength_threshold: Proportion of recent swings that must confirm a trend.

    Returns:
        Dictionary with supply and demand zones
    """
    detector = MarketStructureDetector(
        swing_lookback=swing_lookback,
        atr_swing_threshold_multiplier=atr_swing_threshold_multiplier,
        trend_strength_threshold=trend_strength_threshold,
    )

    # Market structure detection will be called within get_supply_demand_zones if needed
    # detector.detect_structure(data) # This is implicitly called by get_supply_demand_zones

    return detector.get_supply_demand_zones(data)
