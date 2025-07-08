#!/usr/bin/env python3
"""
Simple Real-time Trading Dashboard
Demonstrates the forex trading system in action
"""

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import json
import random
import time
from datetime import datetime, timedelta
import threading
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# Global state for the trading system
trading_state = {
    'is_running': True,
    'current_balance': 1000000,
    'initial_balance': 1000000,
    'total_trades': 0,
    'winning_trades': 0,
    'current_positions': [],
    'recent_trades': [],
    'equity_curve': [1000000],
    'daily_pnl': 0,
    'max_drawdown': 0,
    'peak_balance': 1000000,
    'last_update': datetime.now()
}

# Currency pairs and their current "prices"
currency_pairs = {
    'EURUSD': {'price': 1.1000, 'spread': 0.0005, 'volatility': 0.008},
    'GBPUSD': {'price': 1.3000, 'spread': 0.0008, 'volatility': 0.012},
    'USDJPY': {'price': 110.00, 'spread': 0.006, 'volatility': 0.010},
    'USDCHF': {'price': 0.9200, 'spread': 0.0007, 'volatility': 0.009},
    'AUDUSD': {'price': 0.7500, 'spread': 0.0009, 'volatility': 0.011}
}

def simulate_trading():
    """Simulate real-time trading activity"""
    global trading_state, currency_pairs
    
    while True:
        if trading_state['is_running']:
            # Update currency prices
            for pair, data in currency_pairs.items():
                change = random.gauss(0, data['volatility'] * data['price'] * 0.1)
                currency_pairs[pair]['price'] += change
            
            # Simulate new trade every 5-15 seconds
            if random.random() < 0.3:  # 30% chance per iteration
                execute_simulated_trade()
            
            # Update existing positions
            update_positions()
            
            trading_state['last_update'] = datetime.now()
        
        time.sleep(2)  # Update every 2 seconds

def execute_simulated_trade():
    """Execute a simulated trade"""
    global trading_state
    
    pair = random.choice(list(currency_pairs.keys()))
    signal = random.choice(['BUY', 'SELL'])
    strategy = random.choice(['RSI_Extreme', 'Breakout', 'News_Trading', 'Scalping'])
    
    # Position sizing
    risk_amount = trading_state['current_balance'] * 0.02  # 2% risk
    leverage = 2000
    position_size = risk_amount * leverage
    
    # Entry price
    entry_price = currency_pairs[pair]['price']
    
    # Simulate trade outcome
    confidence = random.uniform(0.6, 0.95)
    win_probability = 0.45 + (confidence * 0.25)
    is_winner = random.random() < win_probability
    
    if is_winner:
        pips_gained = random.uniform(5, 25)
        pnl = position_size * (pips_gained / 10000)
    else:
        pips_lost = random.uniform(3, 15)
        pnl = -position_size * (pips_lost / 10000)
    
    # Cap P&L to prevent unrealistic values
    pnl = max(min(pnl, trading_state['current_balance'] * 0.1), -trading_state['current_balance'] * 0.05)
    
    # Update balance
    trading_state['current_balance'] += pnl
    trading_state['current_balance'] = max(trading_state['current_balance'], 0)
    
    # Update statistics
    trading_state['total_trades'] += 1
    if is_winner:
        trading_state['winning_trades'] += 1
    
    trading_state['daily_pnl'] += pnl
    trading_state['equity_curve'].append(trading_state['current_balance'])
    
    # Keep only last 100 equity points
    if len(trading_state['equity_curve']) > 100:
        trading_state['equity_curve'] = trading_state['equity_curve'][-100:]
    
    # Update drawdown
    if trading_state['current_balance'] > trading_state['peak_balance']:
        trading_state['peak_balance'] = trading_state['current_balance']
    
    current_drawdown = (trading_state['peak_balance'] - trading_state['current_balance']) / trading_state['peak_balance'] * 100
    trading_state['max_drawdown'] = max(trading_state['max_drawdown'], current_drawdown)
    
    # Add to recent trades
    trade = {
        'id': trading_state['total_trades'],
        'pair': pair,
        'signal': signal,
        'strategy': strategy,
        'entry_price': entry_price,
        'pnl': pnl,
        'is_winner': is_winner,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'confidence': confidence
    }
    
    trading_state['recent_trades'].insert(0, trade)
    if len(trading_state['recent_trades']) > 20:
        trading_state['recent_trades'] = trading_state['recent_trades'][:20]

