"""
BacktestConfig Validator
Ensures proper parameter validation and prevents common configuration errors
"""

import logging
from typing import Dict, Any, List
from dataclasses import fields
from datetime import datetime

from .enhanced_backtester import BacktestConfig


class ConfigValidator:
    """Validates BacktestConfig parameters and provides helpful error messages"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.valid_fields = {field.name for field in fields(BacktestConfig)}
        
    def validate_config_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean configuration dictionary
        
        Args:
            config_dict: Dictionary of configuration parameters
            
        Returns:
            Cleaned configuration dictionary with valid parameters only
            
        Raises:
            ValueError: If critical parameters are invalid
        """
        cleaned_config = {}
        warnings = []
        
        # Check for invalid parameters
        for key, value in config_dict.items():
            if key in self.valid_fields:
                cleaned_config[key] = value
            else:
                # Handle common parameter name mistakes
                corrected_key = self._correct_parameter_name(key)
                if corrected_key:
                    cleaned_config[corrected_key] = value
                    warnings.append(f"Parameter '{key}' corrected to '{corrected_key}'")
                else:
                    warnings.append(f"Unknown parameter '{key}' ignored")
        
        # Log warnings
        for warning in warnings:
            self.logger.warning(warning)
        
        # Validate parameter values
        self._validate_parameter_values(cleaned_config)
        
        return cleaned_config
    
    def _correct_parameter_name(self, incorrect_name: str) -> str:
        """
        Correct common parameter name mistakes
        
        Args:
            incorrect_name: The incorrect parameter name
            
        Returns:
            Corrected parameter name or empty string if no correction found
        """
        corrections = {
            'commission': 'commission_rate',
            'slippage': 'slippage_rate',
            'spread': 'spread_multiplier',
            'risk': 'risk_per_trade',
            'max_pos': 'max_positions',
            'positions': 'max_positions',
            'balance': 'initial_balance',
            'start': 'start_date',
            'end': 'end_date',
            'tf': 'timeframe',
            'time_frame': 'timeframe',
            'pairs': 'symbols',
            'instruments': 'symbols'
        }
        
        return corrections.get(incorrect_name, '')
    
    def _validate_parameter_values(self, config_dict: Dict[str, Any]) -> None:
        """
        Validate parameter values
        
        Args:
            config_dict: Configuration dictionary to validate
            
        Raises:
            ValueError: If any parameter value is invalid
        """
        # Validate initial_balance
        if 'initial_balance' in config_dict:
            balance = config_dict['initial_balance']
            if not isinstance(balance, (int, float)) or balance <= 0:
                raise ValueError(f"initial_balance must be a positive number, got {balance}")
        
        # Validate leverage
        if 'leverage' in config_dict:
            leverage = config_dict['leverage']
            if not isinstance(leverage, int) or leverage < 1 or leverage > 2000:
                raise ValueError(f"leverage must be an integer between 1 and 2000, got {leverage}")
        
        # Validate commission_rate
        if 'commission_rate' in config_dict:
            commission = config_dict['commission_rate']
            if not isinstance(commission, (int, float)) or commission < 0 or commission > 0.01:
                raise ValueError(f"commission_rate must be between 0 and 0.01 (1%), got {commission}")
        
        # Validate slippage_rate
        if 'slippage_rate' in config_dict:
            slippage = config_dict['slippage_rate']
            if not isinstance(slippage, (int, float)) or slippage < 0 or slippage > 0.01:
                raise ValueError(f"slippage_rate must be between 0 and 0.01 (1%), got {slippage}")
        
        # Validate risk_per_trade
        if 'risk_per_trade' in config_dict:
            risk = config_dict['risk_per_trade']
            if not isinstance(risk, (int, float)) or risk <= 0 or risk > 1:
                raise ValueError(f"risk_per_trade must be between 0 and 1 (100%), got {risk}")
        
        # Validate max_positions
        if 'max_positions' in config_dict:
            positions = config_dict['max_positions']
            if not isinstance(positions, int) or positions < 1 or positions > 100:
                raise ValueError(f"max_positions must be an integer between 1 and 100, got {positions}")
        
        # Validate symbols
        if 'symbols' in config_dict:
            symbols = config_dict['symbols']
            if not isinstance(symbols, list) or not symbols:
                raise ValueError(f"symbols must be a non-empty list, got {symbols}")
            
            for symbol in symbols:
                if not isinstance(symbol, str) or len(symbol) < 3:
                    raise ValueError(f"Invalid symbol '{symbol}', must be a string with at least 3 characters")
        
        # Validate dates
        if 'start_date' in config_dict and config_dict['start_date'] is not None:
            if not isinstance(config_dict['start_date'], datetime):
                raise ValueError("start_date must be a datetime object")
        
        if 'end_date' in config_dict and config_dict['end_date'] is not None:
            if not isinstance(config_dict['end_date'], datetime):
                raise ValueError("end_date must be a datetime object")
        
        # Validate timeframe
        if 'timeframe' in config_dict:
            timeframe = config_dict['timeframe']
            valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
            if timeframe not in valid_timeframes:
                raise ValueError(f"timeframe must be one of {valid_timeframes}, got '{timeframe}'")
    
    def create_safe_config(self, **kwargs) -> BacktestConfig:
        """
        Create a BacktestConfig with validated parameters
        
        Args:
            **kwargs: Configuration parameters
            
        Returns:
            Validated BacktestConfig instance
        """
        # Validate and clean parameters
        cleaned_params = self.validate_config_dict(kwargs)
        
        try:
            # Create config with validated parameters
            config = BacktestConfig(**cleaned_params)
            self.logger.info("BacktestConfig created successfully")
            return config
            
        except TypeError as e:
            # Provide helpful error message
            error_msg = f"Failed to create BacktestConfig: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(f"Valid parameters: {sorted(self.valid_fields)}")
            self.logger.error(f"Provided parameters: {sorted(cleaned_params.keys())}")
            raise ValueError(error_msg) from e
    
    def get_valid_parameters(self) -> List[str]:
        """Get list of valid BacktestConfig parameters"""
        return sorted(self.valid_fields)
    
    def get_parameter_info(self) -> Dict[str, str]:
        """Get information about each parameter"""
        return {
            'initial_balance': 'Starting balance for backtesting (float, > 0)',
            'leverage': 'Trading leverage (int, 1-2000)',
            'commission_rate': 'Commission rate per trade (float, 0-0.01)',
            'slippage_rate': 'Slippage rate (float, 0-0.01)',
            'spread_multiplier': 'Spread multiplier (float, > 0)',
            'risk_per_trade': 'Risk per trade as fraction (float, 0-1)',
            'max_positions': 'Maximum concurrent positions (int, 1-100)',
            'start_date': 'Backtest start date (datetime or None)',
            'end_date': 'Backtest end date (datetime or None)',
            'timeframe': 'Data timeframe (str: 1m, 5m, 15m, 30m, 1h, 4h, 1d)',
            'symbols': 'List of trading symbols (list of strings)'
        }


# Global validator instance
config_validator = ConfigValidator()


def create_validated_config(**kwargs) -> BacktestConfig:
    """
    Convenience function to create validated BacktestConfig
    
    Args:
        **kwargs: Configuration parameters
        
    Returns:
        Validated BacktestConfig instance
    """
    return config_validator.create_safe_config(**kwargs)


def validate_config_parameters(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate configuration parameters
    
    Args:
        config_dict: Dictionary of configuration parameters
        
    Returns:
        Cleaned and validated configuration dictionary
    """
    return config_validator.validate_config_dict(config_dict)

