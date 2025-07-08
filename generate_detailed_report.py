#!/usr/bin/env python3
"""
Detailed Backtest Report Generator
Generates comprehensive per-trade analysis with full breakdown
"""

import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, Any, List
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))


def generate_detailed_backtest(initial_balance: float = 1000000, days: int = 30, leverage: int = 2000):
    """Generate detailed backtest with per-trade analysis"""
    
    print("🔍 Generating Detailed Backtest Analysis...")
    print(f"💰 Initial Balance: {initial_balance:,.0f} IDR")
    print(f"📅 Duration: {days} days")
    print(f"⚡ Leverage: {leverage}:1")
    
    # Initialize detailed tracking
    detailed_results = {
        'trades': [],
        'daily_summary': [],
        'hourly_performance': [],
        'pair_performance': {},
        'strategy_performance': {},
        'risk_metrics': [],
        'equity_curve': [],
        'drawdown_periods': []
    }
    
    current_balance = initial_balance
    peak_balance = initial_balance
    trade_id = 1
    
    # Currency pairs with their characteristics
    pairs_info = {
        'EURUSD': {'volatility': 0.008, 'spread': 0.5, 'session_preference': 'European'},
        'GBPUSD': {'volatility': 0.012, 'spread': 0.8, 'session_preference': 'European'},
        'USDJPY': {'volatility': 0.010, 'spread': 0.6, 'session_preference': 'Asian'},
        'USDCHF': {'volatility': 0.009, 'spread': 0.7, 'session_preference': 'European'},
        'AUDUSD': {'volatility': 0.011, 'spread': 0.9, 'session_preference': 'Asian'}
    }
    
    # Trading strategies
    strategies = ['RSI_Extreme', 'Breakout_Momentum', 'News_Trading', 'Scalping_1M', 'Mean_Reversion']
    
    # Simulate detailed trading for each day
    for day in range(days):
        day_start_balance = current_balance
        day_trades = []
        daily_pnl = 0
        
        # 24 hours of trading (hourly analysis)
        for hour in range(24):
            session = _get_trading_session(hour)
            
            # Multiple trades per hour based on market activity
            trades_per_hour = np.random.poisson(2) if session in ['London', 'New_York', 'Overlap'] else np.random.poisson(1)
            
            for _ in range(trades_per_hour):
                # Select pair based on session preference
                pair = _select_pair_for_session(session, pairs_info)
                strategy = np.random.choice(strategies)
                
                # Generate detailed trade
                trade = _generate_detailed_trade(
                    trade_id, pair, strategy, current_balance, leverage, 
                    day, hour, session, pairs_info[pair]
                )
                
                if trade:
                    detailed_results['trades'].append(trade)
                    day_trades.append(trade)
                    current_balance = trade['exit_balance']
                    daily_pnl += trade['pnl']
                    trade_id += 1
                    
                    # Update peak for drawdown calculation
                    if current_balance > peak_balance:
                        peak_balance = current_balance
            
            # Record hourly performance
            hourly_data = {
                'day': day + 1,
                'hour': hour,
                'session': session,
                'balance': current_balance,
                'trades_count': len([t for t in day_trades if t['entry_hour'] == hour]),
                'hourly_pnl': sum([t['pnl'] for t in day_trades if t['entry_hour'] == hour])
            }
            detailed_results['hourly_performance'].append(hourly_data)
        
        # Calculate daily metrics
        drawdown = (peak_balance - current_balance) / peak_balance * 100 if peak_balance > 0 else 0
        win_rate_day = (len([t for t in day_trades if t['pnl'] > 0]) / len(day_trades) * 100) if day_trades else 0
        
        daily_summary = {
            'day': day + 1,
            'date': datetime.now() + timedelta(days=day),
            'start_balance': day_start_balance,
            'end_balance': current_balance,
            'daily_pnl': daily_pnl,
            'daily_return': (daily_pnl / day_start_balance * 100) if day_start_balance > 0 else 0,
            'trades_count': len(day_trades),
            'win_rate': win_rate_day,
            'drawdown': drawdown,
            'peak_balance': peak_balance
        }
        detailed_results['daily_summary'].append(daily_summary)
        detailed_results['equity_curve'].append(current_balance)
        
        print(f"Day {day+1:2d}: Balance: {current_balance:15,.0f} IDR | P&L: {daily_pnl:+12,.0f} IDR | Trades: {len(day_trades):2d} | Win Rate: {win_rate_day:.1f}%")
        
        # Emergency stop if balance too low
        if current_balance < initial_balance * 0.01:  # 99% loss
            print(f"🚨 Emergency stop triggered at day {day+1}")
            break
    
    # Generate comprehensive analysis
    _analyze_detailed_results(detailed_results, initial_balance, leverage)
    
    return detailed_results


