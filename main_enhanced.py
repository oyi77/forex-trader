"""
Enhanced Forex Trading Bot - Main Entry Point
Integrates all components for automated forex trading with AI enhancement
"""

import pandas as pd
import numpy as np
import time
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import warnings
warnings.filterwarnings('ignore')

# Import enhanced components
from signals.enhanced_signal_generator import EnhancedSignalGenerator
from core.enhanced_strategy_core import EnhancedStrategyCore
from ai.ai_decision_engine import AIDecisionEngine
from data.data_manager import DataManager
from execution.execution_manager import ExecutionManager
from risk.risk_manager import RiskManager
from monitoring.performance_monitor import PerformanceMonitor

class EnhancedForexTradingBot:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the enhanced forex trading bot"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        
        # Initialize components
        self.signal_generator = EnhancedSignalGenerator(self.config)
        self.strategy_core = EnhancedStrategyCore(self.config)
        self.ai_engine = AIDecisionEngine(self.config)
        self.data_manager = DataManager(self.config)
        self.execution_manager = ExecutionManager(self.config)
        self.risk_manager = RiskManager(self.config)
        self.performance_monitor = PerformanceMonitor(self.config)
        
        # Trading state
        self.is_running = False
        self.active_positions = {}
        self.signal_history = []
        self.last_signal_time = {}
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        
        self.logger.info("Enhanced Forex Trading Bot initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from file"""
        try:
            import yaml
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            # Default configuration if file not found
            return {
                'SYMBOLS': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
                'TIMEFRAMES': ['1H', '4H'],
                'MIN_CONFIDENCE': 75,
                'RISK_PER_TRADE': 0.01,
                'MAX_DAILY_RISK': 0.05,
                'MAX_POSITIONS': 5,
                'MIN_RISK_REWARD': 1.5,
                'TRADING_HOURS': {'start': 0, 'end': 24},
                'AI_ENABLED': True,
                'BACKTESTING_MODE': False,
                'PAPER_TRADING': True,
                'LOG_LEVEL': 'INFO'
            }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('LOG_LEVEL', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('EnhancedForexBot')
    
    async def initialize_ai_models(self, historical_data_days: int = 365):
        """Initialize and train AI models"""
        self.logger.info("Initializing AI models...")
        
        try:
            # Try to load existing models first
            if self.ai_engine.load_models('enhanced_ai_models'):
                self.logger.info("Loaded existing AI models")
                return True
            
            # If no existing models, train new ones
            self.logger.info(f"Training new AI models with {historical_data_days} days of data...")
            
            # Get historical data for training
            training_data = await self._get_training_data(historical_data_days)
            
            if training_data is not None and len(training_data) > 1000:
                success = self.signal_generator.train_ai_models(training_data)
                if success:
                    # Save the trained models
                    self.signal_generator.save_ai_models('enhanced_ai_models')
                    self.logger.info("AI models trained and saved successfully")
                    return True
                else:
                    self.logger.warning("AI model training failed")
                    return False
            else:
                self.logger.warning("Insufficient training data for AI models")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing AI models: {e}")
            return False
    
    async def _get_training_data(self, days: int) -> Optional[pd.DataFrame]:
        """Get historical data for AI training"""
        try:
            # For demo purposes, generate synthetic training data
            # In production, this would fetch real historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Generate synthetic data with realistic forex characteristics
            np.random.seed(42)
            periods = days * 24  # Hourly data
            
            # Create realistic price movements
            returns = np.random.normal(0, 0.001, periods)  # Small hourly returns
            prices = 1.1000 + np.cumsum(returns)  # Starting at 1.1000 (EUR/USD)
            
            # Add some trend and volatility clustering
            trend = np.sin(np.arange(periods) / 100) * 0.01
            volatility = 0.0005 + 0.0005 * np.abs(np.sin(np.arange(periods) / 50))
            
            prices = prices + trend
            
            # Create OHLC data
            training_data = pd.DataFrame({
                'timestamp': pd.date_range(start=start_date, periods=periods, freq='H'),
                'open': prices + np.random.normal(0, volatility, periods),
                'high': prices + np.abs(np.random.normal(0, volatility, periods)),
                'low': prices - np.abs(np.random.normal(0, volatility, periods)),
                'close': prices,
                'volume': np.random.randint(1000, 10000, periods)
            })
            
            # Ensure high >= low and OHLC consistency
            training_data['high'] = training_data[['open', 'high', 'close']].max(axis=1)
            training_data['low'] = training_data[['open', 'low', 'close']].min(axis=1)
            
            self.logger.info(f"Generated {len(training_data)} periods of training data")
            return training_data
            
        except Exception as e:
            self.logger.error(f"Error generating training data: {e}")
            return None
    
    async def start_trading(self):
        """Start the main trading loop"""
        self.logger.info("Starting enhanced forex trading bot...")
        self.is_running = True
        
        # Initialize AI models
        ai_initialized = await self.initialize_ai_models()
        if not ai_initialized:
            self.logger.warning("AI models not initialized, continuing with traditional signals only")
        
        # Main trading loop
        while self.is_running:
            try:
                await self._trading_cycle()
                await asyncio.sleep(60)  # Wait 1 minute between cycles
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, stopping bot...")
                break
            except Exception as e:
                self.logger.error(f"Error in trading cycle: {e}")
                await asyncio.sleep(60)  # Wait before retrying
        
        await self.stop_trading()
    
    async def _trading_cycle(self):
        """Execute one complete trading cycle"""
        current_time = datetime.now()
        
        # Check trading hours
        if not self._is_trading_time(current_time):
            return
        
        # Update market data
        await self._update_market_data()
        
        # Check existing positions
        await self._manage_existing_positions()
        
        # Generate new signals
        await self._generate_and_process_signals()
        
        # Update performance metrics
        self._update_performance_metrics()
        
        # Log status
        self._log_status()
    
    def _is_trading_time(self, current_time: datetime) -> bool:
        """Check if current time is within trading hours"""
        trading_hours = self.config.get('TRADING_HOURS', {'start': 0, 'end': 24})
        current_hour = current_time.hour
        
        return trading_hours['start'] <= current_hour < trading_hours['end']
    
    async def _update_market_data(self):
        """Update market data for all symbols"""
        try:
            # In production, this would fetch real market data
            # For demo, we'll simulate data updates
            pass
        except Exception as e:
            self.logger.error(f"Error updating market data: {e}")
    
    async def _manage_existing_positions(self):
        """Manage existing trading positions"""
        try:
            for position_id, position in list(self.active_positions.items()):
                # Check if position should be closed
                if self._should_close_position(position):
                    await self._close_position(position_id)
                
                # Update position with current market data
                await self._update_position(position_id)
                
        except Exception as e:
            self.logger.error(f"Error managing positions: {e}")
    
    def _should_close_position(self, position: Dict) -> bool:
        """Determine if a position should be closed"""
        # Check expiry time
        if 'expiry_time' in position:
            if datetime.now() > position['expiry_time']:
                return True
        
        # Check stop loss and take profit (would be handled by broker in real trading)
        # This is simplified for demo purposes
        
        return False
    
    async def _close_position(self, position_id: str):
        """Close a trading position"""
        try:
            position = self.active_positions.get(position_id)
            if position:
                # In production, this would send close order to broker
                self.logger.info(f"Closing position {position_id}: {position['symbol']} {position['signal_type']}")
                
                # Update statistics
                self.total_trades += 1
                # Simplified P&L calculation for demo
                profit = np.random.uniform(-0.01, 0.02)  # Random profit/loss
                self.total_profit += profit
                
                if profit > 0:
                    self.winning_trades += 1
                
                # Remove from active positions
                del self.active_positions[position_id]
                
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
    
    async def _update_position(self, position_id: str):
        """Update position with current market data"""
        try:
            position = self.active_positions.get(position_id)
            if position:
                # Update with current price and P&L
                # In production, this would get real market data
                pass
        except Exception as e:
            self.logger.error(f"Error updating position {position_id}: {e}")
    
    async def _generate_and_process_signals(self):
        """Generate and process trading signals for all symbols"""
        symbols = self.config.get('SYMBOLS', ['EURUSD'])
        timeframes = self.config.get('TIMEFRAMES', ['1H'])
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # Check if we should generate signal for this symbol/timeframe
                    if not self._should_generate_signal(symbol, timeframe):
                        continue
                    
                    # Get market data
                    market_data = await self._get_market_data(symbol, timeframe)
                    if market_data is None or len(market_data) < 100:
                        continue
                    
                    # Generate enhanced signal
                    signal = self.signal_generator.generate_enhanced_signal(
                        market_data, symbol, timeframe
                    )
                    
                    if signal and signal['signal_type'] != 'NONE':
                        await self._process_signal(signal)
                    
                except Exception as e:
                    self.logger.error(f"Error generating signal for {symbol} {timeframe}: {e}")
    
    def _should_generate_signal(self, symbol: str, timeframe: str) -> bool:
        """Check if we should generate a signal for this symbol/timeframe"""
        # Avoid generating signals too frequently
        key = f"{symbol}_{timeframe}"
        last_signal = self.last_signal_time.get(key)
        
        if last_signal:
            time_diff = datetime.now() - last_signal
            min_interval = timedelta(hours=1)  # Minimum 1 hour between signals
            
            if time_diff < min_interval:
                return False
        
        # Check if we already have a position for this symbol
        for position in self.active_positions.values():
            if position['symbol'] == symbol:
                return False  # Don't open multiple positions for same symbol
        
        return True
    
    async def _get_market_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get market data for signal generation"""
        try:
            # For demo purposes, generate synthetic market data
            # In production, this would fetch real market data from broker/data provider
            
            periods = 200  # Get 200 periods for analysis
            np.random.seed(hash(symbol + timeframe) % 2**32)
            
            # Generate realistic forex data
            returns = np.random.normal(0, 0.001, periods)
            base_price = 1.1000 if 'EUR' in symbol else 1.3000
            prices = base_price + np.cumsum(returns)
            
            # Add some realistic patterns
            trend = np.sin(np.arange(periods) / 20) * 0.01
            prices = prices + trend
            
            # Create OHLC data
            volatility = 0.0005
            market_data = pd.DataFrame({
                'timestamp': pd.date_range(end=datetime.now(), periods=periods, freq='H'),
                'open': prices + np.random.normal(0, volatility, periods),
                'high': prices + np.abs(np.random.normal(0, volatility, periods)),
                'low': prices - np.abs(np.random.normal(0, volatility, periods)),
                'close': prices,
                'volume': np.random.randint(1000, 10000, periods)
            })
            
            # Ensure OHLC consistency
            market_data['high'] = market_data[['open', 'high', 'close']].max(axis=1)
            market_data['low'] = market_data[['open', 'low', 'close']].min(axis=1)
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data for {symbol} {timeframe}: {e}")
            return None
    
    async def _process_signal(self, signal: Dict):
        """Process a trading signal"""
        try:
            # Validate signal with risk management
            if not self.risk_manager.validate_signal(signal, self.active_positions):
                self.logger.info(f"Signal rejected by risk management: {signal['symbol']} {signal['signal_type']}")
                return
            
            # Check position limits
            if len(self.active_positions) >= self.config.get('MAX_POSITIONS', 5):
                self.logger.info("Maximum positions reached, skipping signal")
                return
            
            # Execute signal
            if self.config.get('PAPER_TRADING', True):
                await self._execute_paper_trade(signal)
            else:
                await self._execute_live_trade(signal)
            
            # Record signal
            self.signal_history.append(signal)
            self.last_signal_time[f"{signal['symbol']}_{signal['timeframe']}"] = datetime.now()
            
            self.logger.info(f"Processed signal: {signal['alert_message']}")
            
        except Exception as e:
            self.logger.error(f"Error processing signal: {e}")
    
    async def _execute_paper_trade(self, signal: Dict):
        """Execute a paper trade (simulation)"""
        try:
            position_id = f"{signal['symbol']}_{int(time.time())}"
            
            position = {
                'id': position_id,
                'symbol': signal['symbol'],
                'signal_type': signal['signal_type'],
                'entry_price': signal['entry_price'],
                'stop_loss': signal['stop_loss'],
                'take_profit': signal['take_profit'],
                'position_size': signal.get('position_size_pct', 0.01),
                'timestamp': datetime.now(),
                'expiry_time': datetime.now() + timedelta(hours=signal.get('expiry_time_hours', 4)),
                'confidence': signal['confidence_score'],
                'strategy_type': signal.get('strategy_type', 'UNKNOWN')
            }
            
            self.active_positions[position_id] = position
            self.logger.info(f"Paper trade executed: {position_id}")
            
        except Exception as e:
            self.logger.error(f"Error executing paper trade: {e}")
    
    async def _execute_live_trade(self, signal: Dict):
        """Execute a live trade (real money)"""
        try:
            # In production, this would place real orders through broker API
            self.logger.warning("Live trading not implemented - use paper trading mode")
            
        except Exception as e:
            self.logger.error(f"Error executing live trade: {e}")
    
    def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        try:
            # Calculate current drawdown
            if self.total_trades > 0:
                win_rate = self.winning_trades / self.total_trades
                avg_profit = self.total_profit / self.total_trades
                
                # Update max drawdown (simplified calculation)
                if self.total_profit < 0:
                    self.current_drawdown = abs(self.total_profit)
                    self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
                else:
                    self.current_drawdown = 0
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def _log_status(self):
        """Log current bot status"""
        try:
            active_count = len(self.active_positions)
            win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
            
            status_msg = (
                f"Status: Active Positions: {active_count}, "
                f"Total Trades: {self.total_trades}, "
                f"Win Rate: {win_rate:.1f}%, "
                f"Total P&L: {self.total_profit:.4f}, "
                f"Max DD: {self.max_drawdown:.4f}"
            )
            
            self.logger.info(status_msg)
            
        except Exception as e:
            self.logger.error(f"Error logging status: {e}")
    
    async def stop_trading(self):
        """Stop the trading bot"""
        self.logger.info("Stopping enhanced forex trading bot...")
        self.is_running = False
        
        # Close all active positions
        for position_id in list(self.active_positions.keys()):
            await self._close_position(position_id)
        
        # Save performance data
        self._save_performance_data()
        
        self.logger.info("Trading bot stopped successfully")
    
    def _save_performance_data(self):
        """Save performance data to file"""
        try:
            performance_data = {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'total_profit': self.total_profit,
                'max_drawdown': self.max_drawdown,
                'win_rate': (self.winning_trades / self.total_trades) if self.total_trades > 0 else 0,
                'signal_history': [
                    {k: str(v) if isinstance(v, datetime) else v for k, v in signal.items()}
                    for signal in self.signal_history[-100:]  # Save last 100 signals
                ]
            }
            
            with open('performance_data.json', 'w') as f:
                json.dump(performance_data, f, indent=2)
            
            self.logger.info("Performance data saved")
            
        except Exception as e:
            self.logger.error(f"Error saving performance data: {e}")
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        return {
            'is_running': self.is_running,
            'active_positions': len(self.active_positions),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': (self.winning_trades / self.total_trades) if self.total_trades > 0 else 0,
            'total_profit': self.total_profit,
            'max_drawdown': self.max_drawdown,
            'current_drawdown': self.current_drawdown
        }

# Demo/Testing functions
async def run_demo():
    """Run a demo of the enhanced trading bot"""
    print("Starting Enhanced Forex Trading Bot Demo...")
    
    # Create bot instance
    bot = EnhancedForexTradingBot()
    
    try:
        # Run for a short demo period
        demo_task = asyncio.create_task(bot.start_trading())
        
        # Let it run for 5 minutes for demo
        await asyncio.sleep(300)
        
        # Stop the bot
        bot.is_running = False
        await demo_task
        
        # Print final status
        status = bot.get_status()
        print("\nDemo completed!")
        print(f"Final Status: {status}")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        await bot.stop_trading()

def run_signal_test():
    """Test signal generation without full trading loop"""
    print("Testing Enhanced Signal Generation...")
    
    # Create signal generator
    signal_generator = EnhancedSignalGenerator()
    
    # Generate test data
    np.random.seed(42)
    test_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=200, freq='H'),
        'open': np.random.randn(200).cumsum() + 100,
        'high': np.random.randn(200).cumsum() + 102,
        'low': np.random.randn(200).cumsum() + 98,
        'close': np.random.randn(200).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 200)
    })
    
    # Generate signal
    signal = signal_generator.generate_enhanced_signal(test_data, "EURUSD", "1H")
    
    if signal:
        print("Signal Generated:")
        for key, value in signal.items():
            if key not in ['technical_context', 'ai_enhancement']:
                print(f"  {key}: {value}")
    else:
        print("No signal generated")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo
        asyncio.run(run_demo())
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run signal test
        run_signal_test()
    else:
        print("Enhanced Forex Trading Bot")
        print("Usage:")
        print("  python main_enhanced.py demo  - Run demo mode")
        print("  python main_enhanced.py test  - Test signal generation")
        print("  python main_enhanced.py       - Show this help")

