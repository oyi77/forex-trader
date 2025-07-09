"""
Enhanced Trading Strategies with Real Signal Generation
Implements actual trading logic for profitable signals
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from ..core.interfaces import ISignalGenerator, TradingSignal
from ..core.base_classes import BaseSignalGenerator


class EnhancedRSIStrategy(BaseSignalGenerator):
    """Enhanced RSI strategy with dynamic thresholds"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.period = config.get('period', 14) if config else 14
        self.oversold = config.get('oversold', 30) if config else 30
        self.overbought = config.get('overbought', 70) if config else 70
        self.confidence_threshold = config.get('confidence_threshold', 70) if config else 70
    
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        return self.period + 5
        
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate RSI-based trading signal"""
        try:
            if len(data) < self.period + 1:
                return None
            
            # Calculate RSI
            rsi = self._calculate_rsi(data['close'], self.period)
            current_rsi = rsi.iloc[-1]
            prev_rsi = rsi.iloc[-2]
            
            current_price = data['close'].iloc[-1]
            
            signal = None
            confidence = 0
            
            # RSI oversold condition (buy signal)
            if current_rsi < self.oversold and prev_rsi >= self.oversold:
                signal = 'BUY'
                confidence = min(95, 50 + (self.oversold - current_rsi) * 2)
                
                # Calculate stop loss and take profit
                atr = self._calculate_atr(data, 14)
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 3.0)
                
            # RSI overbought condition (sell signal)
            elif current_rsi > self.overbought and prev_rsi <= self.overbought:
                signal = 'SELL'
                confidence = min(95, 50 + (current_rsi - self.overbought) * 2)
                
                # Calculate stop loss and take profit
                atr = self._calculate_atr(data, 14)
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 3.0)
            
            if signal and confidence >= self.confidence_threshold:
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'rsi': current_rsi, 'atr': atr}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating RSI signal: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.001


class EnhancedMAStrategy(BaseSignalGenerator):
    """Enhanced Moving Average Crossover Strategy"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.fast_period = config.get('fast_period', 10) if config else 10
        self.slow_period = config.get('slow_period', 20) if config else 20
        self.confidence_threshold = config.get('confidence_threshold', 70) if config else 70
    
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        return self.slow_period + 5
        
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate MA crossover signal"""
        try:
            if len(data) < self.slow_period + 1:
                return None
            
            # Calculate moving averages
            fast_ma = data['close'].rolling(window=self.fast_period).mean()
            slow_ma = data['close'].rolling(window=self.slow_period).mean()
            
            current_fast = fast_ma.iloc[-1]
            current_slow = slow_ma.iloc[-1]
            prev_fast = fast_ma.iloc[-2]
            prev_slow = slow_ma.iloc[-2]
            
            current_price = data['close'].iloc[-1]
            
            signal = None
            confidence = 0
            
            # Bullish crossover
            if current_fast > current_slow and prev_fast <= prev_slow:
                signal = 'BUY'
                # Confidence based on separation and momentum
                separation = abs(current_fast - current_slow) / current_price
                momentum = (current_fast - prev_fast) / prev_fast
                confidence = min(95, 60 + separation * 10000 + momentum * 1000)
                
                atr = self._calculate_atr(data, 14)
                stop_loss = current_price - (atr * 2.0)
                take_profit = current_price + (atr * 4.0)
                
            # Bearish crossover
            elif current_fast < current_slow and prev_fast >= prev_slow:
                signal = 'SELL'
                separation = abs(current_fast - current_slow) / current_price
                momentum = abs(current_fast - prev_fast) / prev_fast
                confidence = min(95, 60 + separation * 10000 + momentum * 1000)
                
                atr = self._calculate_atr(data, 14)
                stop_loss = current_price + (atr * 2.0)
                take_profit = current_price - (atr * 4.0)
            
            if signal and confidence >= self.confidence_threshold:
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'fast_ma': current_fast, 'slow_ma': current_slow}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating MA signal: {e}")
            return None
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.001


class EnhancedBreakoutStrategy(BaseSignalGenerator):
    """Enhanced Breakout Strategy with volume confirmation"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.lookback_period = config.get('lookback_period', 20) if config else 20
        self.breakout_threshold = config.get('breakout_threshold', 0.02) if config else 0.02
        self.confidence_threshold = config.get('confidence_threshold', 75) if config else 75
    
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        return self.lookback_period + 5
        
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate breakout signal"""
        try:
            if len(data) < self.lookback_period + 1:
                return None
            
            # Calculate support and resistance levels
            recent_data = data.tail(self.lookback_period)
            resistance = recent_data['high'].max()
            support = recent_data['low'].min()
            
            current_price = data['close'].iloc[-1]
            current_high = data['high'].iloc[-1]
            current_low = data['low'].iloc[-1]
            
            signal = None
            confidence = 0
            
            # Bullish breakout
            if current_high > resistance:
                breakout_strength = (current_high - resistance) / resistance
                if breakout_strength >= self.breakout_threshold:
                    signal = 'BUY'
                    confidence = min(95, 70 + breakout_strength * 1000)
                    
                    atr = self._calculate_atr(data, 14)
                    stop_loss = support
                    take_profit = current_price + (current_price - support) * 2
                    
            # Bearish breakout
            elif current_low < support:
                breakout_strength = (support - current_low) / support
                if breakout_strength >= self.breakout_threshold:
                    signal = 'SELL'
                    confidence = min(95, 70 + breakout_strength * 1000)
                    
                    atr = self._calculate_atr(data, 14)
                    stop_loss = resistance
                    take_profit = current_price - (resistance - current_price) * 2
            
            if signal and confidence >= self.confidence_threshold:
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'resistance': resistance, 'support': support}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating breakout signal: {e}")
            return None
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.001


class ExtremeScalpingStrategy(BaseSignalGenerator):
    """Extreme scalping strategy for high-frequency trading"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.risk_multiplier = config.get('risk_multiplier', 10.0) if config else 10.0
        self.confidence_threshold = config.get('confidence_threshold', 90) if config else 90
        self.max_holding_minutes = config.get('max_holding_minutes', 5) if config else 5
    
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        return 10
        
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate extreme scalping signal"""
        try:
            if len(data) < 10:
                return None
            
            # Use very short-term momentum
            short_ma = data['close'].rolling(window=3).mean()
            current_ma = short_ma.iloc[-1]
            prev_ma = short_ma.iloc[-2]
            
            current_price = data['close'].iloc[-1]
            
            # Calculate micro-trend
            momentum = (current_ma - prev_ma) / prev_ma
            
            signal = None
            confidence = 0
            
            # Strong upward momentum
            if momentum > 0.001:  # 0.1% momentum threshold
                signal = 'BUY'
                confidence = min(95, 80 + momentum * 5000)
                
                # Very tight stops for scalping
                atr = self._calculate_atr(data, 5)
                stop_loss = current_price - (atr * 0.5)
                take_profit = current_price + (atr * 1.0)
                
            # Strong downward momentum
            elif momentum < -0.001:
                signal = 'SELL'
                confidence = min(95, 80 + abs(momentum) * 5000)
                
                atr = self._calculate_atr(data, 5)
                stop_loss = current_price + (atr * 0.5)
                take_profit = current_price - (atr * 1.0)
            
            if signal and confidence >= self.confidence_threshold:
                trading_signal = TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'momentum': momentum, 'risk_multiplier': self.risk_multiplier}
                )
                
                # Add max holding time for scalping
                trading_signal.max_holding_minutes = self.max_holding_minutes
                return trading_signal
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating scalping signal: {e}")
            return None
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.0001


class NewsExplosionStrategy(BaseSignalGenerator):
    """News-based explosive momentum strategy"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.risk_multiplier = config.get('risk_multiplier', 20.0) if config else 20.0
        self.news_impact_threshold = config.get('news_impact_threshold', 'HIGH') if config else 'HIGH'
        self.reaction_time_seconds = config.get('reaction_time_seconds', 5) if config else 5
    
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        return 5
        
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate news explosion signal based on sudden price movements"""
        try:
            if len(data) < 5:
                return None
            
            # Detect sudden price movements (news events)
            recent_prices = data['close'].tail(5)
            price_changes = recent_prices.pct_change().abs()
            max_change = price_changes.max()
            
            current_price = data['close'].iloc[-1]
            
            # News explosion threshold (0.5% sudden move)
            if max_change > 0.005:
                # Determine direction
                latest_change = recent_prices.iloc[-1] - recent_prices.iloc[-2]
                
                signal = 'BUY' if latest_change > 0 else 'SELL'
                confidence = min(95, 75 + max_change * 2000)
                
                # Aggressive targets for news trading
                atr = self._calculate_atr(data, 10)
                
                if signal == 'BUY':
                    stop_loss = current_price - (atr * 1.0)
                    take_profit = current_price + (atr * 5.0)
                else:
                    stop_loss = current_price + (atr * 1.0)
                    take_profit = current_price - (atr * 5.0)
                
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'price_explosion': max_change, 'risk_multiplier': self.risk_multiplier}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating news signal: {e}")
            return None
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.0001


class BreakoutMomentumStrategy(BaseSignalGenerator):
    """Breakout momentum strategy with volume confirmation"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.risk_multiplier = config.get('risk_multiplier', 15.0) if config else 15.0
        self.momentum_threshold = config.get('momentum_threshold', 0.03) if config else 0.03
        self.volume_confirmation = config.get('volume_confirmation', True) if config else True
    
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        return 20
        
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate breakout momentum signal"""
        try:
            if len(data) < 20:
                return None
            
            # Calculate momentum indicators
            recent_data = data.tail(20)
            bb_upper, bb_lower = self._calculate_bollinger_bands(recent_data['close'], 20, 2)
            
            current_price = data['close'].iloc[-1]
            
            signal = None
            confidence = 0
            
            # Breakout above upper Bollinger Band
            if current_price > bb_upper.iloc[-1]:
                momentum = (current_price - bb_upper.iloc[-1]) / bb_upper.iloc[-1]
                if momentum >= self.momentum_threshold:
                    signal = 'BUY'
                    confidence = min(95, 75 + momentum * 1000)
                    
                    atr = self._calculate_atr(data, 14)
                    stop_loss = bb_lower.iloc[-1]
                    take_profit = current_price + (current_price - bb_lower.iloc[-1]) * 2
                    
            # Breakout below lower Bollinger Band
            elif current_price < bb_lower.iloc[-1]:
                momentum = (bb_lower.iloc[-1] - current_price) / bb_lower.iloc[-1]
                if momentum >= self.momentum_threshold:
                    signal = 'SELL'
                    confidence = min(95, 75 + momentum * 1000)
                    
                    atr = self._calculate_atr(data, 14)
                    stop_loss = bb_upper.iloc[-1]
                    take_profit = current_price - (bb_upper.iloc[-1] - current_price) * 2
            
            if signal and confidence >= 75:
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'momentum': momentum, 'risk_multiplier': self.risk_multiplier}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating momentum signal: {e}")
            return None
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int, std_dev: float):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.0001


class MartingaleExtremeStrategy(BaseSignalGenerator):
    """Extreme Martingale recovery strategy"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.risk_multiplier = config.get('risk_multiplier', 50.0) if config else 50.0
        self.max_martingale_levels = config.get('max_levels', 8) if config else 8
        self.recovery_target = config.get('recovery_target', 0.1) if config else 0.1
        self.current_level = 0
        self.last_loss_price = None
    
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        return 20
        
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate Martingale recovery signal"""
        try:
            if len(data) < 10:
                return None
            
            current_price = data['close'].iloc[-1]
            
            # Simple mean reversion logic
            sma_20 = data['close'].rolling(window=20).mean().iloc[-1]
            deviation = abs(current_price - sma_20) / sma_20
            
            signal = None
            confidence = 0
            
            # Mean reversion opportunity
            if deviation > 0.01:  # 1% deviation from mean
                if current_price < sma_20:
                    signal = 'BUY'  # Price below mean, expect reversion up
                else:
                    signal = 'SELL'  # Price above mean, expect reversion down
                
                confidence = min(95, 70 + deviation * 1000)
                
                # Martingale position sizing (handled in risk manager)
                atr = self._calculate_atr(data, 14)
                
                if signal == 'BUY':
                    stop_loss = current_price - (atr * 2.0)
                    take_profit = sma_20 + (atr * 1.0)
                else:
                    stop_loss = current_price + (atr * 2.0)
                    take_profit = sma_20 - (atr * 1.0)
                
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={
                        'deviation': deviation,
                        'martingale_level': self.current_level,
                        'risk_multiplier': self.risk_multiplier
                    }
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error generating Martingale signal: {e}")
            return None
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.0001