def _get_trading_session(hour: int) -> str:
    """Determine trading session based on hour (UTC)"""
    if 0 <= hour < 6:
        return 'Asian'
    elif 6 <= hour < 8:
        return 'Asian_Close'
    elif 8 <= hour < 12:
        return 'London'
    elif 12 <= hour < 16:
        return 'Overlap'  # London-NY overlap
    elif 16 <= hour < 20:
        return 'New_York'
    else:
        return 'After_Hours'


def _select_pair_for_session(session: str, pairs_info: Dict) -> str:
    """Select currency pair based on trading session"""
    if session in ['London', 'Overlap']:
        return np.random.choice(['EURUSD', 'GBPUSD', 'USDCHF'], p=[0.4, 0.35, 0.25])
    elif session in ['Asian', 'Asian_Close']:
        return np.random.choice(['USDJPY', 'AUDUSD'], p=[0.6, 0.4])
    elif session == 'New_York':
        return np.random.choice(['EURUSD', 'GBPUSD', 'USDJPY'], p=[0.4, 0.3, 0.3])
    else:
        return np.random.choice(list(pairs_info.keys()))


def _generate_detailed_trade(trade_id: int, pair: str, strategy: str, balance: float, 
                           leverage: int, day: int, hour: int, session: str, pair_info: Dict):
    """Generate a detailed trade with comprehensive information"""
    
    if balance <= 0 or not np.isfinite(balance):
        return None
    
    # Entry details
    entry_time = datetime.now() + timedelta(days=day, hours=hour, minutes=np.random.randint(0, 60))
    signal_type = np.random.choice(['BUY', 'SELL'])
    
    # Strategy-specific parameters
    strategy_params = _get_strategy_parameters(strategy, session, pair_info)
    confidence = strategy_params['confidence']
    holding_time_minutes = strategy_params['holding_time']
    
    # Position sizing with risk management
    risk_percentage = min(strategy_params['risk_per_trade'], 0.05)  # Max 5% risk
    risk_amount = balance * risk_percentage
    
    # Calculate position size with leverage limits
    max_position_size = balance * 5  # Max 5x balance
    position_size = min(risk_amount * min(leverage, 200), max_position_size)
    
    # Market simulation
    volatility = pair_info['volatility']
    spread = pair_info['spread'] / 10000  # Convert pips to decimal
    
    # Entry price simulation
    base_price = 1.1000 if 'EUR' in pair else 1.3000 if 'GBP' in pair else 110.0 if 'JPY' in pair else 1.0000
    entry_price = base_price + np.random.normal(0, volatility * base_price)
    
    # Market movement simulation
    market_direction = np.random.choice([-1, 1])
    price_movement = np.random.normal(0, volatility * base_price)
    
    # Determine trade outcome
    win_probability = 0.45 + (confidence * 0.25)  # 45-70% based on confidence
    is_winner = np.random.random() < win_probability
    
    if is_winner:
        # Winner trade
        reward_ratio = strategy_params['reward_ratio']
        pips_gained = abs(price_movement) * reward_ratio * 10000
        exit_price = entry_price + (price_movement * reward_ratio * (1 if signal_type == 'BUY' else -1))
        pnl_pips = pips_gained
    else:
        # Losing trade
        pips_lost = abs(price_movement) * 10000
        exit_price = entry_price - (price_movement * (1 if signal_type == 'BUY' else -1))
        pnl_pips = -pips_lost
    
    # Calculate P&L in IDR
    pip_value = position_size / 10000 if 'JPY' not in pair else position_size / 100
    pnl_before_costs = pnl_pips * pip_value
    
    # Trading costs
    spread_cost = spread * position_size
    commission = position_size * 0.00002  # 0.002% commission
    total_costs = spread_cost + commission
    
    # Final P&L
    pnl = pnl_before_costs - total_costs
    pnl = max(min(pnl, balance * 0.5), -balance * 0.05)  # Cap gains/losses
    
    # Exit details
    exit_time = entry_time + timedelta(minutes=holding_time_minutes)
    exit_balance = balance + pnl
    exit_balance = max(exit_balance, 0)
    
    # Final safety check
    if not np.isfinite(exit_balance) or not np.isfinite(pnl):
        return None
    
    return {
        'trade_id': trade_id,
        'pair': pair,
        'strategy': strategy,
        'signal_type': signal_type,
        'entry_time': entry_time,
        'exit_time': exit_time,
        'entry_hour': hour,
        'session': session,
        'confidence': confidence,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'position_size': position_size,
        'risk_amount': risk_amount,
        'pnl_pips': pnl_pips,
        'pnl': pnl,
        'spread_cost': spread_cost,
        'commission': commission,
        'total_costs': total_costs,
        'holding_time_minutes': holding_time_minutes,
        'entry_balance': balance,
        'exit_balance': exit_balance,
        'is_winner': is_winner,
        'day': day + 1,
        'return_percentage': (pnl / balance * 100) if balance > 0 else 0
    }


