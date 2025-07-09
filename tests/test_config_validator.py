"""
Tests for BacktestConfig Validator
"""

import unittest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.backtest.config_validator import ConfigValidator, create_validated_config, validate_config_parameters
from src.backtest.enhanced_backtester import BacktestConfig


class TestConfigValidator(unittest.TestCase):
    """Test cases for ConfigValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ConfigValidator()
    
    def test_valid_config_creation(self):
        """Test creating valid configuration"""
        config = create_validated_config(
            initial_balance=1000000.0,
            leverage=100,
            risk_per_trade=0.02
        )
        
        self.assertIsInstance(config, BacktestConfig)
        self.assertEqual(config.initial_balance, 1000000.0)
        self.assertEqual(config.leverage, 100)
        self.assertEqual(config.risk_per_trade, 0.02)
    
    def test_parameter_name_correction(self):
        """Test automatic parameter name correction"""
        config_dict = {
            'commission': 0.0001,  # Should be corrected to commission_rate
            'slippage': 0.0003,    # Should be corrected to slippage_rate
            'balance': 1000000.0,  # Should be corrected to initial_balance
            'pairs': ['EURUSD']    # Should be corrected to symbols
        }
        
        cleaned = validate_config_parameters(config_dict)
        
        self.assertIn('commission_rate', cleaned)
        self.assertIn('slippage_rate', cleaned)
        self.assertIn('initial_balance', cleaned)
        self.assertIn('symbols', cleaned)
        
        self.assertNotIn('commission', cleaned)
        self.assertNotIn('slippage', cleaned)
        self.assertNotIn('balance', cleaned)
        self.assertNotIn('pairs', cleaned)
    
    def test_invalid_parameter_ignored(self):
        """Test that invalid parameters are ignored"""
        config_dict = {
            'initial_balance': 1000000.0,
            'invalid_param': 'should_be_ignored',
            'another_invalid': 123
        }
        
        cleaned = validate_config_parameters(config_dict)
        
        self.assertIn('initial_balance', cleaned)
        self.assertNotIn('invalid_param', cleaned)
        self.assertNotIn('another_invalid', cleaned)
    
    def test_parameter_value_validation(self):
        """Test parameter value validation"""
        
        # Test invalid initial_balance
        with self.assertRaises(ValueError):
            validate_config_parameters({'initial_balance': -1000})
        
        # Test invalid leverage
        with self.assertRaises(ValueError):
            validate_config_parameters({'leverage': 3000})  # Too high
        
        # Test invalid commission_rate
        with self.assertRaises(ValueError):
            validate_config_parameters({'commission_rate': 0.1})  # Too high
        
        # Test invalid risk_per_trade
        with self.assertRaises(ValueError):
            validate_config_parameters({'risk_per_trade': 1.5})  # > 100%
        
        # Test invalid symbols
        with self.assertRaises(ValueError):
            validate_config_parameters({'symbols': []})  # Empty list
    
    def test_valid_parameters_list(self):
        """Test getting valid parameters list"""
        valid_params = self.validator.get_valid_parameters()
        
        self.assertIn('initial_balance', valid_params)
        self.assertIn('leverage', valid_params)
        self.assertIn('commission_rate', valid_params)
        self.assertIn('symbols', valid_params)
    
    def test_parameter_info(self):
        """Test getting parameter information"""
        param_info = self.validator.get_parameter_info()
        
        self.assertIn('initial_balance', param_info)
        self.assertIn('leverage', param_info)
        self.assertTrue(isinstance(param_info['initial_balance'], str))
    
    def test_edge_cases(self):
        """Test edge cases"""
        
        # Test minimum valid values
        config = create_validated_config(
            initial_balance=1.0,
            leverage=1,
            risk_per_trade=0.001,
            max_positions=1
        )
        self.assertIsInstance(config, BacktestConfig)
        
        # Test maximum valid values
        config = create_validated_config(
            initial_balance=1000000000.0,
            leverage=2000,
            risk_per_trade=1.0,
            max_positions=100
        )
        self.assertIsInstance(config, BacktestConfig)
    
    def test_datetime_validation(self):
        """Test datetime parameter validation"""
        
        # Valid datetime
        config = create_validated_config(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        self.assertIsInstance(config, BacktestConfig)
        
        # Invalid datetime (string instead of datetime)
        with self.assertRaises(ValueError):
            validate_config_parameters({
                'start_date': '2024-01-01'  # Should be datetime object
            })
    
    def test_timeframe_validation(self):
        """Test timeframe validation"""
        
        # Valid timeframes
        for tf in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']:
            config = create_validated_config(timeframe=tf)
            self.assertEqual(config.timeframe, tf)
        
        # Invalid timeframe
        with self.assertRaises(ValueError):
            validate_config_parameters({'timeframe': '2h'})  # Not in valid list


if __name__ == '__main__':
    unittest.main()

