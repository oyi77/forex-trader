#!/usr/bin/env python3
"""
Live Trading System Deployment Script
Deploys the optimized forex trading system for live trading with Exness
"""

import os
import sys
import subprocess
import shutil
import logging
import yaml
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment.log')
    ]
)

logger = logging.getLogger(__name__)


class LiveSystemDeployer:
    """Deploys the live trading system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_dir = self.project_root / "deployment"
        self.config_file = self.project_root / "live_config.yaml"
        
    def deploy(self):
        """Deploy the live trading system"""
        try:
            logger.info("🚀 Starting live trading system deployment...")
            
            # Step 1: Validate environment
            self._validate_environment()
            
            # Step 2: Create deployment directory
            self._create_deployment_structure()
            
            # Step 3: Copy system files
            self._copy_system_files()
            
            # Step 4: Setup configuration
            self._setup_configuration()
            
            # Step 5: Install dependencies
            self._install_dependencies()
            
            # Step 6: Create startup scripts
            self._create_startup_scripts()
            
            # Step 7: Setup monitoring
            self._setup_monitoring()
            
            # Step 8: Create backup system
            self._setup_backup_system()
            
            # Step 9: Final validation
            self._final_validation()
            
            logger.info("✅ Live trading system deployed successfully!")
            self._print_deployment_summary()
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            raise
    
    def _validate_environment(self):
        """Validate deployment environment"""
        logger.info("Validating environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8+ required")
        
        # Check required packages
        required_packages = ['pandas', 'numpy', 'pyyaml', 'talib']
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                logger.warning(f"Package {package} not found - will install")
        
        logger.info("Environment validation completed")
    
    def _create_deployment_structure(self):
        """Create deployment directory structure"""
        logger.info("Creating deployment structure...")
        
        directories = [
            self.deployment_dir,
            self.deployment_dir / "src",
            self.deployment_dir / "logs",
            self.deployment_dir / "data",
            self.deployment_dir / "reports",
            self.deployment_dir / "backups",
            self.deployment_dir / "config",
            self.deployment_dir / "scripts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def _copy_system_files(self):
        """Copy system files to deployment directory"""
        logger.info("Copying system files...")
        
        # Copy source code
        src_dir = self.project_root / "src"
        dest_src_dir = self.deployment_dir / "src"
        
        if src_dir.exists():
            shutil.copytree(src_dir, dest_src_dir, dirs_exist_ok=True)
            logger.info("Source code copied")
        
        # Copy main scripts
        main_scripts = [
            "live_trading_system.py",
            "run_enhanced_backtest.py",
            "optimize_strategies.py"
        ]
        
        for script in main_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                shutil.copy2(script_path, self.deployment_dir)
                logger.info(f"Copied {script}")
        
        # Copy requirements
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            shutil.copy2(req_file, self.deployment_dir)
            logger.info("Requirements file copied")
    
    def _setup_configuration(self):
        """Setup configuration files"""
        logger.info("Setting up configuration...")
        
        # Copy main config
        if self.config_file.exists():
            shutil.copy2(self.config_file, self.deployment_dir / "config")
            logger.info("Main configuration copied")
        
        # Create production config template
        prod_config = {
            'exness': {
                'login': 0,  # TO BE FILLED
                'password': '',  # TO BE FILLED
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
                    {'name': 'Ultra_Scalping_1', 'type': 'ULTRA_SCALPING', 'weight': 0.25},
                    {'name': 'Volatility_Explosion_1', 'type': 'VOLATILITY_EXPLOSION', 'weight': 0.25},
                    {'name': 'Momentum_Surge_1', 'type': 'MOMENTUM_SURGE', 'weight': 0.25},
                    {'name': 'News_Impact_1', 'type': 'NEWS_IMPACT', 'weight': 0.25}
                ]
            },
            'risk_management': {
                'max_risk_per_trade': 0.20,  # 20% per trade (extreme)
                'max_positions': 5,
                'max_daily_loss': 0.30,  # 30% daily loss limit
                'max_drawdown': 0.50,  # 50% drawdown limit
                'emergency_stop_loss': 0.70  # 70% emergency stop
            },
            'monitoring': {
                'update_interval': 30,  # 30 seconds
                'report_interval': 300,  # 5 minutes
                'heartbeat_interval': 60  # 1 minute
            }
        }
        
        with open(self.deployment_dir / "config" / "production_config.yaml", 'w') as f:
            yaml.dump(prod_config, f, default_flow_style=False)
        
        logger.info("Production configuration template created")
    
    def _install_dependencies(self):
        """Install required dependencies"""
        logger.info("Installing dependencies...")
        
        req_file = self.deployment_dir / "requirements.txt"
        if req_file.exists():
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(req_file)
                ], check=True, capture_output=True, text=True)
                logger.info("Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Some dependencies failed to install: {e}")
    
    def _create_startup_scripts(self):
        """Create startup scripts"""
        logger.info("Creating startup scripts...")
        
        # Linux/Mac startup script
        startup_script = f"""#!/bin/bash
# Live Trading System Startup Script
# Generated on {datetime.now()}

cd "{self.deployment_dir}"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="{self.deployment_dir}:$PYTHONPATH"

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
"""
        
        script_path = self.deployment_dir / "scripts" / "start_trading.sh"
        with open(script_path, 'w') as f:
            f.write(startup_script)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Windows startup script
        windows_script = f"""@echo off
REM Live Trading System Startup Script
REM Generated on {datetime.now()}

cd /d "{self.deployment_dir}"

REM Set environment variables
set PYTHONPATH={self.deployment_dir};%PYTHONPATH%

REM Start live trading system
echo Starting Live Trading System...
python live_trading_system.py --config config/production_config.yaml

