"""
Enhanced Signal Generator with AI Integration
Combines traditional technical analysis with machine learning for superior signal quality
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_strategy_core import EnhancedStrategyCore
from ai.ai_decision_engine import AIDecisionEngine

class EnhancedSignalGenerator:
    def __init__(self, config=None):
        self.config = config or {}
        self.strategy_core = EnhancedStrategyCore(config)
        self.ai_engine = AIDecisionEngine(config)
        
        # Signal generation parameters
        self.min_confidence = self.config.get('MIN_CONFIDENCE', 70)
        self.risk_per_trade = self.config.get('RISK_PER_TRADE', 0.01)
        self.max_risk_reward = self.config.get('MAX_RISK_REWARD', 3.0)
        self.min_risk_reward = self.config.get('MIN_RISK_REWARD', 1.5)
        
        # Strategy weights for different market regimes
        self.regime_weights = {
            'STRONG_UPTREND': {'trend_following': 0.7, 'mean_reversion': 0.2, 'breakout': 0.1},
            'STRONG_DOWNTREND': {'trend_following': 0.7, 'mean_reversion': 0.2, 'breakout': 0.1},
            'WEAK_UPTREND': {'trend_following': 0.5, 'mean_reversion': 0.3, 'breakout': 0.2},
            'WEAK_DOWNTREND': {'trend_following': 0.5, 'mean_reversion': 0.3, 'breakout': 0.2},
            'SIDEWAYS_RANGE': {'trend_following': 0.2, 'mean_reversion': 0.6, 'breakout': 0.2},
            'LOW_VOLATILITY_RANGE': {'trend_following': 0.1, 'mean_reversion': 0.7, 'breakout': 0.2},
            'HIGH_VOLATILITY_RANGE': {'trend_following': 0.3, 'mean_reversion': 0.4, 'breakout': 0.3}
        }
    
    def generate_enhanced_signal(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Optional[Dict]:
        """Generate enhanced trading signal with AI integration"""
        if df.empty or len(df) < 100:
            return None
        
        # Process data with all indicators
        processed_df = self.strategy_core.calculate_all_indicators(df)
        
        # Get market regime and strategy signals
        regime = self.strategy_core.calculate_market_regime(processed_df)
        strategy_signals = self.strategy_core.get_strategy_signals(processed_df)
        
        # Generate signals from different strategies
        trend_signal = self._generate_trend_following_signal(processed_df, strategy_signals)
        mean_reversion_signal = self._generate_mean_reversion_signal(processed_df, strategy_signals)
        breakout_signal = self._generate_breakout_signal(processed_df, strategy_signals)
        
        # Combine signals based on market regime
        combined_signal = self._combine_signals(
            trend_signal, mean_reversion_signal, breakout_signal, regime
        )
        
        if not combined_signal or combined_signal['signal_type'] == 'NONE':
            return None
        
        # Enhance with AI if models are trained
        if self.ai_engine.is_trained:
            ai_signal = self.ai_engine.predict_signal(processed_df, symbol, timeframe)
            combined_signal = self.ai_engine.enhance_signal(combined_signal, ai_signal)
        
        # Final validation and risk management
        validated_signal = self._validate_and_enhance_signal(
            combined_signal, processed_df, symbol, timeframe, regime
        )
        
        return validated_signal
    
    def _generate_trend_following_signal(self, df: pd.DataFrame, signals: Dict) -> Optional[Dict]:
        """Generate trend following signal"""
        latest = df.iloc[-1]
        
        # Trend following conditions
        bullish_conditions = [
            signals['trend_signals']['ema_trend'] == 'BULLISH',
            signals['trend_signals']['golden_cross'],
            signals['momentum_signals']['macd_signal'] == 'BULLISH',
            signals['trend_signals']['adx_strength'] > 20,
            latest.get('RSI', 50) > 40 and latest.get('RSI', 50) < 70,
            signals['structure_signals']['bos_bullish'] or signals['pattern_signals']['bullish_engulfing']
        ]
        
        bearish_conditions = [
            signals['trend_signals']['ema_trend'] == 'BEARISH',
            signals['trend_signals']['death_cross'],
            signals['momentum_signals']['macd_signal'] == 'BEARISH',
            signals['trend_signals']['adx_strength'] > 20,
            latest.get('RSI', 50) < 60 and latest.get('RSI', 50) > 30,
            signals['structure_signals']['bos_bearish'] or signals['pattern_signals']['bearish_engulfing']
        ]
        
        bullish_score = sum(bullish_conditions)
        bearish_score = sum(bearish_conditions)
        
        if bullish_score >= 4:
            return self._create_signal_template(
                'BUY', latest['close'], bullish_score * 15, 'TREND_FOLLOWING', df
            )
        elif bearish_score >= 4:
            return self._create_signal_template(
                'SELL', latest['close'], bearish_score * 15, 'TREND_FOLLOWING', df
            )
        
        return None
    
    def _generate_mean_reversion_signal(self, df: pd.DataFrame, signals: Dict) -> Optional[Dict]:
        """Generate mean reversion signal"""
        latest = df.iloc[-1]
        
        # Mean reversion conditions
        bullish_conditions = [
            signals['momentum_signals']['rsi_oversold'],
            latest.get('BB_Position', 0.5) < 0.2,  # Near lower Bollinger Band
            signals['pattern_signals']['bullish_pinbar'] or signals['pattern_signals']['bullish_engulfing'],
            latest.get('Stoch_K', 50) < 20,
            signals['divergence_signals']['bullish_divergence'],
            abs(latest.get('Distance_To_Support', 100)) < 2  # Near support
        ]
        
        bearish_conditions = [
            signals['momentum_signals']['rsi_overbought'],
            latest.get('BB_Position', 0.5) > 0.8,  # Near upper Bollinger Band
            signals['pattern_signals']['bearish_pinbar'] or signals['pattern_signals']['bearish_engulfing'],
            latest.get('Stoch_K', 50) > 80,
            signals['divergence_signals']['bearish_divergence'],
            abs(latest.get('Distance_To_Resistance', 100)) < 2  # Near resistance
        ]
        
        bullish_score = sum(bullish_conditions)
        bearish_score = sum(bearish_conditions)
        
        # Mean reversion requires stronger confluence
        if bullish_score >= 3:
            return self._create_signal_template(
                'BUY', latest['close'], bullish_score * 18, 'MEAN_REVERSION', df
            )
        elif bearish_score >= 3:
            return self._create_signal_template(
                'SELL', latest['close'], bearish_score * 18, 'MEAN_REVERSION', df
            )
        
        return None
    
    def _generate_breakout_signal(self, df: pd.DataFrame, signals: Dict) -> Optional[Dict]:
        """Generate breakout signal"""
        latest = df.iloc[-1]
        
        # Breakout conditions
        bullish_conditions = [
            signals['structure_signals']['bos_bullish'],
            latest.get('close') > latest.get('BB_Upper', latest.get('close')),
            latest.get('Volume_Ratio', 1) > 1.5,  # High volume
            signals['volatility_signals']['bb_squeeze'],  # Previous squeeze
            latest.get('ADX', 0) > 25,  # Strong momentum
            latest.get('RSI', 50) > 50  # Momentum confirmation
        ]
        
        bearish_conditions = [
            signals['structure_signals']['bos_bearish'],
            latest.get('close') < latest.get('BB_Lower', latest.get('close')),
            latest.get('Volume_Ratio', 1) > 1.5,  # High volume
            signals['volatility_signals']['bb_squeeze'],  # Previous squeeze
            latest.get('ADX', 0) > 25,  # Strong momentum
            latest.get('RSI', 50) < 50  # Momentum confirmation
        ]
        
        bullish_score = sum(bullish_conditions)
        bearish_score = sum(bearish_conditions)
        
        if bullish_score >= 3:
            return self._create_signal_template(
                'BUY', latest['close'], bullish_score * 16, 'BREAKOUT', df
            )
        elif bearish_score >= 3:
            return self._create_signal_template(
                'SELL', latest['close'], bearish_score * 16, 'BREAKOUT', df
            )
        
        return None
    
    def _create_signal_template(self, signal_type: str, entry_price: float, 
                              base_confidence: float, strategy_type: str, df: pd.DataFrame) -> Dict:
        """Create signal template with basic information"""
        latest = df.iloc[-1]
        atr_value = latest.get('ATR', 0.001)
        
        # Calculate stop loss and take profit
        if signal_type == 'BUY':
            stop_loss = self._calculate_dynamic_stop_loss(entry_price, True, atr_value, df)
            take_profits = self._calculate_dynamic_take_profits(entry_price, True, atr_value, df)
        else:
            stop_loss = self._calculate_dynamic_stop_loss(entry_price, False, atr_value, df)
            take_profits = self._calculate_dynamic_take_profits(entry_price, False, atr_value, df)
        
        # Calculate risk-reward ratio
        risk_reward = self._calculate_risk_reward_ratio(entry_price, stop_loss, take_profits[0], signal_type == 'BUY')
        
        return {
            'symbol': '',  # Will be filled by caller
            'timeframe': '',  # Will be filled by caller
            'timestamp': pd.Timestamp.now(),
            'signal_type': signal_type,
            'strategy_type': strategy_type,
            'entry_price': round(entry_price, 5),
            'stop_loss': round(stop_loss, 5),
            'take_profit': [round(tp, 5) for tp in take_profits],
            'risk_reward_ratio': round(risk_reward, 2),
            'confidence_score': min(100, base_confidence),
            'atr_value': atr_value,
            'market_regime': '',  # Will be filled by caller
            'expiry_time_hours': self._calculate_expiry_time(strategy_type),
            'position_size_pct': self._calculate_position_size(risk_reward),
            'alert_message': '',
            'status_tag': '#ENHANCED_SIGNAL',
            'emoji': '🚀' if signal_type == 'BUY' else '🔻'
        }
    
    def _combine_signals(self, trend_signal: Optional[Dict], mean_reversion_signal: Optional[Dict],
                        breakout_signal: Optional[Dict], regime: str) -> Optional[Dict]:
        """Combine signals based on market regime"""
        signals = [s for s in [trend_signal, mean_reversion_signal, breakout_signal] if s is not None]
        
        if not signals:
            return None
        
        # Get regime weights
        weights = self.regime_weights.get(regime, self.regime_weights['SIDEWAYS_RANGE'])
        
        # Calculate weighted scores for each signal type
        signal_scores = {}
        for signal in signals:
            strategy_type = signal['strategy_type']
            weight_key = strategy_type.lower().replace('_', '_')
            
            if strategy_type == 'TREND_FOLLOWING':
                weight = weights['trend_following']
            elif strategy_type == 'MEAN_REVERSION':
                weight = weights['mean_reversion']
            elif strategy_type == 'BREAKOUT':
                weight = weights['breakout']
            else:
                weight = 0.33
            
            signal_type = signal['signal_type']
            weighted_confidence = signal['confidence_score'] * weight
            
            if signal_type not in signal_scores:
                signal_scores[signal_type] = {'confidence': 0, 'signals': []}
            
            signal_scores[signal_type]['confidence'] += weighted_confidence
            signal_scores[signal_type]['signals'].append(signal)
        
        # Find the strongest signal
        best_signal_type = None
        best_confidence = 0
        
        for signal_type, data in signal_scores.items():
            if data['confidence'] > best_confidence:
                best_confidence = data['confidence']
                best_signal_type = signal_type
        
        if best_signal_type and best_confidence >= self.min_confidence:
            # Use the signal with highest individual confidence of the winning type
            best_individual_signal = max(
                signal_scores[best_signal_type]['signals'],
                key=lambda x: x['confidence_score']
            )
            
            # Update with combined confidence
            best_individual_signal['confidence_score'] = min(100, best_confidence)
            best_individual_signal['combined_signal'] = True
            best_individual_signal['contributing_strategies'] = [
                s['strategy_type'] for s in signal_scores[best_signal_type]['signals']
            ]
            
            return best_individual_signal
        
        return None
    
    def _calculate_dynamic_stop_loss(self, entry_price: float, is_buy: bool, 
                                   atr_value: float, df: pd.DataFrame) -> float:
        """Calculate dynamic stop loss based on market conditions"""
        latest = df.iloc[-1]
        
        # Base ATR multiplier
        atr_multiplier = 2.0
        
        # Adjust based on volatility
        bb_width = latest.get('BB_Width', 3)
        if bb_width > 5:  # High volatility
            atr_multiplier = 2.5
        elif bb_width < 2:  # Low volatility
            atr_multiplier = 1.5
        
        # Adjust based on ADX
        adx = latest.get('ADX', 20)
        if adx > 30:  # Strong trend
            atr_multiplier *= 1.2
        elif adx < 15:  # Weak trend
            atr_multiplier *= 0.8
        
        # Calculate stop loss
        if is_buy:
            # Look for recent support
            support_level = latest.get('Nearest_Support', entry_price * 0.99)
            atr_stop = entry_price - (atr_value * atr_multiplier)
            stop_loss = min(support_level * 0.999, atr_stop)  # Use tighter of the two
        else:
            # Look for recent resistance
            resistance_level = latest.get('Nearest_Resistance', entry_price * 1.01)
            atr_stop = entry_price + (atr_value * atr_multiplier)
            stop_loss = max(resistance_level * 1.001, atr_stop)  # Use tighter of the two
        
        return stop_loss
    
    def _calculate_dynamic_take_profits(self, entry_price: float, is_buy: bool,
                                      atr_value: float, df: pd.DataFrame) -> List[float]:
        """Calculate dynamic take profit levels"""
        latest = df.iloc[-1]
        
        # Base take profit levels
        tp_levels = []
        base_multipliers = [1.5, 2.5, 3.5]
        
        # Adjust multipliers based on market conditions
        adx = latest.get('ADX', 20)
        if adx > 30:  # Strong trend - extend targets
            base_multipliers = [2.0, 3.5, 5.0]
        elif adx < 15:  # Weak trend - conservative targets
            base_multipliers = [1.0, 1.8, 2.5]
        
        for multiplier in base_multipliers:
            if is_buy:
                tp = entry_price + (atr_value * multiplier)
                # Check against resistance levels
                resistance = latest.get('Nearest_Resistance', tp)
                if resistance and resistance < tp and (resistance - entry_price) / entry_price > 0.005:
                    tp = resistance * 0.999  # Just below resistance
            else:
                tp = entry_price - (atr_value * multiplier)
                # Check against support levels
                support = latest.get('Nearest_Support', tp)
                if support and support > tp and (entry_price - support) / entry_price > 0.005:
                    tp = support * 1.001  # Just above support
            
            tp_levels.append(tp)
        
        return tp_levels
    
    def _calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float,
                                   take_profit: float, is_buy: bool) -> float:
        """Calculate risk-reward ratio"""
        if is_buy:
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        
        if risk <= 0:
            return 0
        
        return reward / risk
    
    def _calculate_expiry_time(self, strategy_type: str) -> int:
        """Calculate signal expiry time based on strategy type"""
        expiry_times = {
            'TREND_FOLLOWING': 8,  # 8 hours
            'MEAN_REVERSION': 4,   # 4 hours
            'BREAKOUT': 6          # 6 hours
        }
        return expiry_times.get(strategy_type, 4)
    
    def _calculate_position_size(self, risk_reward_ratio: float) -> float:
        """Calculate position size as percentage of account"""
        base_size = self.risk_per_trade
        
        # Adjust based on risk-reward ratio
        if risk_reward_ratio >= 3.0:
            return min(base_size * 1.5, 0.02)  # Max 2%
        elif risk_reward_ratio >= 2.0:
            return base_size
        elif risk_reward_ratio >= 1.5:
            return base_size * 0.8
        else:
            return base_size * 0.5  # Reduce size for poor R:R
    
    def _validate_and_enhance_signal(self, signal: Dict, df: pd.DataFrame,
                                   symbol: str, timeframe: str, regime: str) -> Optional[Dict]:
        """Final validation and enhancement of signal"""
        if not signal:
            return None
        
        # Fill in missing information
        signal['symbol'] = symbol
        signal['timeframe'] = timeframe
        signal['market_regime'] = regime
        
        # Validate risk-reward ratio
        if signal['risk_reward_ratio'] < self.min_risk_reward:
            signal['confidence_score'] *= 0.7  # Reduce confidence for poor R:R
        
        # Validate confidence threshold
        if signal['confidence_score'] < self.min_confidence:
            return None
        
        # Create alert message
        signal['alert_message'] = self._create_alert_message(signal)
        
        # Add technical context
        latest = df.iloc[-1]
        signal['technical_context'] = {
            'rsi': latest.get('RSI', 50),
            'atr_ratio': latest.get('ATR', 0) / latest.get('close', 1) * 100,
            'bb_position': latest.get('BB_Position', 0.5),
            'volume_ratio': latest.get('Volume_Ratio', 1),
            'adx': latest.get('ADX', 20)
        }
        
        return signal
    
    def _create_alert_message(self, signal: Dict) -> str:
        """Create formatted alert message"""
        symbol = signal['symbol']
        signal_type = signal['signal_type']
        strategy = signal['strategy_type'].replace('_', ' ').title()
        entry = signal['entry_price']
        sl = signal['stop_loss']
        tp1 = signal['take_profit'][0]
        confidence = signal['confidence_score']
        rr = signal['risk_reward_ratio']
        
        message = (
            f"{signal['emoji']} {signal_type} {symbol} | {strategy}\n"
            f"Entry: {entry} | SL: {sl} | TP1: {tp1}\n"
            f"R:R: {rr} | Confidence: {confidence:.1f}%\n"
            f"Regime: {signal['market_regime']}"
        )
        
        return message
    
    def train_ai_models(self, historical_data: pd.DataFrame) -> bool:
        """Train AI models on historical data"""
        return self.ai_engine.train_models(historical_data)
    
    def save_ai_models(self, filepath_prefix: str = 'enhanced_ai_models') -> bool:
        """Save trained AI models"""
        return self.ai_engine.save_models(filepath_prefix)
    
    def load_ai_models(self, filepath_prefix: str = 'enhanced_ai_models') -> bool:
        """Load trained AI models"""
        return self.ai_engine.load_models(filepath_prefix)

# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=500, freq='H')
    
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(500).cumsum() + 100,
        'high': np.random.randn(500).cumsum() + 102,
        'low': np.random.randn(500).cumsum() + 98,
        'close': np.random.randn(500).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 500)
    })
    
    # Test Enhanced Signal Generator
    config = {
        'MIN_CONFIDENCE': 70,
        'RISK_PER_TRADE': 0.01,
        'MIN_RISK_REWARD': 1.5
    }
    
    signal_generator = EnhancedSignalGenerator(config)
    
    # Generate signal
    signal = signal_generator.generate_enhanced_signal(sample_data, "EURUSD", "1H")
    
    if signal:
        print("Generated Enhanced Signal:")
        for key, value in signal.items():
            print(f"{key}: {value}")
    else:
        print("No signal generated")
    
    # Test AI training (with sample data)
    print("\nTesting AI model training...")
    success = signal_generator.train_ai_models(sample_data)
    print(f"AI training success: {success}")
    
    if success:
        # Generate AI-enhanced signal
        ai_signal = signal_generator.generate_enhanced_signal(sample_data, "EURUSD", "1H")
        if ai_signal:
            print("\nAI-Enhanced Signal:")
            print(f"Confidence: {ai_signal['confidence_score']}")
            print(f"AI Enhancement: {ai_signal.get('ai_enhancement', 'None')}")

