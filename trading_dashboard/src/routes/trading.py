"""
Trading API Routes for Forex Trading Bot Dashboard
Provides REST API endpoints for trading data, performance metrics, and controls
"""

from flask import Blueprint, jsonify, request
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import trading bot modules
try:
    from backtesting.backtest_engine import BacktestEngine, BacktestResults
    from strategies.strategy_validator import StrategyValidator
    from execution.broker_integration import BrokerIntegration, BrokerType
    from data.data_providers import DataProviderManager, DataProvider
    from ai.ai_decision_engine import AIDecisionEngine
    from risk.advanced_risk_manager import AdvancedRiskManager
except ImportError as e:
    logging.warning(f"Could not import trading modules: {e}")

trading_bp = Blueprint('trading', __name__)

# Global instances (in production, use proper dependency injection)
data_manager = None
broker = None
ai_engine = None
risk_manager = None
validator = None

# Mock data for demonstration
mock_performance_data = {
    'total_pnl': 1250.75,
    'total_return': 0.125,
    'win_rate': 0.68,
    'total_trades': 45,
    'sharpe_ratio': 1.85,
    'max_drawdown': -0.08,
    'current_positions': 3,
    'account_balance': 11250.75,
    'daily_pnl': [
        {'date': '2025-07-01', 'pnl': 125.50},
        {'date': '2025-07-02', 'pnl': -45.25},
        {'date': '2025-07-03', 'pnl': 89.75},
        {'date': '2025-07-04', 'pnl': 156.25},
        {'date': '2025-07-05', 'pnl': -23.50},
        {'date': '2025-07-06', 'pnl': 78.90},
        {'date': '2025-07-07', 'pnl': 234.15},
        {'date': '2025-07-08', 'pnl': 45.80}
    ]
}

mock_trades = [
    {
        'id': 1,
        'symbol': 'EURUSD',
        'side': 'buy',
        'entry_time': '2025-07-08 08:30:00',
        'exit_time': '2025-07-08 10:15:00',
        'entry_price': 1.1025,
        'exit_price': 1.1045,
        'quantity': 10000,
        'pnl': 200.0,
        'status': 'closed'
    },
    {
        'id': 2,
        'symbol': 'GBPUSD',
        'side': 'sell',
        'entry_time': '2025-07-08 09:45:00',
        'exit_time': None,
        'entry_price': 1.2850,
        'exit_price': None,
        'quantity': 5000,
        'pnl': -45.5,
        'status': 'open'
    },
    {
        'id': 3,
        'symbol': 'USDJPY',
        'side': 'buy',
        'entry_time': '2025-07-08 07:20:00',
        'exit_time': '2025-07-08 09:30:00',
        'entry_price': 146.25,
        'exit_price': 146.85,
        'quantity': 8000,
        'pnl': 480.0,
        'status': 'closed'
    }
]

mock_market_data = {
    'EURUSD': {'price': 1.1035, 'change': 0.0015, 'change_pct': 0.14},
    'GBPUSD': {'price': 1.2845, 'change': -0.0025, 'change_pct': -0.19},
    'USDJPY': {'price': 146.75, 'change': 0.45, 'change_pct': 0.31},
    'AUDUSD': {'price': 0.7520, 'change': 0.0008, 'change_pct': 0.11},
    'USDCHF': {'price': 0.9185, 'change': -0.0012, 'change_pct': -0.13},
    'NZDUSD': {'price': 0.6985, 'change': 0.0005, 'change_pct': 0.07}
}

