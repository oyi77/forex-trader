"""
Extreme Leverage Trading Strategies
Optimized for 1:2000 leverage and IDR currency
Designed for aggressive growth targeting 2B IDR goal
"""

import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

from ..core.interfaces import TradingSignal
from ..core.base_classes import BaseSignalGenerator


class UltraScalpingStrategy(BaseSignalGenerator):
    """
    Ultra-high frequency scalping strategy
    Optimized for 1:2000 leverage with micro-movements
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = config.get('name', 'Ultra_Scalping')
        self.leverage = config.get('leverage', 2000)
        self.risk_per_trade = config.get('risk_per_trade', 0.20)  # 20% risk per trade
        self.min_pip_movement = config.get('min_pip_movement', 0.5)  # 0.5 pip minimum
        self.max_hold_time = config.get('max_hold_time', 300)  # 5 minutes max
        
        # Technical indicators
        self.rsi_period = 5  # Very short RSI
        self.ema_fast = 3    # 3-period EMA
        self.ema_slow = 8    # 8-period EMA
        self.bb_period = 10  # Bollinger Bands
        self.bb_std = 1.5    # BB standard deviation
        
        self.logger = logging.getLogger(__name__)
    
    def get_required_history(self) -> int:
        return max(self.rsi_period, self.ema_slow, self.bb_period) + 10
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate ultra-scalping signal"""
        try:
            if len(data) < self.get_required_history():
                return None
            
            # Calculate indicators
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            
            # RSI for momentum
            rsi = talib.RSI(close, timeperiod=self.rsi_period)
            
            # EMAs for trend
            ema_fast = talib.EMA(close, timeperiod=self.ema_fast)
            ema_slow = talib.EMA(close, timeperiod=self.ema_slow)
            
            # Bollinger Bands for volatility
            bb_upper, bb_middle, bb_lower = talib.BBANDS(
                close, timeperiod=self.bb_period, nbdevup=self.bb_std, nbdevdn=self.bb_std
            )
            
            # Current values
            current_price = close[-1]
            current_rsi = rsi[-1]
            current_ema_fast = ema_fast[-1]
            current_ema_slow = ema_slow[-1]
            current_bb_upper = bb_upper[-1]
            current_bb_lower = bb_lower[-1]
            
            # Signal conditions
            signal = None
            confidence = 0
            
            # Ultra-aggressive scalping conditions
            if (current_rsi < 25 and  # Oversold
                current_price < current_bb_lower and  # Below BB lower
                current_ema_fast > current_ema_slow):  # Trend reversal
                
                signal = "BUY"
                confidence = 85 + min(15, (25 - current_rsi))  # Higher confidence for more oversold
                
            elif (current_rsi > 75 and  # Overbought
                  current_price > current_bb_upper and  # Above BB upper
                  current_ema_fast < current_ema_slow):  # Trend reversal
                
                signal = "SELL"
                confidence = 85 + min(15, (current_rsi - 75))  # Higher confidence for more overbought
            
            if signal:
                # Calculate stop loss and take profit for scalping
                pip_value = self._get_pip_value(pair)
                
                if signal == "BUY":
                    stop_loss = current_price - (2 * pip_value)  # 2 pip stop loss
                    take_profit = current_price + (1 * pip_value)  # 1 pip take profit (1:2 risk/reward)
                else:
                    stop_loss = current_price + (2 * pip_value)
                    take_profit = current_price - (1 * pip_value)
                
                return TradingSignal(
                    symbol=pair,
                    action=signal,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=self.risk_per_trade,
                    confidence=confidence,
                    strategy_name=self.name,
                    timestamp=datetime.now(),
                    timeframe="1m",
                    reason=f"Ultra-scalping: RSI={current_rsi:.1f}, Price vs BB"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ultra scalping signal error: {e}")
            return None


class VolatilityExplosionStrategy(BaseSignalGenerator):
    """
    Volatility explosion strategy
    Captures sudden price movements with high leverage
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = config.get('name', 'Volatility_Explosion')
        self.leverage = config.get('leverage', 2000)
        self.risk_per_trade = config.get('risk_per_trade', 0.25)  # 25% risk per trade
        
        # Volatility parameters
        self.atr_period = 14
        self.volatility_threshold = 2.0  # 2x average volatility
        self.momentum_period = 5
        
        self.logger = logging.getLogger(__name__)
    
    def get_required_history(self) -> int:
        return max(self.atr_period, self.momentum_period) + 10
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate volatility explosion signal"""
        try:
            if len(data) < self.get_required_history():
                return None
            
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            volume = data.get('tick_volume', data.get('volume', np.ones(len(close)))).values
            
            # Calculate ATR for volatility
            atr = talib.ATR(high, low, close, timeperiod=self.atr_period)
            
            # Calculate momentum
            momentum = talib.MOM(close, timeperiod=self.momentum_period)
            
            # Calculate volume surge
            volume_ma = talib.SMA(volume, timeperiod=10)
            volume_ratio = volume[-1] / volume_ma[-1] if volume_ma[-1] > 0 else 1
            
            # Current values
            current_price = close[-1]
            current_atr = atr[-1]
            avg_atr = np.mean(atr[-10:])  # 10-period average ATR
            current_momentum = momentum[-1]
            
            # Detect volatility explosion
            volatility_ratio = current_atr / avg_atr if avg_atr > 0 else 1
            
            signal = None
            confidence = 0
            
            if (volatility_ratio > self.volatility_threshold and  # High volatility
                volume_ratio > 1.5 and  # Volume surge
                abs(current_momentum) > avg_atr * 0.5):  # Strong momentum
                
                if current_momentum > 0:
                    signal = "BUY"
                else:
                    signal = "SELL"
                
                # Confidence based on volatility and volume
                confidence = min(95, 70 + (volatility_ratio * 5) + (volume_ratio * 5))
            
            if signal:
                pip_value = self._get_pip_value(pair)
                
                # Wider stops for volatility
                if signal == "BUY":
                    stop_loss = current_price - (current_atr * 1.5)
                    take_profit = current_price + (current_atr * 3.0)  # 1:2 risk/reward
                else:
                    stop_loss = current_price + (current_atr * 1.5)
                    take_profit = current_price - (current_atr * 3.0)
                
                return TradingSignal(
                    symbol=pair,
                    action=signal,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=self.risk_per_trade,
                    confidence=confidence,
                    strategy_name=self.name,
                    timestamp=datetime.now(),
                    timeframe="5m",
                    reason=f"Volatility explosion: ATR ratio={volatility_ratio:.2f}, Volume={volume_ratio:.2f}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Volatility explosion signal error: {e}")
            return None


class MomentumSurgeStrategy(BaseSignalGenerator):
    """
    Momentum surge strategy
    Captures strong directional moves with maximum leverage
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = config.get('name', 'Momentum_Surge')
        self.leverage = config.get('leverage', 2000)
        self.risk_per_trade = config.get('risk_per_trade', 0.30)  # 30% risk per trade
        
        # Momentum parameters
        self.macd_fast = 5
        self.macd_slow = 13
        self.macd_signal = 4
        self.rsi_period = 8
        self.stoch_k = 5
        self.stoch_d = 3
        
        self.logger = logging.getLogger(__name__)
    
    def get_required_history(self) -> int:
        return max(self.macd_slow, self.rsi_period, self.stoch_k) + 10
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate momentum surge signal"""
        try:
            if len(data) < self.get_required_history():
                return None
            
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            
            # MACD for trend momentum
            macd, macd_signal, macd_hist = talib.MACD(
                close, fastperiod=self.macd_fast, slowperiod=self.macd_slow, signalperiod=self.macd_signal
            )
            
            # RSI for momentum strength
            rsi = talib.RSI(close, timeperiod=self.rsi_period)
            
            # Stochastic for momentum confirmation
            stoch_k, stoch_d = talib.STOCH(
                high, low, close, fastk_period=self.stoch_k, slowk_period=self.stoch_d, slowd_period=self.stoch_d
            )
            
            # Current values
            current_price = close[-1]
            current_macd = macd[-1]
            current_macd_signal = macd_signal[-1]
            current_macd_hist = macd_hist[-1]
            prev_macd_hist = macd_hist[-2]
            current_rsi = rsi[-1]
            current_stoch_k = stoch_k[-1]
            current_stoch_d = stoch_d[-1]
            
            signal = None
            confidence = 0
            
            # Strong bullish momentum
            if (current_macd > current_macd_signal and  # MACD above signal
                current_macd_hist > prev_macd_hist and  # MACD histogram increasing
                current_rsi > 60 and current_rsi < 85 and  # Strong but not overbought
                current_stoch_k > current_stoch_d and  # Stoch bullish
                current_stoch_k > 20):  # Not oversold
                
                signal = "BUY"
                confidence = 80 + min(15, (current_rsi - 60) / 2)
                
            # Strong bearish momentum
            elif (current_macd < current_macd_signal and  # MACD below signal
                  current_macd_hist < prev_macd_hist and  # MACD histogram decreasing
                  current_rsi < 40 and current_rsi > 15 and  # Weak but not oversold
                  current_stoch_k < current_stoch_d and  # Stoch bearish
                  current_stoch_k < 80):  # Not overbought
                
                signal = "SELL"
                confidence = 80 + min(15, (40 - current_rsi) / 2)
            
            if signal:
                pip_value = self._get_pip_value(pair)
                atr = talib.ATR(high, low, close, timeperiod=14)[-1]
                
                if signal == "BUY":
                    stop_loss = current_price - (atr * 2.0)
                    take_profit = current_price + (atr * 4.0)  # 1:2 risk/reward
                else:
                    stop_loss = current_price + (atr * 2.0)
                    take_profit = current_price - (atr * 4.0)
                
                return TradingSignal(
                    symbol=pair,
                    action=signal,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=self.risk_per_trade,
                    confidence=confidence,
                    strategy_name=self.name,
                    timestamp=datetime.now(),
                    timeframe="15m",
                    reason=f"Momentum surge: MACD={current_macd:.5f}, RSI={current_rsi:.1f}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Momentum surge signal error: {e}")
            return None


class GridRecoveryStrategy(BaseSignalGenerator):
    """
    Grid recovery strategy with Martingale elements
    Designed for maximum capital recovery with high leverage
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = config.get('name', 'Grid_Recovery')
        self.leverage = config.get('leverage', 2000)
        self.risk_per_trade = config.get('risk_per_trade', 0.35)  # 35% risk per trade
        
        # Grid parameters
        self.grid_size_pips = config.get('grid_size_pips', 10)  # 10 pip grid
        self.max_grid_levels = config.get('max_grid_levels', 5)  # Maximum 5 levels
        self.multiplier = config.get('multiplier', 1.5)  # 1.5x position size multiplier
        
        # Recovery tracking
        self.active_grids = {}  # Track active grid positions
        
        self.logger = logging.getLogger(__name__)
    
    def get_required_history(self) -> int:
        return 50
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate grid recovery signal"""
        try:
            if len(data) < self.get_required_history():
                return None
            
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            
            # Calculate trend direction
            sma_20 = talib.SMA(close, timeperiod=20)
            sma_50 = talib.SMA(close, timeperiod=50)
            
            current_price = close[-1]
            current_sma_20 = sma_20[-1]
            current_sma_50 = sma_50[-1]
            
            # Determine trend
            is_uptrend = current_sma_20 > current_sma_50
            is_downtrend = current_sma_20 < current_sma_50
            
            # Check for reversal patterns
            rsi = talib.RSI(close, timeperiod=14)
            current_rsi = rsi[-1]
            
            signal = None
            confidence = 0
            
            # Grid entry conditions
            if is_uptrend and current_rsi < 35:  # Uptrend pullback
                signal = "BUY"
                confidence = 75 + min(20, (35 - current_rsi))
                
            elif is_downtrend and current_rsi > 65:  # Downtrend pullback
                signal = "SELL"
                confidence = 75 + min(20, (current_rsi - 65))
            
            if signal:
                pip_value = self._get_pip_value(pair)
                grid_size = self.grid_size_pips * pip_value
                
                # Calculate grid levels
                if signal == "BUY":
                    stop_loss = current_price - (grid_size * self.max_grid_levels)
                    take_profit = current_price + (grid_size * 2)  # Conservative take profit
                else:
                    stop_loss = current_price + (grid_size * self.max_grid_levels)
                    take_profit = current_price - (grid_size * 2)
                
                return TradingSignal(
                    symbol=pair,
                    action=signal,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=self.risk_per_trade,
                    confidence=confidence,
                    strategy_name=self.name,
                    timestamp=datetime.now(),
                    timeframe="30m",
                    reason=f"Grid recovery: Trend={'UP' if is_uptrend else 'DOWN'}, RSI={current_rsi:.1f}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Grid recovery signal error: {e}")
            return None
    
    def _get_pip_value(self, pair: str) -> float:
        """Get pip value for the currency pair"""
        # Standard pip values (simplified)
        if 'JPY' in pair:
            return 0.01  # JPY pairs
        elif 'XAU' in pair or 'GOLD' in pair:
            return 0.1   # Gold
        else:
            return 0.0001  # Standard forex pairs


class NewsImpactStrategy(BaseSignalGenerator):
    """
    News impact strategy
    Captures price movements during high-impact news events
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = config.get('name', 'News_Impact')
        self.leverage = config.get('leverage', 2000)
        self.risk_per_trade = config.get('risk_per_trade', 0.40)  # 40% risk per trade
        
        # News detection parameters
        self.volume_threshold = 3.0  # 3x normal volume
        self.price_change_threshold = 0.002  # 0.2% price change
        self.time_window = 5  # 5-minute window
        
        self.logger = logging.getLogger(__name__)
    
    def get_required_history(self) -> int:
        return 30
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate news impact signal"""
        try:
            if len(data) < self.get_required_history():
                return None
            
            close = data['close'].values
            high = data['high'].values
            low = data['low'].values
            volume = data.get('tick_volume', data.get('volume', np.ones(len(close)))).values
            
            # Calculate recent price change
            price_change = (close[-1] - close[-self.time_window]) / close[-self.time_window]
            
            # Calculate volume surge
            recent_volume = np.mean(volume[-self.time_window:])
            normal_volume = np.mean(volume[-20:-self.time_window])
            volume_ratio = recent_volume / normal_volume if normal_volume > 0 else 1
            
            # Calculate volatility
            atr = talib.ATR(high, low, close, timeperiod=14)[-1]
            
            signal = None
            confidence = 0
            
            # Detect news impact
            if (abs(price_change) > self.price_change_threshold and
                volume_ratio > self.volume_threshold):
                
                if price_change > 0:
                    signal = "BUY"  # Continue the momentum
                else:
                    signal = "SELL"
                
                # Confidence based on strength of movement
                confidence = min(90, 70 + (abs(price_change) * 1000) + (volume_ratio * 5))
            
            if signal:
                current_price = close[-1]
                
                # Aggressive targets for news trading
                if signal == "BUY":
                    stop_loss = current_price - (atr * 1.0)
                    take_profit = current_price + (atr * 3.0)  # 1:3 risk/reward
                else:
                    stop_loss = current_price + (atr * 1.0)
                    take_profit = current_price - (atr * 3.0)
                
                return TradingSignal(
                    symbol=pair,
                    action=signal,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=self.risk_per_trade,
                    confidence=confidence,
                    strategy_name=self.name,
                    timestamp=datetime.now(),
                    timeframe="1m",
                    reason=f"News impact: Price change={price_change:.3%}, Volume ratio={volume_ratio:.2f}"
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"News impact signal error: {e}")
            return None

