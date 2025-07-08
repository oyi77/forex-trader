#!/usr/bin/env python3
"""
Advanced Forex Trading Bot - Main Application
Implements SOLID principles with extreme trading capabilities
"""

import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

# Core imports
from src.core.interfaces import ITradingEngine, ISignalGenerator, IRiskManager
from src.core.base_classes import BaseRiskManager

# Factory imports
from src.factories.strategy_factory import get_strategy_factory
from src.factories.data_provider_factory import get_data_provider_factory
from src.factories.execution_factory import get_execution_factory
from src.config.configuration_manager import get_config_manager, create_extreme_preset


class ForexTradingBot:
    """Main Forex Trading Bot implementing SOLID principles"""
    
    def __init__(self, config_manager=None):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager or get_config_manager()
        self.data_provider = None
        self.execution_engine = None
        self.risk_manager = None
        self.strategies = []
        self.is_running = False
        self.session_id = None
        
    def initialize(self, mode: str = "conservative") -> bool:
        """Initialize the trading bot with specified mode"""
        try:
            self.logger.info(f"🚀 Initializing Forex Trading Bot - Mode: {mode}")
            
            # Load appropriate configuration
            if mode == "extreme":
                create_extreme_preset()
                self.config_manager.load_config_preset('extreme')
            else:
                self.config_manager.load_default_config()
            
            config = self.config_manager.get_trading_config()
            
            # Initialize components using factories
            self._initialize_data_provider(config)
            self._initialize_execution_engine(config)
            self._initialize_risk_manager(config)
            self._initialize_strategies(config, mode)
            
            self.logger.info("✅ Trading bot initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize trading bot: {e}")
            return False
    
    def _initialize_data_provider(self, config) -> None:
        """Initialize data provider using factory"""
        factory = get_data_provider_factory()
        self.data_provider = factory.create_provider(
            getattr(config, 'data_provider', 'MOCK'),
            getattr(config, 'data_provider_config', {})
        )
        self.logger.info(f"📊 Data provider initialized: {getattr(config, 'data_provider', 'MOCK')}")
    
    def _initialize_execution_engine(self, config) -> None:
        """Initialize execution engine using factory"""
        factory = get_execution_factory()
        self.execution_engine = factory.create_engine(
            getattr(config, 'execution_engine', 'PAPER'),
            {
                'leverage': getattr(config, 'leverage', 100),
                'account_balance': getattr(config, 'initial_balance', 1000000),
                'broker_config': getattr(config, 'broker_config', {})
            }
        )
        self.logger.info(f"⚡ Execution engine initialized: {getattr(config, 'execution_engine', 'PAPER')}")
    
    def _initialize_risk_manager(self, config) -> None:
        """Initialize risk manager"""
        try:
            from risk.risk_manager import RiskManager
            
            risk_config = self.config_manager.get_risk_config()
            
            self.risk_manager = RiskManager({
                'max_risk_per_trade': risk_config.max_risk_per_trade,
                'max_total_exposure': risk_config.max_total_exposure,
                'max_drawdown_threshold': risk_config.max_drawdown_stop,
                'position_sizing_method': risk_config.position_sizing_method
            })
            
        except ImportError:
            # Fallback to mock risk manager
            from core.base_classes import BaseRiskManager
            
            class MockRiskManager(BaseRiskManager):
                def __init__(self, config):
                    self.config = config
                
                def validate_trade(self, signal, current_positions):
                    return True
                
                def calculate_position_size(self, signal, account_balance):
                    return account_balance * self.config.get('max_risk_per_trade', 0.1)
                
                def should_emergency_stop(self, current_balance, initial_balance):
                    return current_balance < initial_balance * 0.2
            
            risk_config = self.config_manager.get_risk_config()
            self.risk_manager = MockRiskManager({
                'max_risk_per_trade': risk_config.max_risk_per_trade,
                'max_total_exposure': risk_config.max_total_exposure
            })
        
        self.logger.info("🛡️ Risk manager initialized")
    
    def _initialize_strategies(self, config, mode: str) -> None:
        """Initialize trading strategies using factory"""
        if mode == "extreme":
            factory = get_extreme_strategy_factory()
        else:
            factory = get_strategy_factory()
        
        self.strategies = []
        strategies_config = getattr(config, 'strategies', [
            {'type': 'RSI', 'name': 'RSI_Strategy', 'period': 14},
            {'type': 'MA_CROSSOVER', 'name': 'MA_Strategy', 'fast_period': 10, 'slow_period': 20}
        ])
        
        for strategy_config in strategies_config:
            try:
                strategy = factory.create_strategy(
                    strategy_config['type'],
                    strategy_config['name'],
                    strategy_config
                )
                if strategy:
                    self.strategies.append(strategy)
            except Exception as e:
                self.logger.error(f"Failed to create strategy {strategy_config['type']}: {e}")
        
        self.logger.info(f"🎯 Initialized {len(self.strategies)} trading strategies")
    
    def start_trading(self) -> bool:
        """Start the trading bot"""
        if not self.strategies:
            self.logger.error("❌ No strategies available for trading")
            return False
        
        self.is_running = True
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"🚀 Trading bot started - Session: {self.session_id}")
        return True
    
    def stop_trading(self) -> bool:
        """Stop the trading bot"""
        self.is_running = False
        self.logger.info("🛑 Trading bot stopped")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        config = self.config_manager.get_trading_config()
        return {
            'is_running': self.is_running,
            'session_id': self.session_id,
            'strategies_count': len(self.strategies),
            'open_positions': 0,  # TODO: Get from execution engine
            'account_balance': getattr(config, 'initial_balance', 1000000),
            'strategies': [getattr(s, 'name', 'Unknown') for s in self.strategies] if self.strategies else [],
            'last_update': datetime.now().isoformat()
        }
    
    def run_backtest(self, days: int = 30, leverage: int = 100) -> Dict[str, Any]:
        """Run comprehensive backtest"""
        self.logger.info(f"🧪 Starting backtest - Days: {days}, Leverage: {leverage}")
        
        # Import backtest functionality
        from test_system import run_comprehensive_backtest
        
        config = self.config_manager.get_trading_config()
        return run_comprehensive_backtest(
            initial_balance=getattr(config, 'initial_balance', 1000000),
            days=days,
            leverage=leverage,
            strategies=self.strategies,
            data_provider=self.data_provider,
            execution_engine=self.execution_engine,
            risk_manager=self.risk_manager
        )


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('forex_trading_bot.log')
        ]
    )


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Advanced Forex Trading Bot')
    parser.add_argument('--mode', choices=['conservative', 'moderate', 'aggressive', 'extreme'], 
                       default='conservative', help='Trading mode')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--backtest', action='store_true', help='Run backtest')
    parser.add_argument('--days', type=int, default=30, help='Backtest days')
    parser.add_argument('--leverage', type=int, default=100, help='Leverage ratio')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    print(f"🚀 Advanced Forex Trading Bot - Mode: {args.mode}")
    print("=" * 60)
    
    # Create and initialize bot
    bot = ForexTradingBot()
    
    if not bot.initialize(args.mode):
        print("❌ Failed to initialize trading bot")
        return 1
    
    if args.test:
        # Test mode
        status = bot.get_status()
        print(f"✅ Test mode - System status: {status}")
        print(f"🎯 Trading Bot - Test Successful!")
        print(f"📊 Strategies loaded: {status['strategies_count']}")
        print(f"💰 Account balance: {status['account_balance']:,.2f}")
        print(f"🎯 Active strategies: {', '.join(status['strategies'])}")
        return 0
    
    elif args.backtest:
        # Backtest mode
        print(f"🧪 Running backtest - Days: {args.days}, Leverage: {args.leverage}")
        results = bot.run_backtest(args.days, args.leverage)
        print("📊 Backtest completed! Check reports for detailed results.")
        return 0
    
    else:
        # Live trading mode
        if bot.start_trading():
            print("🚀 Trading bot started successfully!")
            print("Press Ctrl+C to stop...")
            try:
                # Keep running until interrupted
                import time
                while bot.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping trading bot...")
                bot.stop_trading()
        else:
            print("❌ Failed to start trading bot")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

