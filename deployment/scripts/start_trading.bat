@echo off
REM Live Trading System Startup Script
REM Generated on 2025-07-08 17:48:38.295646

cd /d "/home/ubuntu/forex-trader/deployment"

REM Set environment variables
set PYTHONPATH=/home/ubuntu/forex-trader/deployment;%PYTHONPATH%

REM Start live trading system
echo Starting Live Trading System...
python live_trading_system.py --config config/production_config.yaml

pause
