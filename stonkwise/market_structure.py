"""
Market structure detection module for stonkwise.

This module provides functionality for detecting market structure (uptrend, downtrend, or range)
based on price action, specifically by analyzing the sequence of highs and lows.
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
        swing_threshold: float = 0.003,  # Reduced from 0.005 to 0.003
        trend_strength_threshold: float = 0.5,
    ):
        """
        Initialize the market structure detector.

        Args:
            swing_lookback: Number of bars to look back for swing detection
            swing_threshold: Minimum price change (as percentage) to consider a swing
            trend_strength_threshold: Threshold for trend strength (0.0 to 1.0)
        """
        self.swing_lookback = swing_lookback
        self.swing_threshold = swing_threshold
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

        Args:
            data: DataFrame with OHLC price data
        """
        # Ensure we have enough data
        if len(data) < 2 * self.swing_lookback + 1:
            print(
                f"Not enough data: {len(data)} bars, need at least {2 * self.swing_lookback + 1}"
            )
            return

        # Get high and low prices
        highs = data["High"].values
        lows = data["Low"].values

        # Use a more relaxed swing detection algorithm
        # Instead of requiring a perfect local maximum/minimum,
        # we'll use a rolling window approach

        # For swing highs - find local maxima
        for i in range(self.swing_lookback, len(data) - self.swing_lookback):
            # Check if this is a local maximum within the lookback window
            window_highs = highs[i - self.swing_lookback : i + self.swing_lookback + 1]
            if (
                highs[i] >= np.max(window_highs) * 0.9995
            ):  # Allow for very small variations
                # Check if it's significantly different from the previous swing high
                if (
                    not self.swing_highs
                    or abs(highs[i] - self.swing_highs[-1][1]) / self.swing_highs[-1][1]
                    >= self.swing_threshold
                ):
                    self.swing_highs.append((i, highs[i]))

        # For swing lows - find local minima
        for i in range(self.swing_lookback, len(data) - self.swing_lookback):
            # Check if this is a local minimum within the lookback window
            window_lows = lows[i - self.swing_lookback : i + self.swing_lookback + 1]
            if (
                lows[i] <= np.min(window_lows) * 1.0005
            ):  # Allow for very small variations
                # Check if it's significantly different from the previous swing low
                if (
                    not self.swing_lows
                    or abs(lows[i] - self.swing_lows[-1][1]) / self.swing_lows[-1][1]
                    >= self.swing_threshold
                ):
                    self.swing_lows.append((i, lows[i]))

        print(
            f"Detected {len(self.swing_highs)} swing highs and {len(self.swing_lows)} swing lows"
        )

    def _analyze_swings(self) -> TrendType:
        """
        Analyze the sequence of swing highs and lows to determine market structure.

        Returns:
            Detected trend type (uptrend, downtrend, or range)
        """
        # If we don't have enough swings, return unknown
        if len(self.swing_highs) < 2 or len(self.swing_lows) < 2:
            print(
                f"Not enough swings detected: {len(self.swing_highs)} highs, {len(self.swing_lows)} lows"
            )
            return TrendType.UNKNOWN

        # Get the last few swing highs and lows
        recent_highs = (
            self.swing_highs[-3:]
            if len(self.swing_highs) >= 3
            else self.swing_highs[-2:]
        )
        recent_lows = (
            self.swing_lows[-3:] if len(self.swing_lows) >= 3 else self.swing_lows[-2:]
        )

        # Check for higher highs and higher lows (uptrend)
        higher_highs = all(
            recent_highs[i][1] > recent_highs[i - 1][1]
            for i in range(1, len(recent_highs))
        )
        higher_lows = all(
            recent_lows[i][1] > recent_lows[i - 1][1]
            for i in range(1, len(recent_lows))
        )

        # Check for lower highs and lower lows (downtrend)
        lower_highs = all(
            recent_highs[i][1] < recent_highs[i - 1][1]
            for i in range(1, len(recent_highs))
        )
        lower_lows = all(
            recent_lows[i][1] < recent_lows[i - 1][1]
            for i in range(1, len(recent_lows))
        )

        # Print debug info
        print(f"Higher highs: {higher_highs}, Higher lows: {higher_lows}")
        print(f"Lower highs: {lower_highs}, Lower lows: {lower_lows}")

        # Determine trend based on the sequence of highs and lows
        if higher_highs and higher_lows:
            return TrendType.UPTREND
        elif lower_highs and lower_lows:
            return TrendType.DOWNTREND
        else:
            return TrendType.RANGE

    def get_supply_demand_zones(
        self, data: pd.DataFrame
    ) -> Dict[str, List[Dict[str, float]]]:
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
        zones = {"supply": [], "demand": []}

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
            ATR value
        """
        # Calculate true range
        high = data["High"].values
        low = data["Low"].values
        close = data["Close"].values

        tr1 = high[1:] - low[1:]  # Current high - current low
        tr2 = np.abs(high[1:] - close[:-1])  # Current high - previous close
        tr3 = np.abs(low[1:] - close[:-1])  # Current low - previous close

        tr = np.maximum(np.maximum(tr1, tr2), tr3)

        # Calculate ATR as the simple moving average of true range
        atr = np.mean(tr[-period:])

        return atr


def detect_market_structure(
    data: pd.DataFrame, swing_lookback: int = 5, swing_threshold: float = 0.003
) -> TrendType:
    """
    Detect market structure from price data.

    Args:
        data: DataFrame with OHLC price data
        swing_lookback: Number of bars to look back for swing detection
        swing_threshold: Minimum price change (as percentage) to consider a swing

    Returns:
        Detected trend type (uptrend, downtrend, or range)
    """
    detector = MarketStructureDetector(
        swing_lookback=swing_lookback, swing_threshold=swing_threshold
    )

    return detector.detect_structure(data)


def get_supply_demand_zones(
    data: pd.DataFrame, swing_lookback: int = 5, swing_threshold: float = 0.003
) -> Dict[str, List[Dict[str, float]]]:
    """
    Identify supply and demand zones based on market structure.

    Args:
        data: DataFrame with OHLC price data
        swing_lookback: Number of bars to look back for swing detection
        swing_threshold: Minimum price change (as percentage) to consider a swing

    Returns:
        Dictionary with supply and demand zones
    """
    detector = MarketStructureDetector(
        swing_lookback=swing_lookback, swing_threshold=swing_threshold
    )

    detector.detect_structure(data)

    return detector.get_supply_demand_zones(data)