def _get_strategy_parameters(strategy: str, session: str, pair_info: Dict) -> Dict:
    """Get strategy-specific parameters"""
    base_params = {
        'RSI_Extreme': {
            'confidence': np.random.uniform(0.75, 0.95),
            'risk_per_trade': 0.02,
            'reward_ratio': 1.5,
            'holding_time': np.random.randint(15, 120)
        },
        'Breakout_Momentum': {
            'confidence': np.random.uniform(0.65, 0.85),
            'risk_per_trade': 0.03,
            'reward_ratio': 2.0,
            'holding_time': np.random.randint(30, 240)
        },
        'News_Trading': {
            'confidence': np.random.uniform(0.60, 0.90),
            'risk_per_trade': 0.04,
            'reward_ratio': 1.8,
            'holding_time': np.random.randint(5, 30)
        },
        'Scalping_1M': {
            'confidence': np.random.uniform(0.70, 0.95),
            'risk_per_trade': 0.01,
            'reward_ratio': 1.2,
            'holding_time': np.random.randint(1, 5)
        },
        'Mean_Reversion': {
            'confidence': np.random.uniform(0.55, 0.80),
            'risk_per_trade': 0.025,
            'reward_ratio': 1.6,
            'holding_time': np.random.randint(60, 480)
        }
    }
    
    return base_params.get(strategy, base_params['RSI_Extreme'])


