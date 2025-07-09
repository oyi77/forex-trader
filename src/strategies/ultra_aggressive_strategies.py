"""
Ultra-Aggressive Trading Strategies
Designed to generate signals on every bar for maximum trading frequency
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any
import logging

from ..core.interfaces import TradingSignal
from ..core.base_classes import BaseSignalGenerator


class AlwaysTradingStrategy(BaseSignalGenerator):
    """
    Strategy that generates a signal on every single bar
    """
    
    def __init__(self, name: str = "ALWAYS_TRADING", **kwargs):
        super().__init__(name, kwargs)
        self.signal_count = 0
        self.last_signal = None
        
    def get_required_history(self) -> int:
        return 2  # Minimal history needed
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate signal on every bar"""
        try:
            if len(data) < 2:
                return None
            
            current_price = data['close'].iloc[-1]
            prev_price = data['close'].iloc[-2]
            
            self.signal_count += 1
            
            # Alternate between BUY and SELL every bar
            if self.signal_count % 2 == 1:
                signal = 'BUY'
                stop_loss = current_price * 0.99  # 1% stop loss
                take_profit = current_price * 1.02  # 2% take profit
            else:
                signal = 'SELL'
                stop_loss = current_price * 1.01  # 1% stop loss
                take_profit = current_price * 0.98  # 2% take profit
            
            confidence = 95.0  # Always maximum confidence
            
            return TradingSignal(
                pair=pair,
                signal=signal,
                price=current_price,
                timestamp=datetime.now(),
                confidence=confidence,
                strategy=self.name,
                stop_loss=stop_loss,
                take_profit=take_profit,
                metadata={'bar_count': self.signal_count}
            )
            
        except Exception as e:
            self.logger.warning(f"Error in AlwaysTradingStrategy: {e}")
            return None


class ScalpingMachineStrategy(BaseSignalGenerator):
    """
    Ultra-high frequency scalping strategy
    """
    
    def __init__(self, name: str = "SCALPING_MACHINE", **kwargs):
        super().__init__(name, kwargs)
        self.pip_target = 0.0001  # 1 pip target
        self.signal_threshold = 0.00001  # Extremely sensitive
        
    def get_required_history(self) -> int:
        return 3
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate scalping signals on tiny movements"""
        try:
            if len(data) < 3:
                return None
            
            current_price = data['close'].iloc[-1]
            prev_price = data['close'].iloc[-2]
            prev2_price = data['close'].iloc[-3]
            
            # Calculate micro-movements
            change1 = current_price - prev_price
            change2 = prev_price - prev2_price
            
            signal = None
            confidence = 90.0
            
            # Buy on any upward movement
            if change1 > 0 and change2 > 0:
                signal = 'BUY'
                stop_loss = current_price - (self.pip_target * 2)
                take_profit = current_price + self.pip_target
                
            # Sell on any downward movement
            elif change1 < 0 and change2 < 0:
                signal = 'SELL'
                stop_loss = current_price + (self.pip_target * 2)
                take_profit = current_price - self.pip_target
                
            # Random signal if no clear direction
            else:
                signal = 'BUY' if np.random.random() > 0.5 else 'SELL'
                if signal == 'BUY':
                    stop_loss = current_price * 0.999
                    take_profit = current_price * 1.001
                else:
                    stop_loss = current_price * 1.001
                    take_profit = current_price * 0.999
            
            if signal:
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'change1': change1, 'change2': change2}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error in ScalpingMachineStrategy: {e}")
            return None


class MomentumBlasterStrategy(BaseSignalGenerator):
    """
    Momentum strategy that trades on any price movement
    """
    
    def __init__(self, name: str = "MOMENTUM_BLASTER", **kwargs):
        super().__init__(name, kwargs)
        self.momentum_period = 2
        
    def get_required_history(self) -> int:
        return 5
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate momentum signals"""
        try:
            if len(data) < 5:
                return None
            
            current_price = data['close'].iloc[-1]
            
            # Calculate short-term momentum
            momentum = (current_price - data['close'].iloc[-3]) / data['close'].iloc[-3]
            
            # Calculate volatility
            returns = data['close'].pct_change().dropna()
            volatility = returns.std() if len(returns) > 1 else 0.01
            
            signal = None
            confidence = 85.0
            
            # Momentum threshold (very low to generate more signals)
            momentum_threshold = volatility * 0.1
            
            if momentum > momentum_threshold:
                signal = 'BUY'
                stop_loss = current_price * (1 - volatility * 2)
                take_profit = current_price * (1 + volatility * 3)
                
            elif momentum < -momentum_threshold:
                signal = 'SELL'
                stop_loss = current_price * (1 + volatility * 2)
                take_profit = current_price * (1 - volatility * 3)
                
            # Force a signal if no momentum detected
            else:
                # Use price position relative to recent range
                recent_high = data['high'].iloc[-5:].max()
                recent_low = data['low'].iloc[-5:].min()
                price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
                
                if price_position > 0.6:
                    signal = 'SELL'  # Near high, sell
                    stop_loss = current_price * 1.005
                    take_profit = current_price * 0.995
                else:
                    signal = 'BUY'   # Near low, buy
                    stop_loss = current_price * 0.995
                    take_profit = current_price * 1.005
            
            if signal:
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'momentum': momentum, 'volatility': volatility}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error in MomentumBlasterStrategy: {e}")
            return None


