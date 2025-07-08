"""
Enhanced Trading API Routes for Extreme Forex Trading Bot
Supports real-time monitoring of 1:2000 leverage trading
"""

from flask import Blueprint, jsonify, request, current_app
import json
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import logging

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

try:
    from real_market_backtest import RealMarketBacktester
    from extreme_main import ExtremeForexTradingBot
except ImportError as e:
    print(f"Warning: Could not import trading modules: {e}")
    RealMarketBacktester = None
    ExtremeForexTradingBot = None

trading_bp = Blueprint('trading', __name__)

# Global variables for real-time trading
active_backtest = None
backtest_thread = None
live_data = {
    'status': 'stopped',
    'capital': 1000000,
    'trades': [],
    'equity_curve': [],
    'daily_returns': [],
    'current_positions': [],
    'performance_metrics': {},
    'leverage': 2000,
    'risk_per_trade': 60,
    'target_capital': 2000000000
}

@trading_bp.route('/api/trading/status', methods=['GET'])
def get_trading_status():
    """Get current trading status"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'trading_status': live_data['status'],
                'current_capital': live_data['capital'],
                'initial_capital': 1000000,
                'target_capital': live_data['target_capital'],
                'total_trades': len(live_data['trades']),
                'leverage': live_data['leverage'],
                'risk_per_trade': live_data['risk_per_trade'],
                'target_achieved': live_data['capital'] >= live_data['target_capital'],
                'last_update': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trading_bp.route('/api/trading/performance', methods=['GET'])
def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        trades = live_data['trades']
        
        if not trades:
            return jsonify({
                'status': 'success',
                'data': {
                    'total_return': 0,
                    'win_rate': 0,
                    'profit_factor': 0,
                    'max_drawdown': 0,
                    'sharpe_ratio': 0,
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'avg_daily_return': 0,
                    'best_day': 0,
                    'worst_day': 0
                }
            })
        
        # Calculate metrics
        winning_trades = sum(1 for trade in trades if trade.get('profit_idr', 0) > 0)
        losing_trades = len(trades) - winning_trades
        win_rate = winning_trades / len(trades) if trades else 0
        
        total_profit = sum(trade.get('profit_idr', 0) for trade in trades if trade.get('profit_idr', 0) > 0)
        total_loss = abs(sum(trade.get('profit_idr', 0) for trade in trades if trade.get('profit_idr', 0) < 0))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        total_return = (live_data['capital'] - 1000000) / 1000000
        
        daily_returns = live_data['daily_returns']
        avg_daily_return = np.mean(daily_returns) if daily_returns else 0
        best_day = max(daily_returns) if daily_returns else 0
        worst_day = min(daily_returns) if daily_returns else 0
        daily_volatility = np.std(daily_returns) if daily_returns else 0
        sharpe_ratio = avg_daily_return / daily_volatility if daily_volatility > 0 else 0
        
        # Calculate max drawdown
        equity_curve = live_data['equity_curve']
        max_drawdown = 0
        if equity_curve:
            peak = equity_curve[0]
            for value in equity_curve:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_return': total_return * 100,
                'win_rate': win_rate * 100,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown * 100,
                'sharpe_ratio': sharpe_ratio,
                'total_trades': len(trades),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'avg_daily_return': avg_daily_return * 100,
                'best_day': best_day * 100,
                'worst_day': worst_day * 100,
                'current_capital': live_data['capital'],
                'target_progress': (live_data['capital'] / live_data['target_capital']) * 100
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trading_bp.route('/api/trading/equity-curve', methods=['GET'])
def get_equity_curve():
    """Get equity curve data for charting"""
    try:
        equity_curve = live_data['equity_curve']
        
        # Create time series data
        data_points = []
        start_time = datetime.now() - timedelta(hours=len(equity_curve))
        
        for i, value in enumerate(equity_curve):
            timestamp = start_time + timedelta(hours=i)
            data_points.append({
                'timestamp': timestamp.isoformat(),
                'capital': value,
                'return_percent': ((value - 1000000) / 1000000) * 100
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'equity_curve': data_points,
                'target_line': live_data['target_capital']
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trading_bp.route('/api/trading/trades', methods=['GET'])
def get_recent_trades():
    """Get recent trades"""
    try:
        limit = request.args.get('limit', 50, type=int)
        trades = live_data['trades'][-limit:] if live_data['trades'] else []
        
        # Format trades for frontend
        formatted_trades = []
        for trade in trades:
            formatted_trades.append({
                'id': len(formatted_trades) + 1,
                'timestamp': trade.get('timestamp', datetime.now()).isoformat() if hasattr(trade.get('timestamp', datetime.now()), 'isoformat') else str(trade.get('timestamp', datetime.now())),
                'pair': trade.get('pair', 'UNKNOWN'),
                'signal': trade.get('signal', 'UNKNOWN'),
                'strategy': trade.get('strategy', 'UNKNOWN'),
                'entry_price': trade.get('entry_price', 0),
                'exit_price': trade.get('exit_price', 0),
                'position_size': trade.get('position_size', 0),
                'profit_idr': trade.get('profit_idr', 0),
                'profit_pips': trade.get('profit_pips', 0),
                'outcome': trade.get('outcome', 'UNKNOWN'),
                'confidence': trade.get('confidence', 0)
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'trades': formatted_trades,
                'total_count': len(live_data['trades'])
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trading_bp.route('/api/trading/start-backtest', methods=['POST'])
def start_backtest():
    """Start real-time backtest"""
    global active_backtest, backtest_thread
    
    try:
        if live_data['status'] == 'running':
            return jsonify({'status': 'error', 'message': 'Backtest already running'}), 400
        
        data = request.get_json() or {}
        initial_capital = data.get('initial_capital', 1000000)
        days = data.get('days', 7)
        
        # Reset live data
        live_data.update({
            'status': 'running',
            'capital': initial_capital,
            'trades': [],
            'equity_curve': [initial_capital],
            'daily_returns': [],
            'current_positions': []
        })
        
        # Start backtest in separate thread
        def run_backtest():
            global active_backtest
            try:
                if RealMarketBacktester:
                    active_backtest = RealMarketBacktester(initial_capital)
                    results = active_backtest.run_real_market_backtest(days)
                    
                    # Update final status
                    if results:
                        live_data.update({
                            'status': 'completed',
                            'capital': results['final_capital'],
                            'trades': results['trades'],
                            'equity_curve': results['equity_curve'],
                            'daily_returns': results['daily_returns']
                        })
                    else:
                        live_data['status'] = 'error'
                else:
                    # Simulate backtest if modules not available
                    simulate_backtest(initial_capital, days)
                    
            except Exception as e:
                live_data['status'] = 'error'
                print(f"Backtest error: {e}")
        
        backtest_thread = threading.Thread(target=run_backtest)
        backtest_thread.daemon = True
        backtest_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Backtest started',
            'data': {
                'initial_capital': initial_capital,
                'days': days,
                'leverage': live_data['leverage']
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def simulate_backtest(initial_capital: float, days: int):
    """Simulate backtest for demo purposes"""
    live_data['status'] = 'running'
    current_capital = initial_capital
    
    pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']
    
    for day in range(days):
        daily_start = current_capital
        
        # Simulate 8-12 trades per day
        trades_per_day = np.random.randint(8, 13)
        
        for trade_num in range(trades_per_day):
            if current_capital <= 0:
                break
                
            # Check if target reached
            if current_capital >= live_data['target_capital']:
                live_data['status'] = 'completed'
                return
            
            # Generate random trade
            pair = np.random.choice(pairs)
            signal = np.random.choice(['BUY', 'SELL'])
            strategy = np.random.choice(['EXTREME_SCALPING', 'NEWS_EXPLOSION', 'BREAKOUT_MOMENTUM', 'MARTINGALE'])
            
            # Simulate extreme returns with high volatility
            win_probability = 0.75  # 75% win rate
            
            if np.random.random() < win_probability:
                # Winning trade
                return_pct = np.random.uniform(0.5, 3.0)  # 50% to 300% return
                profit = current_capital * (return_pct / 100)
                outcome = 'WIN'
            else:
                # Losing trade
                loss_pct = np.random.uniform(0.3, 1.5)  # 30% to 150% loss
                profit = -current_capital * (loss_pct / 100)
                outcome = 'LOSS'
            
            current_capital += profit
            current_capital = max(0, current_capital)  # Prevent negative capital
            
            # Create trade record
            trade = {
                'timestamp': datetime.now(),
                'pair': pair,
                'signal': signal,
                'strategy': strategy,
                'entry_price': np.random.uniform(1.0, 1.5),
                'exit_price': np.random.uniform(1.0, 1.5),
                'position_size': np.random.uniform(0.1, 10.0),
                'profit_idr': profit,
                'profit_pips': abs(profit) / 10000,
                'outcome': outcome,
                'confidence': np.random.randint(85, 99)
            }
            
            # Update live data
            live_data['trades'].append(trade)
            live_data['equity_curve'].append(current_capital)
            live_data['capital'] = current_capital
            
            # Brief pause for real-time effect
            time.sleep(0.1)
        
        # Calculate daily return
        daily_return = (current_capital - daily_start) / daily_start
        live_data['daily_returns'].append(daily_return)
        
        # Brief pause between days
        time.sleep(0.5)
    
    live_data['status'] = 'completed'

@trading_bp.route('/api/trading/stop', methods=['POST'])
def stop_trading():
    """Stop current trading/backtest"""
    try:
        live_data['status'] = 'stopped'
        return jsonify({
            'status': 'success',
            'message': 'Trading stopped'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trading_bp.route('/api/trading/reset', methods=['POST'])
def reset_trading():
    """Reset trading data"""
    try:
        live_data.update({
            'status': 'stopped',
            'capital': 1000000,
            'trades': [],
            'equity_curve': [1000000],
            'daily_returns': [],
            'current_positions': []
        })
        
        return jsonify({
            'status': 'success',
            'message': 'Trading data reset'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@trading_bp.route('/api/trading/config', methods=['GET', 'POST'])
def trading_config():
    """Get or update trading configuration"""
    try:
        if request.method == 'GET':
            return jsonify({
                'status': 'success',
                'data': {
                    'leverage': live_data['leverage'],
                    'risk_per_trade': live_data['risk_per_trade'],
                    'target_capital': live_data['target_capital'],
                    'extreme_mode': True,
                    'martingale_enabled': True,
                    'news_trading_enabled': True,
                    'scalping_mode': True
                }
            })
        
        elif request.method == 'POST':
            data = request.get_json() or {}
            
            # Update configuration
            if 'leverage' in data:
                live_data['leverage'] = min(max(data['leverage'], 100), 2000)  # Cap between 100-2000
            if 'risk_per_trade' in data:
                live_data['risk_per_trade'] = min(max(data['risk_per_trade'], 1), 80)  # Cap between 1-80%
            if 'target_capital' in data:
                live_data['target_capital'] = max(data['target_capital'], 1000000)
            
            return jsonify({
                'status': 'success',
                'message': 'Configuration updated',
                'data': {
                    'leverage': live_data['leverage'],
                    'risk_per_trade': live_data['risk_per_trade'],
                    'target_capital': live_data['target_capital']
                }
            })
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

