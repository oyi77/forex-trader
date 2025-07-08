"""
Risk Manager for Forex Trading Bot
Handles risk management and position validation
"""

class RiskManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.max_daily_risk = self.config.get('MAX_DAILY_RISK', 0.05)
        self.max_positions = self.config.get('MAX_POSITIONS', 5)
        self.min_risk_reward = self.config.get('MIN_RISK_REWARD', 1.5)
    
    def validate_signal(self, signal, active_positions):
        """Validate if a signal meets risk management criteria"""
        # Check risk-reward ratio
        if signal.get('risk_reward_ratio', 0) < self.min_risk_reward:
            return False
        
        # Check position limits
        if len(active_positions) >= self.max_positions:
            return False
        
        # Check confidence threshold
        if signal.get('confidence_score', 0) < 70:
            return False
        
        return True