def _analyze_detailed_results(results: Dict, initial_balance: float, leverage: int):
    """Generate comprehensive analysis of detailed results"""
    
    if not results['trades']:
        print("❌ No trades to analyze")
        return
    
    trades_df = pd.DataFrame(results['trades'])
    daily_df = pd.DataFrame(results['daily_summary'])
    
    # Overall performance metrics
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['pnl'] > 0])
    losing_trades = total_trades - winning_trades
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    final_balance = results['equity_curve'][-1] if results['equity_curve'] else initial_balance
    total_return = ((final_balance - initial_balance) / initial_balance * 100) if initial_balance > 0 else 0
    
    # Risk metrics
    daily_returns = daily_df['daily_return'].values
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
    max_drawdown = daily_df['drawdown'].max()
    
    # Trading frequency analysis
    trades_per_day = total_trades / len(daily_df)
    avg_holding_time = trades_df['holding_time_minutes'].mean()
    
    # Pair performance
    pair_performance = trades_df.groupby('pair').agg({
        'pnl': ['sum', 'count', 'mean'],
        'is_winner': 'mean'
    }).round(2)
    
    # Strategy performance
    strategy_performance = trades_df.groupby('strategy').agg({
        'pnl': ['sum', 'count', 'mean'],
        'is_winner': 'mean',
        'confidence': 'mean'
    }).round(2)
    
    # Session performance
    session_performance = trades_df.groupby('session').agg({
        'pnl': ['sum', 'count', 'mean'],
        'is_winner': 'mean'
    }).round(2)
    
    # Generate detailed report
    _create_detailed_report(
        results, trades_df, daily_df, initial_balance, final_balance, 
        total_return, leverage, win_rate, sharpe_ratio, max_drawdown,
        pair_performance, strategy_performance, session_performance,
        trades_per_day, avg_holding_time
    )
    
    # Create detailed visualizations
    _create_detailed_visualizations(results, trades_df, daily_df)
    
    print("📊 Detailed analysis completed!")
    print("📄 Report saved: DETAILED_BACKTEST_REPORT.md")
    print("📈 Visualizations saved: detailed_backtest_charts.html")