@trading_bp.route('/status', methods=['GET'])
def get_trading_status():
    """Get overall trading bot status"""
    try:
        status = {
            'bot_active': True,
            'last_update': datetime.now().isoformat(),
            'strategies_running': ['RSI_Mean_Reversion', 'MA_Crossover'],
            'data_connection': 'connected',
            'broker_connection': 'connected',
            'ai_engine_status': 'active',
            'risk_manager_status': 'active',
            'uptime_hours': 24.5
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/performance', methods=['GET'])
def get_performance_metrics():
    """Get trading performance metrics"""
    try:
        return jsonify(mock_performance_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/trades', methods=['GET'])
def get_trades():
    """Get trading history and current positions"""
    try:
        status_filter = request.args.get('status', 'all')
        limit = int(request.args.get('limit', 50))
        
        filtered_trades = mock_trades
        if status_filter != 'all':
            filtered_trades = [t for t in mock_trades if t['status'] == status_filter]
        
        return jsonify({
            'trades': filtered_trades[:limit],
            'total_count': len(filtered_trades)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/market-data', methods=['GET'])
def get_market_data():
    """Get current market data for major currency pairs"""
    try:
        return jsonify(mock_market_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/equity-curve', methods=['GET'])
def get_equity_curve():
    """Get equity curve data for charting"""
    try:
        # Generate mock equity curve data
        start_date = datetime.now() - timedelta(days=30)
        dates = pd.date_range(start=start_date, end=datetime.now(), freq='H')
        
        # Simulate equity curve with some volatility
        np.random.seed(42)
        returns = np.random.normal(0.0001, 0.01, len(dates))
        equity_values = 10000 * np.exp(np.cumsum(returns))
        
        equity_data = [
            {
                'timestamp': date.isoformat(),
                'equity': float(equity),
                'drawdown': float(max(0, (max(equity_values[:i+1]) - equity) / max(equity_values[:i+1])) * 100)
            }
            for i, (date, equity) in enumerate(zip(dates, equity_values))
        ]
        
        return jsonify(equity_data[-168:])  # Last 7 days of hourly data
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/strategies', methods=['GET'])
def get_strategies():
    """Get available trading strategies and their performance"""
    try:
        strategies = [
            {
                'name': 'RSI_Mean_Reversion',
                'active': True,
                'performance': {
                    'total_return': 0.15,
                    'sharpe_ratio': 1.85,
                    'win_rate': 0.68,
                    'max_drawdown': -0.08
                },
                'last_signal': '2025-07-08 10:15:00',
                'confidence': 0.75
            },
            {
                'name': 'MA_Crossover',
                'active': True,
                'performance': {
                    'total_return': 0.08,
                    'sharpe_ratio': 1.25,
                    'win_rate': 0.55,
                    'max_drawdown': -0.12
                },
                'last_signal': '2025-07-08 09:45:00',
                'confidence': 0.62
            },
            {
                'name': 'Breakout_Strategy',
                'active': False,
                'performance': {
                    'total_return': 0.03,
                    'sharpe_ratio': 0.85,
                    'win_rate': 0.48,
                    'max_drawdown': -0.18
                },
                'last_signal': '2025-07-08 08:30:00',
                'confidence': 0.45
            }
        ]
        return jsonify(strategies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/risk-metrics', methods=['GET'])
def get_risk_metrics():
    """Get current risk metrics and exposure"""
    try:
        risk_metrics = {
            'current_exposure': 0.75,  # 75% of capital exposed
            'max_exposure_limit': 0.80,
            'var_95': -0.025,  # 2.5% VaR
            'expected_shortfall': -0.035,
            'correlation_risk': 0.45,
            'leverage_ratio': 2.5,
            'margin_utilization': 0.65,
            'risk_score': 6.5,  # Out of 10
            'position_sizes': {
                'EURUSD': 0.25,
                'GBPUSD': 0.15,
                'USDJPY': 0.20,
                'AUDUSD': 0.10,
                'USDCHF': 0.05
            }
        }
        return jsonify(risk_metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts and notifications"""
    try:
        alerts = [
            {
                'id': 1,
                'type': 'warning',
                'message': 'High correlation detected between EURUSD and GBPUSD positions',
                'timestamp': '2025-07-08 10:30:00',
                'severity': 'medium',
                'acknowledged': False
            },
            {
                'id': 2,
                'type': 'info',
                'message': 'RSI strategy generated new buy signal for USDJPY',
                'timestamp': '2025-07-08 10:15:00',
                'severity': 'low',
                'acknowledged': True
            },
            {
                'id': 3,
                'type': 'success',
                'message': 'EURUSD position closed with +200 pips profit',
                'timestamp': '2025-07-08 10:15:00',
                'severity': 'low',
                'acknowledged': True
            }
        ]
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        # In a real implementation, update the alert in the database
        return jsonify({'success': True, 'message': f'Alert {alert_id} acknowledged'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    try:
        # In a real implementation, start the trading bot
        return jsonify({'success': True, 'message': 'Trading bot started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    try:
        # In a real implementation, stop the trading bot
        return jsonify({'success': True, 'message': 'Trading bot stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/bot/restart', methods=['POST'])
def restart_bot():
    """Restart the trading bot"""
    try:
        # In a real implementation, restart the trading bot
        return jsonify({'success': True, 'message': 'Trading bot restarted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/strategies/<strategy_name>/toggle', methods=['POST'])
def toggle_strategy(strategy_name):
    """Enable or disable a trading strategy"""
    try:
        action = request.json.get('action', 'toggle')
        # In a real implementation, enable/disable the strategy
        return jsonify({
            'success': True, 
            'message': f'Strategy {strategy_name} {action}d',
            'strategy': strategy_name,
            'active': action == 'enable'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/backtest', methods=['POST'])
def run_backtest():
    """Run a backtest with specified parameters"""
    try:
        params = request.json
        strategy = params.get('strategy', 'RSI_Mean_Reversion')
        start_date = params.get('start_date', '2024-01-01')
        end_date = params.get('end_date', '2024-12-31')
        initial_capital = params.get('initial_capital', 10000)
        
        # Mock backtest results
        results = {
            'strategy': strategy,
            'period': f"{start_date} to {end_date}",
            'initial_capital': initial_capital,
            'final_capital': initial_capital * 1.15,
            'total_return': 0.15,
            'sharpe_ratio': 1.85,
            'max_drawdown': -0.08,
            'total_trades': 125,
            'win_rate': 0.68,
            'profit_factor': 1.85,
            'completed_at': datetime.now().isoformat()
        }
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/config', methods=['GET'])
def get_config():
    """Get current bot configuration"""
    try:
        config = {
            'risk_management': {
                'max_risk_per_trade': 0.02,
                'max_total_exposure': 0.80,
                'stop_loss_pct': 0.015,
                'take_profit_pct': 0.025
            },
            'trading_parameters': {
                'min_confidence': 0.65,
                'max_positions': 5,
                'position_sizing_method': 'kelly_criterion',
                'rebalance_frequency': 'daily'
            },
            'data_sources': {
                'primary_provider': 'twelve_data',
                'fallback_providers': ['fcs_api', 'free_forex_api'],
                'update_frequency': '1min'
            },
            'broker_settings': {
                'broker_type': 'paper_trading',
                'account_id': 'PAPER_ACCOUNT',
                'leverage': 100
            }
        }
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/config', methods=['POST'])
def update_config():
    """Update bot configuration"""
    try:
        new_config = request.json
        # In a real implementation, validate and save the configuration
        return jsonify({
            'success': True, 
            'message': 'Configuration updated successfully',
            'config': new_config
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@trading_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'database': 'healthy',
                'data_provider': 'healthy',
                'broker_connection': 'healthy',
                'ai_engine': 'healthy',
                'risk_manager': 'healthy'
            },
            'version': '1.0.0'
        }
        return jsonify(health_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

