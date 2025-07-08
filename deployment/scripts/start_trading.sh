#!/bin/bash
# Live Trading System Startup Script
# Generated on 2025-07-08 17:48:38.295463

cd "/home/ubuntu/forex-trader/deployment"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="/home/ubuntu/forex-trader/deployment:$PYTHONPATH"

# Start live trading system
echo "Starting Live Trading System..."
python3 live_trading_system.py --config config/production_config.yaml

# Keep script running
while true; do
    echo "Checking system status..."
    if ! pgrep -f "live_trading_system.py" > /dev/null; then
        echo "System stopped. Restarting..."
        python3 live_trading_system.py --config config/production_config.yaml &
    fi
    sleep 60
done
