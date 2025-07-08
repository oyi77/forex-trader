"""
Exness MT5 Integration Module
Provides live trading capabilities with Exness broker using MetaTrader 5
"""

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    # Use simulator when MT5 is not available
    from . import mt5_simulator as mt5
    MT5_AVAILABLE = False

import pandas as pd
import numpy as np
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import threading
from decimal import Decimal

from ..core.interfaces import IExecutionEngine, TradingSignal, TradeResult, MarketData
from ..core.base_classes import BaseComponent


@dataclass
class ExnessConfig:
    """Configuration for Exness MT5 connection"""
    login: int
    password: str
    server: str = "Exness-MT5Real"  # Default Exness server
    timeout: int = 60000  # Connection timeout in milliseconds
    portable: bool = False  # Use portable mode
    
    # Trading parameters
    leverage: int = 2000  # 1:2000 leverage
    base_currency: str = "IDR"  # Indonesian Rupiah
    min_lot: float = 0.01
    max_lot: float = 100.0
    
    # Risk management
    max_slippage: int = 3  # Maximum slippage in points
    magic_number: int = 123456  # Unique identifier for trades


@dataclass
class ExnessPosition:
    """Represents an open position in Exness"""
    ticket: int
    symbol: str
    type: int  # 0=BUY, 1=SELL
    volume: float
    price_open: float
    price_current: float
    profit: float
    swap: float
    commission: float
    magic: int
    comment: str
    time_open: datetime