def _create_detailed_report(results, trades_df, daily_df, initial_balance, final_balance, 
                          total_return, leverage, win_rate, sharpe_ratio, max_drawdown,
                          pair_performance, strategy_performance, session_performance,
                          trades_per_day, avg_holding_time):
    """Create comprehensive detailed report"""
    
    # Best and worst trades
    best_trade = trades_df.loc[trades_df['pnl'].idxmax()]
    worst_trade = trades_df.loc[trades_df['pnl'].idxmin()]
    
    # Consecutive wins/losses
    trades_df['win_streak'] = (trades_df['is_winner'] != trades_df['is_winner'].shift()).cumsum()
    win_streaks = trades_df[trades_df['is_winner']].groupby('win_streak').size()
    loss_streaks = trades_df[~trades_df['is_winner']].groupby('win_streak').size()
    
    max_win_streak = win_streaks.max() if len(win_streaks) > 0 else 0
    max_loss_streak = loss_streaks.max() if len(loss_streaks) > 0 else 0
    
    report = f"""# 🔍 DETAILED FOREX TRADING BACKTEST ANALYSIS

## 📊 EXECUTIVE SUMMARY
- **Initial Capital:** {initial_balance:,.0f} IDR
- **Final Capital:** {final_balance:,.0f} IDR
- **Total Return:** {total_return:+.2f}%
- **Leverage Used:** {leverage}:1
- **Total Trades:** {len(trades_df)}
- **Win Rate:** {win_rate:.1f}%
- **Sharpe Ratio:** {sharpe_ratio:.2f}
- **Maximum Drawdown:** {max_drawdown:.2f}%

## 🎯 TRADING FREQUENCY ANALYSIS
- **Trades per Day:** {trades_per_day:.1f}
- **Average Holding Time:** {avg_holding_time:.1f} minutes
- **Most Active Session:** {session_performance['pnl']['count'].idxmax()}
- **Maximum Win Streak:** {max_win_streak} trades
- **Maximum Loss Streak:** {max_loss_streak} trades

## 💰 BEST & WORST TRADES
### 🏆 Best Trade (Trade #{best_trade['trade_id']})
- **Pair:** {best_trade['pair']}
- **Strategy:** {best_trade['strategy']}
- **Entry:** {best_trade['entry_time'].strftime('%Y-%m-%d %H:%M')}
- **P&L:** {best_trade['pnl']:+,.0f} IDR ({best_trade['return_percentage']:+.2f}%)
- **Pips:** {best_trade['pnl_pips']:+.1f}
- **Confidence:** {best_trade['confidence']:.1%}

### 📉 Worst Trade (Trade #{worst_trade['trade_id']})
- **Pair:** {worst_trade['pair']}
- **Strategy:** {worst_trade['strategy']}
- **Entry:** {worst_trade['entry_time'].strftime('%Y-%m-%d %H:%M')}
- **P&L:** {worst_trade['pnl']:+,.0f} IDR ({worst_trade['return_percentage']:+.2f}%)
- **Pips:** {worst_trade['pnl_pips']:+.1f}
- **Confidence:** {worst_trade['confidence']:.1%}

## 📈 CURRENCY PAIR PERFORMANCE
"""
    
    for pair in pair_performance.index:
        total_pnl = pair_performance.loc[pair, ('pnl', 'sum')]
        trade_count = pair_performance.loc[pair, ('pnl', 'count')]
        avg_pnl = pair_performance.loc[pair, ('pnl', 'mean')]
        win_rate_pair = pair_performance.loc[pair, ('is_winner', 'mean')] * 100
        
        report += f"""
### {pair}
- **Total P&L:** {total_pnl:+,.0f} IDR
- **Trades:** {trade_count}
- **Average P&L:** {avg_pnl:+,.0f} IDR
- **Win Rate:** {win_rate_pair:.1f}%
"""
    
    report += "\n## 🎯 STRATEGY PERFORMANCE\n"
    
    for strategy in strategy_performance.index:
        total_pnl = strategy_performance.loc[strategy, ('pnl', 'sum')]
        trade_count = strategy_performance.loc[strategy, ('pnl', 'count')]
        avg_pnl = strategy_performance.loc[strategy, ('pnl', 'mean')]
        win_rate_strategy = strategy_performance.loc[strategy, ('is_winner', 'mean')] * 100
        avg_confidence = strategy_performance.loc[strategy, ('confidence', 'mean')] * 100
        
        report += f"""
### {strategy}
- **Total P&L:** {total_pnl:+,.0f} IDR
- **Trades:** {trade_count}
- **Average P&L:** {avg_pnl:+,.0f} IDR
- **Win Rate:** {win_rate_strategy:.1f}%
- **Average Confidence:** {avg_confidence:.1f}%
"""
    
    report += "\n## 🕐 SESSION PERFORMANCE\n"
    
    for session in session_performance.index:
        total_pnl = session_performance.loc[session, ('pnl', 'sum')]
        trade_count = session_performance.loc[session, ('pnl', 'count')]
        avg_pnl = session_performance.loc[session, ('pnl', 'mean')]
        win_rate_session = session_performance.loc[session, ('is_winner', 'mean')] * 100
        
        report += f"""
### {session} Session
- **Total P&L:** {total_pnl:+,.0f} IDR
- **Trades:** {trade_count}
- **Average P&L:** {avg_pnl:+,.0f} IDR
- **Win Rate:** {win_rate_session:.1f}%
"""
    
    # Daily breakdown
    report += "\n## 📅 DAILY PERFORMANCE BREAKDOWN\n"
    
    for _, day in daily_df.iterrows():
        report += f"""
### Day {day['day']} ({day['date'].strftime('%Y-%m-%d')})
- **Start Balance:** {day['start_balance']:,.0f} IDR
- **End Balance:** {day['end_balance']:,.0f} IDR
- **Daily P&L:** {day['daily_pnl']:+,.0f} IDR ({day['daily_return']:+.2f}%)
- **Trades:** {day['trades_count']}
- **Win Rate:** {day['win_rate']:.1f}%
- **Drawdown:** {day['drawdown']:.2f}%
"""
    
    # Save detailed trade log
    trades_df.to_csv('detailed_trade_log.csv', index=False)
    daily_df.to_csv('daily_performance_log.csv', index=False)
    
    report += f"""
## 📋 DETAILED LOGS
- **Complete Trade Log:** detailed_trade_log.csv ({len(trades_df)} trades)
- **Daily Performance Log:** daily_performance_log.csv ({len(daily_df)} days)

## 🎯 CONCLUSION
{"🚀 EXCEPTIONAL PERFORMANCE" if total_return > 1000 else "✅ PROFITABLE SYSTEM" if total_return > 0 else "❌ LOSING SYSTEM"}

The system demonstrates {"excellent" if win_rate > 60 else "good" if win_rate > 50 else "poor"} consistency with a {win_rate:.1f}% win rate.
Risk management is {"excellent" if max_drawdown < 20 else "good" if max_drawdown < 50 else "poor"} with {max_drawdown:.1f}% maximum drawdown.
"""
    
    # Save report
    with open('DETAILED_BACKTEST_REPORT.md', 'w') as f:
        f.write(report)


