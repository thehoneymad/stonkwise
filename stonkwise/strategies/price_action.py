"""
Price action trading strategy for stonkwise.

This strategy implements trade entry logic based on:
1. Market structure detection (uptrend, downtrend, range)
2. Supply and demand zone identification
3. Price retracements to zones
4. Reversal candlestick pattern confirmation
5. Risk management with stop-loss and take-profit
"""

from typing import Dict, List, Optional, Tuple

import backtrader as bt
import pandas as pd

from stonkwise.market_structure import MarketStructureDetector, TrendType
from stonkwise.patterns import PatternDetector


class PriceActionStrategy(bt.Strategy):
    """
    A price action trading strategy that trades reversals at supply/demand zones.

    This strategy:
    - Identifies market structure and supply/demand zones
    - Monitors price retracements to these zones
    - Confirms entries with bullish/bearish engulfing patterns
    - Uses ATR-based stop-loss and risk-reward ratio for take-profit
    """

    params = (
        # Market structure parameters
        ("swing_lookback", 5),  # Lookback for swing detection
        ("atr_swing_threshold_multiplier", 1.0),  # ATR multiplier for swing significance
        ("trend_strength_threshold", 0.66),  # Proportion of swings confirming trend
        # Zone parameters
        ("zone_buffer_atr_mult", 1.0),  # ATR multiplier for zone width
        ("max_zones_to_track", 3),  # Maximum number of zones to track
        ("zone_strength_threshold", 0.5),  # Minimum zone strength to consider
        # Pattern parameters
        ("engulfing_threshold", 0.01),  # Minimum engulfing percentage
        ("require_pattern_confirmation", True),  # Whether to require pattern confirmation
        ("allowed_patterns", ["bullish_engulfing", "bearish_engulfing"]),  # Patterns to use
        # Risk management parameters
        ("risk_reward_ratio", 2.0),  # Risk-reward ratio (2:1 means 2x risk for reward)
        ("stop_loss_atr_mult", 2.0),  # ATR multiplier for stop-loss distance
        ("max_risk_per_trade", 0.02),  # Maximum risk per trade as % of portfolio
        ("atr_period", 14),  # ATR calculation period
        # Trade management
        ("max_concurrent_trades", 2),  # Maximum concurrent positions
        ("zone_retest_lookback", 20),  # Bars to look back for zone retest detection
    )

    def __init__(self) -> None:
        """Initialize the strategy."""
        # Data references
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.datavolume = self.datas[0].volume

        # Initialize detectors
        self.market_detector = MarketStructureDetector(
            swing_lookback=self.p.swing_lookback,
            atr_swing_threshold_multiplier=self.p.atr_swing_threshold_multiplier,
            trend_strength_threshold=self.p.trend_strength_threshold,
        )

        self.pattern_detector = PatternDetector(
            engulfing_threshold=self.p.engulfing_threshold,
        )

        # Strategy state
        self.current_trend = TrendType.UNKNOWN
        self.supply_zones: List[Dict] = []
        self.demand_zones: List[Dict] = []
        self.pending_orders: List[bt.Order] = []
        self.active_trades: List[Dict] = []

        # Data buffer for analysis (store recent bars)
        self.data_buffer: List[Dict] = []
        self.buffer_size = max(50, self.p.zone_retest_lookback + 10)

        # ATR indicator for risk management
        self.atr = bt.indicators.AverageTrueRange(self.datas[0], period=self.p.atr_period)

        # Internal state
        self.bar_count = 0
        self.last_structure_update = 0
        self.structure_update_frequency = 10  # Update every N bars

    def log(self, txt: str, dt: Optional[bt.datetime.date] = None) -> None:
        """Enhanced logging function for the strategy."""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order: bt.Order) -> None:
        """Handle order notifications."""
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Remove from pending orders
        if order in self.pending_orders:
            self.pending_orders.remove(order)

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"BUY EXECUTED: Price: {order.executed.price:.2f}, " f"Size: {order.executed.size:.2f}, " f"Commission: {order.executed.comm:.2f}"
                )

                # Add to active trades
                self.active_trades.append(
                    {
                        "type": "long",
                        "entry_price": order.executed.price,
                        "size": order.executed.size,
                        "entry_time": len(self),
                    }
                )

            elif order.issell():
                self.log(
                    f"SELL EXECUTED: Price: {order.executed.price:.2f}, "
                    f"Size: {order.executed.size:.2f}, "
                    f"Commission: {order.executed.comm:.2f}"
                )

                # Add to active trades or close existing
                if not self.position:  # New short position
                    self.active_trades.append(
                        {
                            "type": "short",
                            "entry_price": order.executed.price,
                            "size": order.executed.size,
                            "entry_time": len(self),
                        }
                    )
                else:  # Closing existing position
                    if self.active_trades:
                        trade = self.active_trades.pop(0)
                        pnl = self._calculate_pnl(trade, order.executed.price)
                        self.log(f"TRADE CLOSED: PnL: {pnl:.2f}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            status_name = getattr(order.status, "name", str(order.status))
            self.log(f"Order {status_name}: {order}")

    def notify_trade(self, trade: bt.Trade) -> None:
        """Handle trade notifications."""
        if not trade.isclosed:
            return

        self.log(f"TRADE PROFIT: Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}")

    def _calculate_pnl(self, trade: Dict, exit_price: float) -> float:
        """Calculate PnL for a trade."""
        if trade["type"] == "long":
            return (exit_price - trade["entry_price"]) * trade["size"]
        else:  # short
            return (trade["entry_price"] - exit_price) * trade["size"]

    def _update_data_buffer(self) -> None:
        """Update the data buffer with current bar."""
        current_bar = {
            "Open": self.dataopen[0],
            "High": self.datahigh[0],
            "Low": self.datalow[0],
            "Close": self.dataclose[0],
            "Volume": self.datavolume[0],
            "DateTime": self.datas[0].datetime.datetime(0),
        }

        self.data_buffer.append(current_bar)

        # Maintain buffer size
        if len(self.data_buffer) > self.buffer_size:
            self.data_buffer.pop(0)

    def _get_dataframe(self) -> pd.DataFrame:
        """Convert data buffer to pandas DataFrame."""
        if len(self.data_buffer) < 10:
            return pd.DataFrame()

        df = pd.DataFrame(self.data_buffer)
        df.set_index("DateTime", inplace=True)
        return df

    def _update_market_structure(self) -> None:
        """Update market structure and zones."""
        df = self._get_dataframe()
        if df.empty or len(df) < 20:
            return

        # Detect market structure
        try:
            self.current_trend = self.market_detector.detect_structure(df)

            # Get supply and demand zones
            zones = self.market_detector.get_supply_demand_zones(df)

            # Update zones with timestamps and strengths
            self.supply_zones = []
            self.demand_zones = []

            for zone in zones.get("supply", []):
                if zone["strength"] >= self.p.zone_strength_threshold:
                    zone["last_updated"] = len(self)
                    self.supply_zones.append(zone)

            for zone in zones.get("demand", []):
                if zone["strength"] >= self.p.zone_strength_threshold:
                    zone["last_updated"] = len(self)
                    self.demand_zones.append(zone)

            # Limit number of zones
            self.supply_zones = self.supply_zones[: self.p.max_zones_to_track]
            self.demand_zones = self.demand_zones[: self.p.max_zones_to_track]

            self.log(
                f"Market Structure: {self.current_trend.value}, "
                f"Supply Zones: {len(self.supply_zones)}, "
                f"Demand Zones: {len(self.demand_zones)}"
            )

        except Exception as e:
            self.log(f"Error updating market structure: {e}")

    def _is_price_in_zone(self, price: float, zone: Dict) -> bool:
        """Check if price is within a zone."""
        return zone["lower"] <= price <= zone["upper"]

    def _detect_zone_retest(self) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Detect if price is retesting a supply or demand zone.

        Returns:
            Tuple of (zone_type, zone_dict) or (None, None)
        """
        current_price = self.dataclose[0]
        current_high = self.datahigh[0]
        current_low = self.datalow[0]

        # Check demand zones (for long entries)
        for zone in self.demand_zones:
            # Price touching or entering the zone
            if self._is_price_in_zone(current_price, zone) or self._is_price_in_zone(current_low, zone):
                return "demand", zone

        # Check supply zones (for short entries)
        for zone in self.supply_zones:
            # Price touching or entering the zone
            if self._is_price_in_zone(current_price, zone) or self._is_price_in_zone(current_high, zone):
                return "supply", zone

        return None, None

    def _detect_reversal_pattern(self, zone_type: str) -> bool:
        """
        Detect reversal pattern confirmation.

        Args:
            zone_type: 'demand' for bullish patterns, 'supply' for bearish patterns

        Returns:
            True if valid reversal pattern is detected
        """
        if not self.p.require_pattern_confirmation:
            return True

        df = self._get_dataframe()
        if df.empty or len(df) < 2:
            return False

        current_index = len(df) - 1

        try:
            if zone_type == "demand":
                # Look for bullish patterns
                if "bullish_engulfing" in self.p.allowed_patterns:
                    if self.pattern_detector.detect_bullish_engulfing(df, current_index):
                        self.log("BULLISH ENGULFING pattern detected at demand zone")
                        return True

                # Could add hammer pattern detection here
                # if 'hammer' in self.p.allowed_patterns:
                #     if self.pattern_detector.detect_hammer(df, current_index):
                #         return True

            elif zone_type == "supply":
                # Look for bearish patterns
                if "bearish_engulfing" in self.p.allowed_patterns:
                    if self.pattern_detector.detect_bearish_engulfing(df, current_index):
                        self.log("BEARISH ENGULFING pattern detected at supply zone")
                        return True

                # Could add shooting star pattern detection here
                # if 'shooting_star' in self.p.allowed_patterns:
                #     if self.pattern_detector.detect_shooting_star(df, current_index):
                #         return True

        except Exception as e:
            self.log(f"Error detecting pattern: {e}")

        return False

    def _calculate_position_size(self, stop_loss_distance: float) -> float:
        """
        Calculate position size based on risk management.

        Args:
            stop_loss_distance: Distance to stop loss in price units

        Returns:
            Position size
        """
        if stop_loss_distance <= 0:
            return 0

        # Calculate maximum risk amount
        portfolio_value = self.broker.getvalue()
        max_risk_amount = portfolio_value * self.p.max_risk_per_trade

        # Calculate position size
        position_size = max_risk_amount / stop_loss_distance

        # Ensure we don't exceed available cash
        available_cash = self.broker.getcash()
        current_price = self.dataclose[0]
        max_affordable_size = available_cash / current_price * 0.95  # 95% to leave buffer

        return min(position_size, max_affordable_size)

    def _place_long_order(self, zone: Dict) -> None:
        """Place a long order with stop-loss and take-profit."""
        if len(self.pending_orders) >= self.p.max_concurrent_trades:
            return

        current_price = self.dataclose[0]
        atr_value = self.atr[0] if self.atr[0] > 0 else current_price * 0.01

        # Calculate stop-loss (below the zone or current low)
        stop_loss = min(zone["lower"], current_price - atr_value * self.p.stop_loss_atr_mult)
        stop_loss_distance = current_price - stop_loss

        # Calculate take-profit
        take_profit = current_price + (stop_loss_distance * self.p.risk_reward_ratio)

        # Calculate position size
        position_size = self._calculate_position_size(stop_loss_distance)

        if position_size <= 0:
            self.log("Position size too small, skipping trade")
            return

        try:
            # Place market buy order
            order = self.buy(size=position_size)
            self.pending_orders.append(order)

            # Place stop-loss order
            stop_order = self.sell(size=position_size, exectype=bt.Order.Stop, price=stop_loss)
            self.pending_orders.append(stop_order)

            # Place take-profit order
            target_order = self.sell(size=position_size, exectype=bt.Order.Limit, price=take_profit)
            self.pending_orders.append(target_order)

            self.log(
                f"LONG SIGNAL: Entry: {current_price:.2f}, "
                f"Stop: {stop_loss:.2f}, Target: {take_profit:.2f}, "
                f"Size: {position_size:.2f}, Risk: {stop_loss_distance:.2f}"
            )

        except Exception as e:
            self.log(f"Error placing long order: {e}")

    def _place_short_order(self, zone: Dict) -> None:
        """Place a short order with stop-loss and take-profit."""
        if len(self.pending_orders) >= self.p.max_concurrent_trades:
            return

        current_price = self.dataclose[0]
        atr_value = self.atr[0] if self.atr[0] > 0 else current_price * 0.01

        # Calculate stop-loss (above the zone or current high)
        stop_loss = max(zone["upper"], current_price + atr_value * self.p.stop_loss_atr_mult)
        stop_loss_distance = stop_loss - current_price

        # Calculate take-profit
        take_profit = current_price - (stop_loss_distance * self.p.risk_reward_ratio)

        # Calculate position size
        position_size = self._calculate_position_size(stop_loss_distance)

        if position_size <= 0:
            self.log("Position size too small, skipping trade")
            return

        try:
            # Place market sell order
            order = self.sell(size=position_size)
            self.pending_orders.append(order)

            # Place stop-loss order
            stop_order = self.buy(size=position_size, exectype=bt.Order.Stop, price=stop_loss)
            self.pending_orders.append(stop_order)

            # Place take-profit order
            target_order = self.buy(size=position_size, exectype=bt.Order.Limit, price=take_profit)
            self.pending_orders.append(target_order)

            self.log(
                f"SHORT SIGNAL: Entry: {current_price:.2f}, "
                f"Stop: {stop_loss:.2f}, Target: {take_profit:.2f}, "
                f"Size: {position_size:.2f}, Risk: {stop_loss_distance:.2f}"
            )

        except Exception as e:
            self.log(f"Error placing short order: {e}")

    def next(self) -> None:
        """Main strategy logic called for each new bar."""
        self.bar_count += 1

        # Update data buffer
        self._update_data_buffer()

        # Update market structure periodically
        if (self.bar_count - self.last_structure_update) >= self.structure_update_frequency:
            self._update_market_structure()
            self.last_structure_update = self.bar_count

        # Skip if we don't have enough data or if we already have max positions
        if len(self.data_buffer) < 20 or len(self.pending_orders) >= self.p.max_concurrent_trades:
            return

        # Detect zone retest
        zone_type, zone = self._detect_zone_retest()

        if zone_type is None or zone is None:
            return

        # Check for reversal pattern confirmation
        if not self._detect_reversal_pattern(zone_type):
            return

        # Check trend alignment
        if zone_type == "demand" and self.current_trend == TrendType.DOWNTREND:
            # Counter-trend trade in downtrend - be more cautious
            self.log("Demand zone retest in downtrend - counter-trend trade")
        elif zone_type == "supply" and self.current_trend == TrendType.UPTREND:
            # Counter-trend trade in uptrend - be more cautious
            self.log("Supply zone retest in uptrend - counter-trend trade")

        # Place orders based on zone type
        if zone_type == "demand":
            self.log(f"DEMAND ZONE RETEST: Zone strength: {zone.get('strength', 0):.2f}, " f"Zone price: {zone['price']:.2f}")
            self._place_long_order(zone)
        elif zone_type == "supply":
            self.log(f"SUPPLY ZONE RETEST: Zone strength: {zone.get('strength', 0):.2f}, " f"Zone price: {zone['price']:.2f}")
            self._place_short_order(zone)