class ExnessMT5Engine(BaseComponent, IExecutionEngine):
    """
    Exness MT5 execution engine for live trading
    Implements 1:2000 leverage trading with IDR base currency
    """
    
    def __init__(self, config: ExnessConfig):
        super().__init__("ExnessMT5Engine", {})
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connected = False
        self.account_info = None
        self.symbols_info = {}
        self.positions = {}
        self.orders = {}
        
        # Trading state
        self.trading_enabled = False
        self.last_heartbeat = datetime.now()
        self.connection_lock = threading.Lock()
        
        # Performance tracking
        self.total_trades = 0
        self.successful_trades = 0
        self.failed_trades = 0
        
        self.logger.info("Exness MT5 Engine initialized")
        if not MT5_AVAILABLE:
            self.logger.warning("MT5 not available - using simulator mode")
        else:
            self.logger.info("MT5 library available - ready for live trading")
    
    def connect(self) -> bool:
        """Establish connection to Exness MT5 terminal"""
        try:
            with self.connection_lock:
                self.logger.info("Connecting to Exness MT5...")
                
                # Initialize MT5 connection
                if not mt5.initialize(
                    login=self.config.login,
                    password=self.config.password,
                    server=self.config.server,
                    timeout=self.config.timeout,
                    portable=self.config.portable
                ):
                    error = mt5.last_error()
                    self.logger.error(f"MT5 initialization failed: {error}")
                    return False
                
                # Verify connection
                terminal_info = mt5.terminal_info()
                if terminal_info is None:
                    self.logger.error("Failed to get terminal info")
                    return False
                
                # Get account information
                self.account_info = mt5.account_info()
                if self.account_info is None:
                    self.logger.error("Failed to get account info")
                    return False
                
                self.connected = True
                self.last_heartbeat = datetime.now()
                
                self.logger.info(f"Connected to Exness MT5 successfully")
                self.logger.info(f"Account: {self.account_info.login}")
                self.logger.info(f"Server: {self.account_info.server}")
                self.logger.info(f"Balance: {self.account_info.balance} {self.account_info.currency}")
                self.logger.info(f"Leverage: 1:{self.account_info.leverage}")
                
                # Load symbol information
                self._load_symbols_info()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MT5 terminal"""
        try:
            with self.connection_lock:
                if self.connected:
                    mt5.shutdown()
                    self.connected = False
                    self.trading_enabled = False
                    self.logger.info("Disconnected from Exness MT5")
        except Exception as e:
            self.logger.error(f"Disconnect error: {e}")
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        if not self.connected:
            return False
        
        try:
            # Heartbeat check
            account_info = mt5.account_info()
            if account_info is None:
                self.connected = False
                return False
            
            self.last_heartbeat = datetime.now()
            return True
            
        except Exception as e:
            self.logger.error(f"Connection check failed: {e}")
            self.connected = False
            return False
    
    def enable_trading(self) -> bool:
        """Enable live trading"""
        if not self.is_connected():
            self.logger.error("Cannot enable trading: not connected")
            return False
        
        # Verify account allows trading
        if not self.account_info.trade_allowed:
            self.logger.error("Trading not allowed on this account")
            return False
        
        self.trading_enabled = True
        self.logger.info("Live trading ENABLED - REAL MONEY AT RISK!")
        return True
    
    def disable_trading(self) -> None:
        """Disable live trading"""
        self.trading_enabled = False
        self.logger.info("Live trading disabled")
    
    def execute_signal(self, signal: TradingSignal) -> TradeResult:
        """Execute a trading signal on Exness"""
        if not self.trading_enabled:
            return TradeResult(
                success=False,
                error="Trading disabled",
                trade_id="",
                entry_price=0.0,
                timestamp=datetime.now()
            )
        
        try:
            self.logger.info(f"Executing signal: {signal.action} {signal.symbol}")
            
            # Validate symbol
            if not self._validate_symbol(signal.symbol):
                return TradeResult(
                    success=False,
                    error=f"Invalid symbol: {signal.symbol}",
                    trade_id="",
                    entry_price=0.0,
                    timestamp=datetime.now()
                )
            
            # Calculate position size
            volume = self._calculate_position_size(signal)
            if volume <= 0:
                return TradeResult(
                    success=False,
                    error="Invalid position size calculated",
                    trade_id="",
                    entry_price=0.0,
                    timestamp=datetime.now()
                )
            
            # Prepare order request
            order_request = self._prepare_order_request(signal, volume)
            
            # Send order
            result = mt5.order_send(order_request)
            
            if result is None:
                error = mt5.last_error()
                self.logger.error(f"Order send failed: {error}")
                self.failed_trades += 1
                return TradeResult(
                    success=False,
                    error=f"Order failed: {error}",
                    trade_id="",
                    entry_price=0.0,
                    timestamp=datetime.now()
                )
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.error(f"Order rejected: {result.retcode} - {result.comment}")
                self.failed_trades += 1
                return TradeResult(
                    success=False,
                    error=f"Order rejected: {result.comment}",
                    trade_id="",
                    entry_price=result.price if hasattr(result, 'price') else 0.0,
                    timestamp=datetime.now()
                )
            
            # Order successful
            self.total_trades += 1
            self.successful_trades += 1
            
            self.logger.info(f"Order executed successfully: {result.order}")
            self.logger.info(f"Price: {result.price}, Volume: {result.volume}")
            
            return TradeResult(
                success=True,
                error="",
                trade_id=str(result.order),
                entry_price=result.price,
                timestamp=datetime.now(),
                volume=result.volume,
                commission=getattr(result, 'commission', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Execute signal error: {e}")
            self.failed_trades += 1
            return TradeResult(
                success=False,
                error=str(e),
                trade_id="",
                entry_price=0.0,
                timestamp=datetime.now()
            )
    
    def close_position(self, position_id: str, reason: str = "Manual close") -> TradeResult:
        """Close an open position"""
        if not self.trading_enabled:
            return TradeResult(
                success=False,
                error="Trading disabled",
                trade_id=position_id,
                entry_price=0.0,
                timestamp=datetime.now()
            )
        
        try:
            # Get position info
            positions = mt5.positions_get(ticket=int(position_id))
            if not positions:
                return TradeResult(
                    success=False,
                    error="Position not found",
                    trade_id=position_id,
                    entry_price=0.0,
                    timestamp=datetime.now()
                )
            
            position = positions[0]
            
            # Prepare close request
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "deviation": self.config.max_slippage,
                "magic": self.config.magic_number,
                "comment": f"Close: {reason}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send close order
            result = mt5.order_send(close_request)
            
            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                error = mt5.last_error() if result is None else result.comment
                self.logger.error(f"Position close failed: {error}")
                return TradeResult(
                    success=False,
                    error=f"Close failed: {error}",
                    trade_id=position_id,
                    entry_price=position.price_open,
                    timestamp=datetime.now()
                )
            
            self.logger.info(f"Position closed successfully: {position_id}")
            return TradeResult(
                success=True,
                error="",
                trade_id=position_id,
                entry_price=position.price_open,
                exit_price=result.price,
                timestamp=datetime.now(),
                profit=getattr(result, 'profit', 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Close position error: {e}")
            return TradeResult(
                success=False,
                error=str(e),
                trade_id=position_id,
                entry_price=0.0,
                timestamp=datetime.now()
            )
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get current account information"""
        if not self.is_connected():
            return {}
        
        try:
            account = mt5.account_info()
            if account is None:
                return {}
            
            return {
                "login": account.login,
                "server": account.server,
                "balance": account.balance,
                "equity": account.equity,
                "margin": account.margin,
                "free_margin": account.margin_free,
                "margin_level": account.margin_level,
                "currency": account.currency,
                "leverage": account.leverage,
                "profit": account.profit,
                "trade_allowed": account.trade_allowed,
                "expert_allowed": account.trade_expert,
                "last_update": datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Get account info error: {e}")
            return {}
    
    def get_positions(self) -> List[ExnessPosition]:
        """Get all open positions"""
        if not self.is_connected():
            return []
        
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                result.append(ExnessPosition(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    type=pos.type,
                    volume=pos.volume,
                    price_open=pos.price_open,
                    price_current=pos.price_current,
                    profit=pos.profit,
                    swap=pos.swap,
                    commission=pos.commission,
                    magic=pos.magic,
                    comment=pos.comment,
                    time_open=datetime.fromtimestamp(pos.time)
                ))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Get positions error: {e}")
            return []
    
    def get_market_data(self, symbol: str, timeframe: str = "1h", count: int = 100) -> Optional[MarketData]:
        """Get real-time market data from Exness"""
        if not self.is_connected():
            return None
        
        try:
            # Convert timeframe
            mt5_timeframe = self._convert_timeframe(timeframe)
            
            # Get historical data
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if rates is None:
                self.logger.error(f"Failed to get market data for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Get current tick
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                current_price = df['close'].iloc[-1]
                bid = ask = current_price
            else:
                bid = tick.bid
                ask = tick.ask
                current_price = (bid + ask) / 2
            
            return MarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                bid=bid,
                ask=ask,
                last=current_price,
                volume=df['tick_volume'].iloc[-1] if len(df) > 0 else 0,
                high_24h=df['high'].max() if len(df) > 0 else current_price,
                low_24h=df['low'].min() if len(df) > 0 else current_price,
                historical_data=df
            )
            
        except Exception as e:
            self.logger.error(f"Get market data error: {e}")
            return None
    
    def _load_symbols_info(self) -> None:
        """Load symbol information"""
        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                self.logger.warning("No symbols available")
                return
            
            for symbol in symbols:
                self.symbols_info[symbol.name] = {
                    "digits": symbol.digits,
                    "point": symbol.point,
                    "spread": symbol.spread,
                    "volume_min": symbol.volume_min,
                    "volume_max": symbol.volume_max,
                    "volume_step": symbol.volume_step,
                    "contract_size": symbol.trade_contract_size,
                    "margin_initial": symbol.margin_initial,
                    "currency_base": symbol.currency_base,
                    "currency_profit": symbol.currency_profit,
                    "currency_margin": symbol.currency_margin
                }
            
            self.logger.info(f"Loaded {len(self.symbols_info)} symbols")
            
        except Exception as e:
            self.logger.error(f"Load symbols error: {e}")
    
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate if symbol is available for trading"""
        if symbol not in self.symbols_info:
            # Try to get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return False
            
            # Add to cache
            self.symbols_info[symbol] = {
                "digits": symbol_info.digits,
                "point": symbol_info.point,
                "spread": symbol_info.spread,
                "volume_min": symbol_info.volume_min,
                "volume_max": symbol_info.volume_max,
                "volume_step": symbol_info.volume_step,
                "contract_size": symbol_info.trade_contract_size,
                "margin_initial": symbol_info.margin_initial,
                "currency_base": symbol_info.currency_base,
                "currency_profit": symbol_info.currency_profit,
                "currency_margin": symbol_info.currency_margin
            }
        
        return True
    
    def _calculate_position_size(self, signal: TradingSignal) -> float:
        """Calculate position size based on risk and leverage"""
        try:
            account = mt5.account_info()
            if account is None:
                return 0.0
            
            # Get symbol info
            symbol_info = self.symbols_info.get(signal.symbol)
            if not symbol_info:
                return 0.0
            
            # Calculate position size based on risk percentage
            risk_amount = account.balance * signal.position_size  # position_size is risk percentage
            
            # Get current price
            tick = mt5.symbol_info_tick(signal.symbol)
            if tick is None:
                return 0.0
            
            current_price = tick.ask if signal.action == "BUY" else tick.bid
            
            # Calculate lot size
            # For forex: 1 lot = 100,000 units of base currency
            # With 1:2000 leverage, margin required = (lot_size * contract_size * price) / leverage
            contract_size = symbol_info["contract_size"]
            
            # Calculate maximum lots based on available margin
            margin_required_per_lot = (contract_size * current_price) / self.config.leverage
            max_lots_by_margin = account.margin_free / margin_required_per_lot
            
            # Calculate lots based on risk
            # Risk per pip = risk_amount / (stop_loss_pips * pip_value)
            # For now, use a conservative approach
            risk_lots = risk_amount / (contract_size * current_price / self.config.leverage)
            
            # Use the smaller of the two
            calculated_lots = min(risk_lots, max_lots_by_margin * 0.8)  # 80% of max margin
            
            # Apply limits
            min_lot = symbol_info["volume_min"]
            max_lot = min(symbol_info["volume_max"], self.config.max_lot)
            
            final_lots = max(min_lot, min(calculated_lots, max_lot))
            
            # Round to step size
            step = symbol_info["volume_step"]
            final_lots = round(final_lots / step) * step
            
            self.logger.info(f"Calculated position size: {final_lots} lots for {signal.symbol}")
            self.logger.info(f"Risk amount: {risk_amount} {account.currency}")
            self.logger.info(f"Margin required: {final_lots * margin_required_per_lot:.2f} {account.currency}")
            
            return final_lots
            
        except Exception as e:
            self.logger.error(f"Calculate position size error: {e}")
            return 0.0
    
    def _prepare_order_request(self, signal: TradingSignal, volume: float) -> Dict[str, Any]:
        """Prepare MT5 order request"""
        # Get current prices
        tick = mt5.symbol_info_tick(signal.symbol)
        
        if signal.action == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        
        # Prepare basic request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": signal.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": self.config.max_slippage,
            "magic": self.config.magic_number,
            "comment": f"Signal: {signal.strategy_name}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Add stop loss and take profit if specified
        if signal.stop_loss and signal.stop_loss > 0:
            request["sl"] = signal.stop_loss
        
        if signal.take_profit and signal.take_profit > 0:
            request["tp"] = signal.take_profit
        
        return request
    
    def _convert_timeframe(self, timeframe: str) -> int:
        """Convert timeframe string to MT5 constant"""
        timeframe_map = {
            "1m": mt5.TIMEFRAME_M1,
            "5m": mt5.TIMEFRAME_M5,
            "15m": mt5.TIMEFRAME_M15,
            "30m": mt5.TIMEFRAME_M30,
            "1h": mt5.TIMEFRAME_H1,
            "4h": mt5.TIMEFRAME_H4,
            "1d": mt5.TIMEFRAME_D1,
            "1w": mt5.TIMEFRAME_W1,
            "1M": mt5.TIMEFRAME_MN1
        }
        
        return timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
    
    def execute_trade(self, signal: TradingSignal, position_size: float) -> TradeResult:
        """Execute a trade (interface compatibility)"""
        # Create a copy of the signal with the specified position size
        modified_signal = TradingSignal(
            symbol=signal.symbol,
            action=signal.action,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            position_size=position_size,
            confidence=signal.confidence,
            strategy_name=signal.strategy_name,
            timestamp=signal.timestamp,
            timeframe=signal.timeframe,
            reason=signal.reason
        )
        return self.execute_signal(modified_signal)
    
    def get_open_positions(self) -> List[TradeResult]:
        """Get all open positions (interface compatibility)"""
        positions = self.get_positions()
        trade_results = []
        
        for position in positions:
            trade_results.append(TradeResult(
                success=True,
                error="",
                trade_id=str(position.ticket),
                entry_price=position.price_open,
                exit_price=position.price_current,
                timestamp=datetime.fromtimestamp(position.time_open.timestamp() if hasattr(position.time_open, 'timestamp') else position.time_open),
                volume=position.volume,
                profit=position.profit,
                commission=position.commission
            ))
        
        return trade_results
    
    def get_account_balance(self) -> float:
        """Get current account balance (interface compatibility)"""
        account_info = self.get_account_info()
        return account_info.get('balance', 0.0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get execution engine performance statistics"""
        success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
        
        return {
            "total_trades": self.total_trades,
            "successful_trades": self.successful_trades,
            "failed_trades": self.failed_trades,
            "success_rate": success_rate,
            "connected": self.connected,
            "trading_enabled": self.trading_enabled,
            "last_heartbeat": self.last_heartbeat,
            "leverage": self.config.leverage,
            "base_currency": self.config.base_currency
        }


def create_exness_engine(login: int, password: str, server: str = "Exness-MT5Real") -> ExnessMT5Engine:
    """Factory function to create Exness MT5 engine"""
    config = ExnessConfig(
        login=login,
        password=password,
        server=server,
        leverage=2000,  # 1:2000 leverage
        base_currency="IDR"
    )
    
    return ExnessMT5Engine(config)

