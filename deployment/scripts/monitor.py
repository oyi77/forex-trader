#!/usr/bin/env python3
'''
Live Trading System Monitor
Monitors system health and sends alerts
'''

import time
import logging
import psutil
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/forex-trader/deployment/logs/monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_system_health():
    '''Check system health metrics'''
    try:
        # Check if trading system is running
        trading_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'live_trading_system.py' in ' '.join(proc.info['cmdline'] or []):
                trading_running = True
                break
        
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        # Log status
        logger.info(f"Trading System Running: {trading_running}")
        logger.info(f"CPU Usage: {cpu_percent}%")
        logger.info(f"Memory Usage: {memory_percent}%")
        logger.info(f"Disk Usage: {disk_percent}%")
        
        # Check for alerts
        if not trading_running:
            logger.error("ALERT: Trading system is not running!")
        
        if cpu_percent > 90:
            logger.warning(f"ALERT: High CPU usage: {cpu_percent}%")
        
        if memory_percent > 90:
            logger.warning(f"ALERT: High memory usage: {memory_percent}%")
        
        if disk_percent > 90:
            logger.warning(f"ALERT: High disk usage: {disk_percent}%")
        
        return trading_running
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

def main():
    '''Main monitoring loop'''
    logger.info("Starting system monitor...")
    
    while True:
        try:
            check_system_health()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
