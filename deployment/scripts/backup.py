#!/usr/bin/env python3
'''
Live Trading System Backup
Creates backups of logs, reports, and configuration
'''

import shutil
import os
from datetime import datetime
from pathlib import Path

def create_backup():
    '''Create system backup'''
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("/home/ubuntu/forex-trader/deployment/backups/backup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup logs
    logs_dir = Path("/home/ubuntu/forex-trader/deployment/logs")
    if logs_dir.exists():
        shutil.copytree(logs_dir, backup_dir / "logs", dirs_exist_ok=True)
    
    # Backup reports
    reports_dir = Path("/home/ubuntu/forex-trader/deployment/reports")
    if reports_dir.exists():
        shutil.copytree(reports_dir, backup_dir / "reports", dirs_exist_ok=True)
    
    # Backup config
    config_dir = Path("/home/ubuntu/forex-trader/deployment/config")
    if config_dir.exists():
        shutil.copytree(config_dir, backup_dir / "config", dirs_exist_ok=True)
    
    print(f"Backup created: {backup_dir}")
    
    # Clean old backups (keep last 10)
    backups = sorted(Path("/home/ubuntu/forex-trader/deployment/backups").glob("backup_*"))
    if len(backups) > 10:
        for old_backup in backups[:-10]:
            shutil.rmtree(old_backup)
            print(f"Removed old backup: {old_backup}")

if __name__ == "__main__":
    create_backup()