pause
"""
        
        with open(self.deployment_dir / "scripts" / "start_trading.bat", 'w') as f:
            f.write(windows_script)
        
        logger.info("Startup scripts created")
    
    def _setup_monitoring(self):
        """Setup monitoring and alerting"""
        logger.info("Setting up monitoring...")
        
        # Create monitoring script
        monitoring_script = f"""#!/usr/bin/env python3
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
        logging.FileHandler('{self.deployment_dir}/logs/monitor.log'),
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
        logger.info(f"Trading System Running: {{trading_running}}")
        logger.info(f"CPU Usage: {{cpu_percent}}%")
        logger.info(f"Memory Usage: {{memory_percent}}%")
        logger.info(f"Disk Usage: {{disk_percent}}%")
        
        # Check for alerts
        if not trading_running:
            logger.error("ALERT: Trading system is not running!")
        
        if cpu_percent > 90:
            logger.warning(f"ALERT: High CPU usage: {{cpu_percent}}%")
        
        if memory_percent > 90:
            logger.warning(f"ALERT: High memory usage: {{memory_percent}}%")
        
        if disk_percent > 90:
            logger.warning(f"ALERT: High disk usage: {{disk_percent}}%")
        
        return trading_running
        
    except Exception as e:
        logger.error(f"Health check failed: {{e}}")
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
            logger.error(f"Monitor error: {{e}}")
            time.sleep(60)

if __name__ == "__main__":
    main()
"""
        
        with open(self.deployment_dir / "scripts" / "monitor.py", 'w') as f:
            f.write(monitoring_script)
        
        logger.info("Monitoring system created")
    
    def _setup_backup_system(self):
        """Setup backup system"""
        logger.info("Setting up backup system...")
        
        backup_script = f"""#!/usr/bin/env python3
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
    backup_dir = Path("{self.deployment_dir}/backups/backup_{{timestamp}}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup logs
    logs_dir = Path("{self.deployment_dir}/logs")
    if logs_dir.exists():
        shutil.copytree(logs_dir, backup_dir / "logs", dirs_exist_ok=True)
    
    # Backup reports
    reports_dir = Path("{self.deployment_dir}/reports")
    if reports_dir.exists():
        shutil.copytree(reports_dir, backup_dir / "reports", dirs_exist_ok=True)
    
    # Backup config
    config_dir = Path("{self.deployment_dir}/config")
    if config_dir.exists():
        shutil.copytree(config_dir, backup_dir / "config", dirs_exist_ok=True)
    
    print(f"Backup created: {{backup_dir}}")
    
    # Clean old backups (keep last 10)
    backups = sorted(Path("{self.deployment_dir}/backups").glob("backup_*"))
    if len(backups) > 10:
        for old_backup in backups[:-10]:
            shutil.rmtree(old_backup)
            print(f"Removed old backup: {{old_backup}}")

if __name__ == "__main__":
    create_backup()
"""
        
        with open(self.deployment_dir / "scripts" / "backup.py", 'w') as f:
            f.write(backup_script)
        
        logger.info("Backup system created")
    
    def _final_validation(self):
        """Final validation of deployment"""
        logger.info("Performing final validation...")
        
        # Check all required files exist
        required_files = [
            "live_trading_system.py",
            "src/brokers/exness_mt5.py",
            "src/strategies/extreme_leverage_strategies.py",
            "config/production_config.yaml",
            "scripts/start_trading.sh",
            "scripts/monitor.py",
            "scripts/backup.py"
        ]
        
        for file_path in required_files:
            full_path = self.deployment_dir / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"Required file missing: {file_path}")
        
        logger.info("All required files present")
        
        # Test import of main modules
        sys.path.insert(0, str(self.deployment_dir))
        try:
            from src.brokers.exness_mt5 import ExnessMT5Engine
            from src.strategies.extreme_leverage_strategies import UltraScalpingStrategy
            logger.info("Module imports successful")
        except ImportError as e:
            logger.warning(f"Import test failed: {e}")
        
        logger.info("Final validation completed")
    
    def _print_deployment_summary(self):
        """Print deployment summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🚀 LIVE TRADING SYSTEM DEPLOYED 🚀                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📁 Deployment Directory: {self.deployment_dir}                              ║
║                                                                              ║
║  🎯 GOAL: 1M IDR → 2B IDR (199,900% return in 15 days)                      ║
║  ⚡ LEVERAGE: 1:2000 (Exness)                                                ║
║  💰 RISK PER TRADE: 20% (Extreme mode)                                       ║
║                                                                              ║
║  📊 STRATEGIES DEPLOYED:                                                     ║
║     • Ultra Scalping (25%)                                                  ║
║     • Volatility Explosion (25%)                                            ║
║     • Momentum Surge (25%)                                                  ║
║     • News Impact (25%)                                                     ║
║                                                                              ║
║  🔧 NEXT STEPS:                                                              ║
║     1. Update Exness credentials in production_config.yaml                  ║
║     2. Run: ./scripts/start_trading.sh                                      ║
║     3. Monitor: python scripts/monitor.py                                   ║
║     4. Backup: python scripts/backup.py                                     ║
║                                                                              ║
║  ⚠️  WARNING: This is EXTREME RISK trading!                                  ║
║     • 65.98% daily return required                                          ║
║     • High probability of total loss                                        ║
║     • Only use money you can afford to lose                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        print(summary)
        
        # Save summary to file
        with open(self.deployment_dir / "DEPLOYMENT_SUMMARY.txt", 'w') as f:
            f.write(summary)


def main():
    """Main deployment function"""
    try:
        deployer = LiveSystemDeployer()
        deployer.deploy()
        
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