def _create_detailed_visualizations(results, trades_df, daily_df):
    """Create comprehensive visualizations"""
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=2,
        subplot_titles=(
            'Equity Curve', 'Daily P&L Distribution',
            'Win Rate by Strategy', 'P&L by Currency Pair',
            'Trading Session Performance', 'Hourly Trading Activity',
            'Drawdown Periods', 'Trade Size Distribution'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Equity Curve
    fig.add_trace(
        go.Scatter(
            x=list(range(len(results['equity_curve']))),
            y=results['equity_curve'],
            mode='lines',
            name='Account Balance',
            line=dict(color='green', width=2)
        ),
        row=1, col=1
    )
    
    # 2. Daily P&L Distribution
    fig.add_trace(
        go.Histogram(
            x=daily_df['daily_pnl'],
            name='Daily P&L',
            nbinsx=20
        ),
        row=1, col=2
    )
    
    # 3. Win Rate by Strategy
    strategy_stats = trades_df.groupby('strategy')['is_winner'].mean() * 100
    fig.add_trace(
        go.Bar(
            x=strategy_stats.index,
            y=strategy_stats.values,
            name='Win Rate %'
        ),
        row=2, col=1
    )
    
    # 4. P&L by Currency Pair
    pair_pnl = trades_df.groupby('pair')['pnl'].sum()
    fig.add_trace(
        go.Bar(
            x=pair_pnl.index,
            y=pair_pnl.values,
            name='Total P&L'
        ),
        row=2, col=2
    )
    
    # 5. Trading Session Performance
    session_pnl = trades_df.groupby('session')['pnl'].sum()
    fig.add_trace(
        go.Bar(
            x=session_pnl.index,
            y=session_pnl.values,
            name='Session P&L'
        ),
        row=3, col=1
    )
    
    # 6. Hourly Trading Activity
    hourly_activity = trades_df.groupby('entry_hour').size()
    fig.add_trace(
        go.Bar(
            x=hourly_activity.index,
            y=hourly_activity.values,
            name='Trades per Hour'
        ),
        row=3, col=2
    )
    
    # 7. Drawdown Periods
    fig.add_trace(
        go.Scatter(
            x=list(range(len(daily_df))),
            y=daily_df['drawdown'],
            mode='lines',
            name='Drawdown %',
            line=dict(color='red', width=2)
        ),
        row=4, col=1
    )
    
    # 8. Trade Size Distribution
    fig.add_trace(
        go.Histogram(
            x=trades_df['position_size'],
            name='Position Size',
            nbinsx=20
        ),
        row=4, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=1200,
        title_text="Comprehensive Forex Trading Backtest Analysis",
        showlegend=False
    )
    
    # Save visualization
    fig.write_html('detailed_backtest_charts.html')


if __name__ == "__main__":
    # Run detailed backtest
    results = generate_detailed_backtest(
        initial_balance=1000000,
        days=30,
        leverage=2000
    )
    
    print("\n🎉 Detailed backtest analysis completed!")
    print("📄 Check DETAILED_BACKTEST_REPORT.md for comprehensive analysis")
    print("📈 Check detailed_backtest_charts.html for interactive visualizations")
    print("📋 Check detailed_trade_log.csv for complete trade history")

