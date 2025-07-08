#!/usr/bin/env python3
"""
Live Trading System for Exness MT5
Implements real-time trading with 1:2000 leverage for 2B IDR goal
"""

import sys
import os
import logging
import time
import signal
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import argparse
import yaml
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.brokers.exness_mt5 import create_exness_engine, ExnessConfig
from src.factories.strategy_factory import get_extreme_strategy_factory
from src.data.real_data_provider import RealDataProvider
from src.core.interfaces import TradingSignal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LiveTradingSystem:
    """
    Live trading system for Exness MT5
    Implements extreme strategies for 2B IDR goal
    """
    
    def __init__(self, config_file: str = "live_config.yaml"):
        self.config = self._load_config(config_file)
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Initialize components
        self.broker_engine = None
        self.strategy_factory = None
        self.data_provider = None
        self.strategies = []
        
        # Performance tracking
        self.start_time = None
        self.start_balance = 0.0
        self.current_balance = 0.0
        self.target_balance = 2000000000.0  # 2B IDR
        self.daily_targets = []
        
        # Risk management
        self.max_daily_loss = 0.2  # 20% max daily loss
        self.max_drawdown = 0.3    # 30% max drawdown
        self.emergency_stop = False
        
        logger.info("Live Trading System initialized")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = ['exness', 'trading', 'risk_management']
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required config section: {field}")
            
            return config
            
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_file}")
            # Create default config
            return self._create_default_config(config_file)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _create_default_config(self, config_file: str) -> Dict[str, Any]:
        """Create default configuration file"""
        default_config = {
            'exness': {
                'login': 0,  # User must set this
                'password': '',  # User must set this
                'server': 'Exness-MT5Real',
                'leverage': 2000,
                'base_currency': 'IDR'
            },
            'trading': {
                'initial_balance': 1000000,
                'target_balance': 2000000000,
                'target_days': 15,
                'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
                'strategies': [
                    {'name': 'Extreme_Scalping_1', 'type': 'EXTREME_SCALPING', 'weight': 0.3},
                    {'name': 'News_Explosion_1', 'type': 'NEWS_EXPLOSION', 'weight': 0.2},
                    {'name': 'Breakout_Momentum_1', 'type': 'BREAKOUT_MOMENTUM', 'weight': 0.3},
                    {'name': 'Martingale_Recovery_1', 'type': 'MARTINGALE_EXTREME', 'weight': 0.2}
                ]
            },
            'risk_management': {
                'max_risk_per_trade': 0.15,  # 15% per trade for extreme mode
                'max_daily_loss': 0.20,      # 20% max daily loss
                'max_drawdown': 0.30,        # 30% max drawdown
                'max_positions': 3,          # Maximum concurrent positions
                'emergency_stop_loss': 0.50  # 50% emergency stop
            },
            'monitoring': {
                'update_interval': 60,       # Update every 60 seconds
                'report_interval': 300,      # Report every 5 minutes
                'heartbeat_interval': 30     # Heartbeat every 30 seconds
            }
        }
        
        # Save default config
        os.makedirs(os.path.dirname(config_file) if os.path.dirname(config_file) else '.', exist_ok=True)
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        logger.warning(f"Created default config file: {config_file}")
        logger.warning("Please update the Exness login credentials before running!")
        
        return default_config
    
    def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            logger.info("Initializing live trading system...")
            
            # Create logs directory
            os.makedirs('logs', exist_ok=True)
            
            # Initialize broker engine
            self.broker_engine = create_exness_engine(
                login=self.config['exness']['login'],
                password=self.config['exness']['password'],
                server=self.config['exness']['server']
            )
            
            # Connect to broker
            if not self.broker_engine.connect():
                logger.error("Failed to connect to Exness MT5")
                return False
            
            # Get initial account info
            account_info = self.broker_engine.get_account_info()
            self.start_balance = account_info.get('balance', 0.0)
            self.current_balance = self.start_balance
            
            logger.info(f"Connected to Exness MT5")
            logger.info(f"Account Balance: {self.start_balance:,.2f} {account_info.get('currency', 'IDR')}")
            logger.info(f"Leverage: 1:{account_info.get('leverage', 2000)}")
            
            # Validate initial balance
            expected_balance = self.config['trading']['initial_balance']
            if abs(self.start_balance - expected_balance) > expected_balance * 0.1:  # 10% tolerance
                logger.warning(f"Balance mismatch: Expected {expected_balance}, Got {self.start_balance}")
            
            # Initialize strategy factory
            self.strategy_factory = get_extreme_strategy_factory()
            
            # Initialize data provider
            self.data_provider = RealDataProvider()
            
            # Create strategies
            self._initialize_strategies()
            
            # Calculate daily targets
            self._calculate_daily_targets()
            
            logger.info("Live trading system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def _initialize_strategies(self) -> None:
        """Initialize trading strategies"""
        try:
            self.strategies = []
            
            for strategy_config in self.config['trading']['strategies']:
                strategy = self.strategy_factory.create_strategy(
                    strategy_config['type'],
                    {
                        'name': strategy_config['name'],
                        'weight': strategy_config['weight'],
                        'risk_per_trade': self.config['risk_management']['max_risk_per_trade'],
                        'leverage': self.config['exness']['leverage']
                    }
                )
                self.strategies.append(strategy)
                logger.info(f"Initialized strategy: {strategy_config['name']}")
            
            logger.info(f"Initialized {len(self.strategies)} trading strategies")
            
        except Exception as e:
            logger.error(f"Strategy initialization failed: {e}")
            raise
    
    def _calculate_daily_targets(self) -> None:
        """Calculate daily return targets to reach 2B IDR"""
        target_days = self.config['trading']['target_days']
        target_balance = self.config['trading']['target_balance']
        
        # Calculate required daily return
        daily_multiplier = (target_balance / self.start_balance) ** (1 / target_days)
        daily_return_pct = (daily_multiplier - 1) * 100
        
        # Generate daily targets
        current_target = self.start_balance
        for day in range(target_days):
            current_target *= daily_multiplier
            self.daily_targets.append(current_target)
        
        logger.info(f"Target: {self.start_balance:,.0f} → {target_balance:,.0f} IDR in {target_days} days")
        logger.info(f"Required daily return: {daily_return_pct:.2f}%")
        logger.info(f"Day 1 target: {self.daily_targets[0]:,.0f} IDR")
    
    def start_trading(self) -> None:
        """Start live trading"""
        try:
            if self.config['exness']['login'] == 0:
                logger.error("Exness login not configured! Please update live_config.yaml")
                return
            
            logger.info("🚀 STARTING LIVE TRADING - REAL MONEY AT RISK! 🚀")
            logger.info("=" * 60)
            
            # Enable trading on broker
            if not self.broker_engine.enable_trading():
                logger.error("Failed to enable trading")
                return
            
            self.running = True
            self.start_time = datetime.now()
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            monitor_thread.start()
            
            # Start main trading loop
            self._trading_loop()
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop_trading()
        except Exception as e:
            logger.error(f"Trading error: {e}")
            self.stop_trading()
    
    def stop_trading(self) -> None:
        """Stop live trading"""
        logger.info("Stopping live trading...")
        
        self.running = False
        self.shutdown_event.set()
        
        if self.broker_engine:
            # Close all positions
            positions = self.broker_engine.get_positions()
            for position in positions:
                result = self.broker_engine.close_position(
                    str(position.ticket), 
                    "System shutdown"
                )
                if result.success:
                    logger.info(f"Closed position {position.ticket}")
                else:
                    logger.error(f"Failed to close position {position.ticket}: {result.error}")
            
            # Disable trading and disconnect
            self.broker_engine.disable_trading()
            self.broker_engine.disconnect()
        
        # Generate final report
        self._generate_final_report()
        
        logger.info("Live trading stopped")
    
    def _trading_loop(self) -> None:
        """Main trading loop"""
        update_interval = self.config['monitoring']['update_interval']
        last_update = datetime.now()
        
        while self.running and not self.shutdown_event.is_set():
            try:
                current_time = datetime.now()
                
                # Check if it's time to update
                if (current_time - last_update).seconds >= update_interval:
                    self._process_trading_cycle()
                    last_update = current_time
                
                # Check risk limits
                if self._check_risk_limits():
                    logger.warning("Risk limits exceeded - stopping trading")
                    break
                
                # Sleep briefly
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _process_trading_cycle(self) -> None:
        """Process one trading cycle"""
        try:
            # Update account info
            account_info = self.broker_engine.get_account_info()
            self.current_balance = account_info.get('balance', 0.0)
            
            # Get market data for all symbols
            symbols = self.config['trading']['symbols']
            market_data = {}
            
            for symbol in symbols:
                data = self.broker_engine.get_market_data(symbol, timeframe='1h', count=100)
                if data:
                    market_data[symbol] = data
            
            # Generate signals from strategies
            signals = []
            for strategy in self.strategies:
                for symbol in symbols:
                    if symbol in market_data:
                        signal = strategy.generate_signal(
                            market_data[symbol].historical_data, 
                            symbol
                        )
                        if signal:
                            signals.append(signal)
            
            # Execute signals
            for signal in signals:
                if self._should_execute_signal(signal):
                    result = self.broker_engine.execute_signal(signal)
                    if result.success:
                        logger.info(f"✅ Signal executed: {signal.action} {signal.symbol}")
                    else:
                        logger.warning(f"❌ Signal failed: {result.error}")
            
            # Log progress
            self._log_progress()
            
        except Exception as e:
            logger.error(f"Trading cycle error: {e}")
    
    def _should_execute_signal(self, signal: TradingSignal) -> bool:
        """Check if signal should be executed"""
        try:
            # Check if trading is enabled
            if not self.broker_engine.trading_enabled:
                return False
            
            # Check maximum positions
            positions = self.broker_engine.get_positions()
            max_positions = self.config['risk_management']['max_positions']
            
            if len(positions) >= max_positions:
                logger.debug(f"Max positions reached: {len(positions)}/{max_positions}")
                return False
            
            # Check if we already have a position in this symbol
            for position in positions:
                if position.symbol == signal.symbol:
                    logger.debug(f"Already have position in {signal.symbol}")
                    return False
            
            # Check signal confidence
            if signal.confidence < 70:  # Minimum 70% confidence
                logger.debug(f"Signal confidence too low: {signal.confidence}%")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Signal validation error: {e}")
            return False
    
    def _check_risk_limits(self) -> bool:
        """Check if risk limits are exceeded"""
        try:
            account_info = self.broker_engine.get_account_info()
            current_balance = account_info.get('balance', 0.0)
            equity = account_info.get('equity', 0.0)
            
            # Check daily loss limit
            daily_loss_pct = (self.start_balance - current_balance) / self.start_balance
            if daily_loss_pct > self.config['risk_management']['max_daily_loss']:
                logger.error(f"Daily loss limit exceeded: {daily_loss_pct:.2%}")
                return True
            
            # Check drawdown limit
            drawdown_pct = (self.start_balance - equity) / self.start_balance
            if drawdown_pct > self.config['risk_management']['max_drawdown']:
                logger.error(f"Drawdown limit exceeded: {drawdown_pct:.2%}")
                return True
            
            # Check emergency stop
            emergency_loss_pct = (self.start_balance - equity) / self.start_balance
            if emergency_loss_pct > self.config['risk_management']['emergency_stop_loss']:
                logger.error(f"EMERGENCY STOP: {emergency_loss_pct:.2%} loss")
                self.emergency_stop = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Risk check error: {e}")
            return True  # Err on the side of caution
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        report_interval = self.config['monitoring']['report_interval']
        last_report = datetime.now()
        
        while self.running and not self.shutdown_event.is_set():
            try:
                current_time = datetime.now()
                
                # Generate periodic reports
                if (current_time - last_report).seconds >= report_interval:
                    self._generate_status_report()
                    last_report = current_time
                
                # Heartbeat check
                if not self.broker_engine.is_connected():
                    logger.error("Lost connection to broker!")
                    self.running = False
                    break
                
                time.sleep(self.config['monitoring']['heartbeat_interval'])
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(30)
    
    def _log_progress(self) -> None:
        """Log current progress towards goal"""
        try:
            if not self.start_time:
                return
            
            elapsed_time = datetime.now() - self.start_time
            elapsed_days = elapsed_time.total_seconds() / 86400
            
            # Calculate current performance
            total_return_pct = ((self.current_balance - self.start_balance) / self.start_balance) * 100
            
            # Calculate required vs actual daily return
            if elapsed_days > 0:
                actual_daily_return = ((self.current_balance / self.start_balance) ** (1 / elapsed_days) - 1) * 100
            else:
                actual_daily_return = 0
            
            required_daily_return = ((self.target_balance / self.start_balance) ** (1 / self.config['trading']['target_days']) - 1) * 100
            
            logger.info(f"📊 Progress: {self.current_balance:,.0f} IDR ({total_return_pct:+.2f}%)")
            logger.info(f"⏱️  Elapsed: {elapsed_days:.2f} days")
            logger.info(f"📈 Daily Return: {actual_daily_return:.2f}% (Required: {required_daily_return:.2f}%)")
            
        except Exception as e:
            logger.error(f"Progress logging error: {e}")
    
    def _generate_status_report(self) -> None:
        """Generate detailed status report"""
        try:
            account_info = self.broker_engine.get_account_info()
            positions = self.broker_engine.get_positions()
            performance = self.broker_engine.get_performance_stats()
            
            logger.info("=" * 60)
            logger.info("📊 LIVE TRADING STATUS REPORT")
            logger.info("=" * 60)
            logger.info(f"💰 Balance: {account_info.get('balance', 0):,.2f} {account_info.get('currency', 'IDR')}")
            logger.info(f"💎 Equity: {account_info.get('equity', 0):,.2f} {account_info.get('currency', 'IDR')}")
            logger.info(f"📊 Margin: {account_info.get('margin', 0):,.2f} (Free: {account_info.get('free_margin', 0):,.2f})")
            logger.info(f"📈 Profit: {account_info.get('profit', 0):+,.2f} {account_info.get('currency', 'IDR')}")
            logger.info(f"🎯 Positions: {len(positions)}")
            logger.info(f"📊 Trades: {performance['total_trades']} (Success: {performance['success_rate']:.1f}%)")
            
            # Position details
            if positions:
                logger.info("📋 Open Positions:")
                for pos in positions:
                    logger.info(f"  {pos.symbol}: {pos.volume} lots, P&L: {pos.profit:+.2f}")
            
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Status report error: {e}")
    
    def _generate_final_report(self) -> None:
        """Generate final trading report"""
        try:
            if not self.start_time:
                return
            
            elapsed_time = datetime.now() - self.start_time
            total_return = self.current_balance - self.start_balance
            total_return_pct = (total_return / self.start_balance) * 100
            
            # Save report to file
            report_file = f"reports/live_trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            os.makedirs("reports", exist_ok=True)
            
            with open(report_file, 'w') as f:
                f.write("LIVE TRADING FINAL REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Trading Period: {self.start_time} to {datetime.now()}\n")
                f.write(f"Duration: {elapsed_time}\n\n")
                f.write(f"Initial Balance: {self.start_balance:,.2f} IDR\n")
                f.write(f"Final Balance: {self.current_balance:,.2f} IDR\n")
                f.write(f"Total Return: {total_return:+,.2f} IDR ({total_return_pct:+.2f}%)\n\n")
                f.write(f"Target Balance: {self.target_balance:,.2f} IDR\n")
                f.write(f"Goal Achievement: {(self.current_balance/self.target_balance)*100:.2f}%\n\n")
                
                # Performance stats
                performance = self.broker_engine.get_performance_stats()
                f.write("PERFORMANCE STATISTICS:\n")
                f.write(f"Total Trades: {performance['total_trades']}\n")
                f.write(f"Successful Trades: {performance['successful_trades']}\n")
                f.write(f"Failed Trades: {performance['failed_trades']}\n")
                f.write(f"Success Rate: {performance['success_rate']:.2f}%\n")
            
            logger.info(f"Final report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Final report error: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    if 'trading_system' in globals():
        trading_system.stop_trading()
    sys.exit(0)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Live Trading System for Exness MT5")
    parser.add_argument("--config", default="live_config.yaml", help="Configuration file")
    parser.add_argument("--demo", action="store_true", help="Demo mode (no real trades)")
    parser.add_argument("--validate", action="store_true", help="Validate configuration only")
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create trading system
        global trading_system
        trading_system = LiveTradingSystem(args.config)
        
        if args.validate:
            logger.info("Configuration validation completed")
            return
        
        # Initialize system
        if not trading_system.initialize():
            logger.error("System initialization failed")
            return
        
        if args.demo:
            logger.info("Running in DEMO mode - no real trades will be executed")
            trading_system.broker_engine.trading_enabled = False
        
        # Start trading
        trading_system.start_trading()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        if 'trading_system' in globals():
            trading_system.stop_trading()


if __name__ == "__main__":
    main()