def update_positions():
    """Update existing positions (placeholder)"""
    # For demo purposes, we'll just simulate some open positions
    if len(trading_state['current_positions']) < 3 and random.random() < 0.1:
        position = {
            'pair': random.choice(list(currency_pairs.keys())),
            'type': random.choice(['BUY', 'SELL']),
            'size': random.uniform(10000, 50000),
            'entry_price': random.uniform(1.0, 1.5),
            'current_pnl': random.uniform(-500, 1500),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        trading_state['current_positions'].append(position)
    
    # Remove positions randomly
    if trading_state['current_positions'] and random.random() < 0.05:
        trading_state['current_positions'].pop(0)

# HTML Template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Forex Trading Bot - Live Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .status { 
            display: inline-block; 
            padding: 5px 15px; 
            background: #00ff00; 
            color: black; 
            border-radius: 20px; 
            font-weight: bold;
        }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: rgba(255,255,255,0.1); 
            border-radius: 15px; 
            padding: 20px; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 { margin-bottom: 15px; color: #ffd700; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .metric-value { font-weight: bold; font-size: 1.1em; }
        .positive { color: #00ff88; }
        .negative { color: #ff4444; }
        .trades-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .trades-table th, .trades-table td { 
            padding: 8px; 
            text-align: left; 
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .trades-table th { background: rgba(255,255,255,0.1); }
        .win { background: rgba(0,255,0,0.2); }
        .loss { background: rgba(255,0,0,0.2); }
        .chart-container { height: 200px; background: rgba(0,0,0,0.3); border-radius: 10px; margin: 10px 0; }
        .controls { text-align: center; margin: 20px 0; }
        .btn { 
            padding: 10px 20px; 
            margin: 0 10px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-weight: bold;
        }
        .btn-start { background: #00ff00; color: black; }
        .btn-stop { background: #ff4444; color: white; }
        .live-indicator { 
            display: inline-block; 
            width: 10px; 
            height: 10px; 
            background: #ff0000; 
            border-radius: 50%; 
            animation: blink 1s infinite;
        }
        @keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0.3; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Forex Trading Bot Dashboard</h1>
            <div class="status">
                <span class="live-indicator"></span> LIVE TRADING
            </div>
            <p>Real-time AI-Enhanced Trading System with 2000:1 Leverage</p>
        </div>

        <div class="controls">
            <button class="btn btn-stop" onclick="toggleTrading()">⏸️ Pause Trading</button>
            <button class="btn btn-start" onclick="resetSystem()">🔄 Reset System</button>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📊 Account Overview</h3>
                <div class="metric">
                    <span>Current Balance:</span>
                    <span class="metric-value" id="balance">Loading...</span>
                </div>
                <div class="metric">
                    <span>Daily P&L:</span>
                    <span class="metric-value" id="daily-pnl">Loading...</span>
                </div>
                <div class="metric">
                    <span>Total Return:</span>
                    <span class="metric-value" id="total-return">Loading...</span>
                </div>
                <div class="metric">
                    <span>Max Drawdown:</span>
                    <span class="metric-value" id="max-drawdown">Loading...</span>
                </div>
            </div>

            <div class="card">
                <h3>📈 Trading Statistics</h3>
                <div class="metric">
                    <span>Total Trades:</span>
                    <span class="metric-value" id="total-trades">Loading...</span>
                </div>
                <div class="metric">
                    <span>Win Rate:</span>
                    <span class="metric-value" id="win-rate">Loading...</span>
                </div>
                <div class="metric">
                    <span>Winning Trades:</span>
                    <span class="metric-value" id="winning-trades">Loading...</span>
                </div>
                <div class="metric">
                    <span>Last Update:</span>
                    <span class="metric-value" id="last-update">Loading...</span>
                </div>
            </div>

            <div class="card">
                <h3>💱 Live Currency Prices</h3>
                <div id="currency-prices">Loading...</div>
            </div>

            <div class="card">
                <h3>📋 Open Positions</h3>
                <div id="open-positions">Loading...</div>
            </div>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h3>🔄 Recent Trades</h3>
            <table class="trades-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Pair</th>
                        <th>Type</th>
                        <th>Strategy</th>
                        <th>P&L (IDR)</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody id="recent-trades">
                    <tr><td colspan="6">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let isTrading = true;

        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update account overview
                    document.getElementById('balance').textContent = 
                        new Intl.NumberFormat('id-ID').format(data.current_balance) + ' IDR';
                    
                    const dailyPnl = data.daily_pnl;
                    document.getElementById('daily-pnl').textContent = 
                        (dailyPnl >= 0 ? '+' : '') + new Intl.NumberFormat('id-ID').format(dailyPnl) + ' IDR';
                    document.getElementById('daily-pnl').className = 'metric-value ' + (dailyPnl >= 0 ? 'positive' : 'negative');
                    
                    const totalReturn = ((data.current_balance - data.initial_balance) / data.initial_balance * 100);
                    document.getElementById('total-return').textContent = 
                        (totalReturn >= 0 ? '+' : '') + totalReturn.toFixed(2) + '%';
                    document.getElementById('total-return').className = 'metric-value ' + (totalReturn >= 0 ? 'positive' : 'negative');
                    
                    document.getElementById('max-drawdown').textContent = data.max_drawdown.toFixed(2) + '%';
                    
                    // Update trading statistics
                    document.getElementById('total-trades').textContent = data.total_trades;
                    const winRate = data.total_trades > 0 ? (data.winning_trades / data.total_trades * 100) : 0;
                    document.getElementById('win-rate').textContent = winRate.toFixed(1) + '%';
                    document.getElementById('winning-trades').textContent = data.winning_trades;
                    document.getElementById('last-update').textContent = new Date(data.last_update).toLocaleTimeString();
                    
                    // Update currency prices
                    let pricesHtml = '';
                    for (const [pair, info] of Object.entries(data.currency_prices)) {
                        pricesHtml += `
                            <div class="metric">
                                <span>${pair}:</span>
                                <span class="metric-value">${info.price.toFixed(4)}</span>
                            </div>
                        `;
                    }
                    document.getElementById('currency-prices').innerHTML = pricesHtml;
                    
                    // Update open positions
                    let positionsHtml = '';
                    if (data.current_positions.length === 0) {
                        positionsHtml = '<p>No open positions</p>';
                    } else {
                        data.current_positions.forEach(pos => {
                            positionsHtml += `
                                <div class="metric">
                                    <span>${pos.pair} ${pos.type}:</span>
                                    <span class="metric-value ${pos.current_pnl >= 0 ? 'positive' : 'negative'}">
                                        ${(pos.current_pnl >= 0 ? '+' : '')}${pos.current_pnl.toFixed(0)} IDR
                                    </span>
                                </div>
                            `;
                        });
                    }
                    document.getElementById('open-positions').innerHTML = positionsHtml;
                    
                    // Update recent trades
                    let tradesHtml = '';
                    data.recent_trades.forEach(trade => {
                        tradesHtml += `
                            <tr class="${trade.is_winner ? 'win' : 'loss'}">
                                <td>${trade.timestamp}</td>
                                <td>${trade.pair}</td>
                                <td>${trade.signal}</td>
                                <td>${trade.strategy}</td>
                                <td>${(trade.pnl >= 0 ? '+' : '')}${new Intl.NumberFormat('id-ID').format(trade.pnl)}</td>
                                <td>${(trade.confidence * 100).toFixed(1)}%</td>
                            </tr>
                        `;
                    });
                    document.getElementById('recent-trades').innerHTML = tradesHtml || '<tr><td colspan="6">No trades yet</td></tr>';
                })
                .catch(error => console.error('Error updating dashboard:', error));
        }

        function toggleTrading() {
            isTrading = !isTrading;
            fetch('/api/toggle', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    const btn = document.querySelector('.btn-stop');
                    btn.textContent = data.is_running ? '⏸️ Pause Trading' : '▶️ Resume Trading';
                    btn.className = data.is_running ? 'btn btn-stop' : 'btn btn-start';
                });
        }

        function resetSystem() {
            if (confirm('Are you sure you want to reset the trading system?')) {
                fetch('/api/reset', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        alert('System reset successfully!');
                    });
            }
        }

        // Update dashboard every 2 seconds
        setInterval(updateDashboard, 2000);
        updateDashboard(); // Initial load
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def get_status():
    return jsonify({
        **trading_state,
        'currency_prices': currency_pairs,
        'last_update': trading_state['last_update'].isoformat()
    })

@app.route('/api/toggle', methods=['POST'])
def toggle_trading():
    trading_state['is_running'] = not trading_state['is_running']
    return jsonify({'is_running': trading_state['is_running']})

@app.route('/api/reset', methods=['POST'])
def reset_system():
    global trading_state
    trading_state.update({
        'current_balance': 1000000,
        'total_trades': 0,
        'winning_trades': 0,
        'current_positions': [],
        'recent_trades': [],
        'equity_curve': [1000000],
        'daily_pnl': 0,
        'max_drawdown': 0,
        'peak_balance': 1000000,
        'last_update': datetime.now()
    })
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    # Start the trading simulation in a background thread
    trading_thread = threading.Thread(target=simulate_trading, daemon=True)
    trading_thread.start()
    
    print("🚀 Starting Forex Trading Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("🔄 Trading simulation is running...")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