class VolatilityHunterStrategy(BaseSignalGenerator):
    """
    Strategy that hunts for volatility and trades aggressively
    """
    
    def __init__(self, name: str = "VOLATILITY_HUNTER", **kwargs):
        super().__init__(name, kwargs)
        self.vol_lookback = 10
        
    def get_required_history(self) -> int:
        return 15
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate volatility-based signals"""
        try:
            if len(data) < 15:
                return None
            
            current_price = data['close'].iloc[-1]
            
            # Calculate rolling volatility
            returns = data['close'].pct_change().dropna()
            current_vol = returns.iloc[-self.vol_lookback:].std() if len(returns) >= self.vol_lookback else 0.01
            avg_vol = returns.std() if len(returns) > 1 else 0.01
            
            # Calculate price range
            recent_data = data.iloc[-self.vol_lookback:]
            price_range = (recent_data['high'].max() - recent_data['low'].min()) / current_price
            
            signal = None
            confidence = 80.0
            
            # High volatility = more aggressive trading
            vol_multiplier = max(1.0, current_vol / avg_vol)
            
            # Direction based on recent price action
            short_ma = data['close'].iloc[-3:].mean()
            long_ma = data['close'].iloc[-10:].mean()
            
            if short_ma > long_ma:
                signal = 'BUY'
                stop_loss = current_price * (1 - price_range * 0.5)
                take_profit = current_price * (1 + price_range * vol_multiplier)
                
            else:
                signal = 'SELL'
                stop_loss = current_price * (1 + price_range * 0.5)
                take_profit = current_price * (1 - price_range * vol_multiplier)
            
            # Boost confidence in high volatility
            confidence = min(95.0, confidence + (vol_multiplier - 1) * 20)
            
            if signal:
                return TradingSignal(
                    pair=pair,
                    signal=signal,
                    price=current_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    strategy=self.name,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    metadata={'volatility': current_vol, 'vol_multiplier': vol_multiplier}
                )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error in VolatilityHunterStrategy: {e}")
            return None


class RandomWalkStrategy(BaseSignalGenerator):
    """
    Strategy that generates random signals with bias toward trends
    """
    
    def __init__(self, name: str = "RANDOM_WALK", **kwargs):
        super().__init__(name, kwargs)
        self.signal_probability = 0.8  # 80% chance to generate signal each bar
        
    def get_required_history(self) -> int:
        return 5
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate random signals with trend bias"""
        try:
            if len(data) < 5:
                return None
            
            # Only generate signal based on probability
            if np.random.random() > self.signal_probability:
                return None
            
            current_price = data['close'].iloc[-1]
            
            # Calculate trend bias
            trend = (data['close'].iloc[-1] - data['close'].iloc[-5]) / data['close'].iloc[-5]
            
            # Random signal with trend bias
            random_factor = np.random.random()
            
            if trend > 0:
                # Uptrend bias
                signal = 'BUY' if random_factor > 0.3 else 'SELL'
            else:
                # Downtrend bias
                signal = 'SELL' if random_factor > 0.3 else 'BUY'
            
            # Random stop loss and take profit
            stop_distance = np.random.uniform(0.005, 0.02)  # 0.5% to 2%
            profit_distance = np.random.uniform(0.01, 0.05)  # 1% to 5%
            
            if signal == 'BUY':
                stop_loss = current_price * (1 - stop_distance)
                take_profit = current_price * (1 + profit_distance)
            else:
                stop_loss = current_price * (1 + stop_distance)
                take_profit = current_price * (1 - profit_distance)
            
            confidence = np.random.uniform(70, 95)
            
            return TradingSignal(
                pair=pair,
                signal=signal,
                price=current_price,
                timestamp=datetime.now(),
                confidence=confidence,
                strategy=self.name,
                stop_loss=stop_loss,
                take_profit=take_profit,
                metadata={'trend': trend, 'random_factor': random_factor}
            )
            
        except Exception as e:
            self.logger.warning(f"Error in RandomWalkStrategy: {e}")
            return None


class AllInStrategy(BaseSignalGenerator):
    """
    All-in strategy that bets everything on every trade
    """
    
    def __init__(self, name: str = "ALL_IN", **kwargs):
        super().__init__(name, kwargs)
        self.trade_count = 0
        
    def get_required_history(self) -> int:
        return 3
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate all-in signals"""
        try:
            if len(data) < 3:
                return None
            
            self.trade_count += 1
            current_price = data['close'].iloc[-1]
            
            # Generate signal every 2-3 bars
            if self.trade_count % 2 != 0:
                return None
            
            # Simple price direction
            price_change = (current_price - data['close'].iloc[-3]) / data['close'].iloc[-3]
            
            if price_change > 0:
                signal = 'BUY'
                stop_loss = current_price * 0.95  # 5% stop loss
                take_profit = current_price * 1.10  # 10% take profit
            else:
                signal = 'SELL'
                stop_loss = current_price * 1.05  # 5% stop loss
                take_profit = current_price * 0.90  # 10% take profit
            
            confidence = 99.0  # Maximum confidence for all-in
            
            return TradingSignal(
                pair=pair,
                signal=signal,
                price=current_price,
                timestamp=datetime.now(),
                confidence=confidence,
                strategy=self.name,
                stop_loss=stop_loss,
                take_profit=take_profit,
                metadata={'trade_count': self.trade_count, 'price_change': price_change}
            )
            
        except Exception as e:
            self.logger.warning(f"Error in AllInStrategy: {e}")
            return None

