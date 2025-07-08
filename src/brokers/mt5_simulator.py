"""
MetaTrader 5 Simulator
Simulates MT5 functionality for testing and development
"""

import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import threading
import random

# Simulate MT5 constants
TRADE_RETCODE_DONE = 10009
TRADE_ACTION_DEAL = 1
ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
POSITION_TYPE_BUY = 0
POSITION_TYPE_SELL = 1
ORDER_TIME_GTC = 0
ORDER_FILLING_IOC = 1
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 60
TIMEFRAME_H4 = 240
TIMEFRAME_D1 = 1440
TIMEFRAME_W1 = 10080
TIMEFRAME_MN1 = 43200


@dataclass
class SimulatedTick:
    """Simulated tick data"""
    time: int
    bid: float
    ask: float
    last: float
    volume: int
    time_msc: int
    flags: int
    volume_real: float


@dataclass
class SimulatedSymbolInfo:
    """Simulated symbol information"""
    name: str
    digits: int
    point: float
    spread: int
    volume_min: float
    volume_max: float
    volume_step: float
    trade_contract_size: float
    margin_initial: float
    currency_base: str
    currency_profit: str
    currency_margin: str


@dataclass
class SimulatedAccountInfo:
    """Simulated account information"""
    login: int
    server: str
    balance: float
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    currency: str
    leverage: int
    profit: float
    trade_allowed: bool
    trade_expert: bool


@dataclass
class SimulatedPosition:
    """Simulated position"""
    ticket: int
    symbol: str
    type: int
    volume: float
    price_open: float
    price_current: float
    profit: float
    swap: float
    commission: float
    magic: int
    comment: str
    time: int


@dataclass
class SimulatedOrderResult:
    """Simulated order result"""
    retcode: int
    order: int
    deal: int
    volume: float
    price: float
    bid: float
    ask: float
    comment: str
    request_id: int
    profit: float = 0.0
    commission: float = 0.0


class MT5Simulator:
    """
    MetaTrader 5 Simulator
    Provides realistic simulation of MT5 functionality
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected = False
        self.account_info = None
        self.symbols = {}
        self.positions = {}
        self.orders = {}
        self.next_ticket = 1000000
        self.next_order_id = 1
        
        # Market data simulation
        self.market_data = {}
        self.price_feeds = {}
        self.simulation_thread = None
        self.running = False
        
        # Initialize default symbols
        self._initialize_symbols()
        
        self.logger.info("MT5 Simulator initialized")
    
    def initialize(self, login: int = 0, password: str = "", server: str = "", 
                  timeout: int = 60000, portable: bool = False) -> bool:
        """Initialize MT5 connection (simulated)"""
        try:
            self.logger.info(f"Simulating MT5 connection to {server}")
            
            # Simulate connection delay
            time.sleep(1)
            
            # Create simulated account
            self.account_info = SimulatedAccountInfo(
                login=login or 12345678,
                server=server or "Exness-MT5Real",
                balance=1000000.0,  # 1M IDR
                equity=1000000.0,
                margin=0.0,
                margin_free=1000000.0,
                margin_level=0.0,
                currency="IDR",
                leverage=2000,
                profit=0.0,
                trade_allowed=True,
                trade_expert=True
            )
            
            self.connected = True
            
            # Start market simulation
            self._start_market_simulation()
            
            self.logger.info("MT5 Simulator connected successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"MT5 Simulator connection failed: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown MT5 connection (simulated)"""
        self.connected = False
        self.running = False
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1)
        
        self.logger.info("MT5 Simulator disconnected")
    
    def terminal_info(self) -> Dict[str, Any]:
        """Get terminal information (simulated)"""
        if not self.connected:
            return None
        
        return {
            "community_account": False,
            "community_connection": False,
            "connected": True,
            "dlls_allowed": True,
            "trade_allowed": True,
            "tradeapi_disabled": False,
            "email_enabled": False,
            "ftp_enabled": False,
            "notifications_enabled": False,
            "mqid": False,
            "build": 3815,
            "maxbars": 100000,
            "codepage": 1252,
            "ping_last": 1234,
            "community_balance": 0.0,
            "retransmission": 0.0,
            "company": "Exness (Simulated)",
            "name": "MetaTrader 5 Simulator",
            "language": "English",
            "path": "/simulated/path"
        }
    
    def account_info(self) -> Optional[SimulatedAccountInfo]:
        """Get account information (simulated)"""
        if not self.connected:
            return None
        return self.account_info
    
    def symbol_info(self, symbol: str) -> Optional[SimulatedSymbolInfo]:
        """Get symbol information (simulated)"""
        if not self.connected or symbol not in self.symbols:
            return None
        return self.symbols[symbol]
    
    def symbol_info_tick(self, symbol: str) -> Optional[SimulatedTick]:
        """Get current tick for symbol (simulated)"""
        if not self.connected or symbol not in self.market_data:
            return None
        
        data = self.market_data[symbol]
        current_time = int(time.time())
        
        return SimulatedTick(
            time=current_time,
            bid=data['bid'],
            ask=data['ask'],
            last=data['last'],
            volume=random.randint(1, 100),
            time_msc=current_time * 1000,
            flags=6,
            volume_real=random.uniform(0.1, 10.0)
        )
    
    def symbols_get(self) -> List[SimulatedSymbolInfo]:
        """Get all available symbols (simulated)"""
        if not self.connected:
            return None
        return list(self.symbols.values())
    
    def copy_rates_from_pos(self, symbol: str, timeframe: int, start_pos: int, count: int) -> Optional[np.ndarray]:
        """Get historical rates (simulated)"""
        if not self.connected or symbol not in self.market_data:
            return None
        
        # Generate simulated historical data
        current_price = self.market_data[symbol]['last']
        
        # Create realistic price movement
        rates = []
        price = current_price
        
        for i in range(count):
            # Random walk with slight trend
            change = random.gauss(0, 0.001)  # 0.1% standard deviation
            price = max(price * (1 + change), 0.0001)  # Prevent negative prices
            
            # OHLC data
            open_price = price
            high_price = price * (1 + abs(random.gauss(0, 0.0005)))
            low_price = price * (1 - abs(random.gauss(0, 0.0005)))
            close_price = price * (1 + random.gauss(0, 0.0003))
            
            # Ensure OHLC consistency
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            rate = (
                int(time.time()) - (count - i) * timeframe * 60,  # time
                open_price,      # open
                high_price,      # high
                low_price,       # low
                close_price,     # close
                random.randint(1, 1000),  # tick_volume
                0,               # spread
                random.randint(1, 1000)   # real_volume
            )
            rates.append(rate)
            price = close_price
        
        # Convert to numpy structured array (similar to MT5 format)
        dtype = [
            ('time', 'i8'),
            ('open', 'f8'),
            ('high', 'f8'),
            ('low', 'f8'),
            ('close', 'f8'),
            ('tick_volume', 'i8'),
            ('spread', 'i4'),
            ('real_volume', 'i8')
        ]
        
        return np.array(rates, dtype=dtype)
    
    def copy_rates_range(self, symbol: str, timeframe: int, date_from: datetime, date_to: datetime) -> Optional[np.ndarray]:
        """Get historical rates for date range (simulated)"""
        if not self.connected:
            return None
        
        # Calculate number of bars needed
        time_diff = date_to - date_from
        bars_needed = int(time_diff.total_seconds() / (timeframe * 60))
        
        return self.copy_rates_from_pos(symbol, timeframe, 0, min(bars_needed, 10000))
    
    def order_send(self, request: Dict[str, Any]) -> Optional[SimulatedOrderResult]:
        """Send trading order (simulated)"""
        if not self.connected:
            return None
        
        try:
            symbol = request.get('symbol')
            action = request.get('action')
            order_type = request.get('type')
            volume = request.get('volume', 0.0)
            price = request.get('price', 0.0)
            
            if symbol not in self.market_data:
                return SimulatedOrderResult(
                    retcode=10013,  # Invalid request
                    order=0,
                    deal=0,
                    volume=0.0,
                    price=0.0,
                    bid=0.0,
                    ask=0.0,
                    comment="Invalid symbol",
                    request_id=0
                )
            
            # Simulate order execution
            current_data = self.market_data[symbol]
            execution_price = current_data['ask'] if order_type == ORDER_TYPE_BUY else current_data['bid']
            
            # Add slippage simulation
            slippage = random.uniform(-0.00005, 0.00005)  # ±0.5 pips
            execution_price *= (1 + slippage)
            
            # Create position
            ticket = self.next_ticket
            self.next_ticket += 1
            
            position = SimulatedPosition(
                ticket=ticket,
                symbol=symbol,
                type=order_type,
                volume=volume,
                price_open=execution_price,
                price_current=execution_price,
                profit=0.0,
                swap=0.0,
                commission=volume * 0.5,  # Simulated commission
                magic=request.get('magic', 0),
                comment=request.get('comment', ''),
                time=int(time.time())
            )
            
            self.positions[ticket] = position
            
            # Update account balance (simulate margin requirement)
            symbol_info = self.symbols[symbol]
            margin_required = (volume * symbol_info.trade_contract_size * execution_price) / self.account_info.leverage
            self.account_info.margin += margin_required
            self.account_info.margin_free -= margin_required
            
            order_id = self.next_order_id
            self.next_order_id += 1
            
            return SimulatedOrderResult(
                retcode=TRADE_RETCODE_DONE,
                order=order_id,
                deal=ticket,
                volume=volume,
                price=execution_price,
                bid=current_data['bid'],
                ask=current_data['ask'],
                comment="Order executed",
                request_id=request.get('request_id', 0),
                commission=position.commission
            )
            
        except Exception as e:
            self.logger.error(f"Order send simulation error: {e}")
            return SimulatedOrderResult(
                retcode=10013,
                order=0,
                deal=0,
                volume=0.0,
                price=0.0,
                bid=0.0,
                ask=0.0,
                comment=f"Error: {e}",
                request_id=0
            )
    
    def positions_get(self, symbol: str = None, ticket: int = None) -> List[SimulatedPosition]:
        """Get open positions (simulated)"""
        if not self.connected:
            return []
        
        positions = list(self.positions.values())
        
        if symbol:
            positions = [p for p in positions if p.symbol == symbol]
        
        if ticket:
            positions = [p for p in positions if p.ticket == ticket]
        
        # Update current prices and profits
        for position in positions:
            if position.symbol in self.market_data:
                current_data = self.market_data[position.symbol]
                if position.type == POSITION_TYPE_BUY:
                    position.price_current = current_data['bid']
                    position.profit = (position.price_current - position.price_open) * position.volume * self.symbols[position.symbol].trade_contract_size
                else:
                    position.price_current = current_data['ask']
                    position.profit = (position.price_open - position.price_current) * position.volume * self.symbols[position.symbol].trade_contract_size
        
        return positions
    
    def last_error(self) -> Tuple[int, str]:
        """Get last error (simulated)"""
        return (0, "No error")
    
    def _initialize_symbols(self) -> None:
        """Initialize default trading symbols"""
        symbols_data = {
            'EURUSD': {
                'digits': 5,
                'point': 0.00001,
                'spread': 1,
                'contract_size': 100000.0,
                'base_currency': 'EUR',
                'profit_currency': 'USD',
                'initial_price': 1.0850
            },
            'GBPUSD': {
                'digits': 5,
                'point': 0.00001,
                'spread': 2,
                'contract_size': 100000.0,
                'base_currency': 'GBP',
                'profit_currency': 'USD',
                'initial_price': 1.2650
            },
            'USDJPY': {
                'digits': 3,
                'point': 0.001,
                'spread': 1,
                'contract_size': 100000.0,
                'base_currency': 'USD',
                'profit_currency': 'JPY',
                'initial_price': 149.50
            },
            'XAUUSD': {
                'digits': 2,
                'point': 0.01,
                'spread': 3,
                'contract_size': 100.0,
                'base_currency': 'XAU',
                'profit_currency': 'USD',
                'initial_price': 2350.00
            }
        }
        
        for symbol, data in symbols_data.items():
            self.symbols[symbol] = SimulatedSymbolInfo(
                name=symbol,
                digits=data['digits'],
                point=data['point'],
                spread=data['spread'],
                volume_min=0.01,
                volume_max=100.0,
                volume_step=0.01,
                trade_contract_size=data['contract_size'],
                margin_initial=1000.0,
                currency_base=data['base_currency'],
                currency_profit=data['profit_currency'],
                currency_margin='USD'
            )
            
            # Initialize market data
            spread = data['spread'] * data['point']
            self.market_data[symbol] = {
                'last': data['initial_price'],
                'bid': data['initial_price'] - spread/2,
                'ask': data['initial_price'] + spread/2
            }
    
    def _start_market_simulation(self) -> None:
        """Start market data simulation thread"""
        self.running = True
        self.simulation_thread = threading.Thread(target=self._simulate_market_data, daemon=True)
        self.simulation_thread.start()
    
    def _simulate_market_data(self) -> None:
        """Simulate real-time market data updates"""
        while self.running and self.connected:
            try:
                for symbol in self.market_data:
                    # Simulate price movement
                    current_price = self.market_data[symbol]['last']
                    
                    # Random walk with volatility
                    volatility = 0.0001  # 0.01% volatility per update
                    change = random.gauss(0, volatility)
                    new_price = max(current_price * (1 + change), 0.0001)
                    
                    # Update bid/ask with spread
                    symbol_info = self.symbols[symbol]
                    spread = symbol_info.spread * symbol_info.point
                    
                    self.market_data[symbol] = {
                        'last': new_price,
                        'bid': new_price - spread/2,
                        'ask': new_price + spread/2
                    }
                
                # Update account equity based on open positions
                self._update_account_equity()
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                self.logger.error(f"Market simulation error: {e}")
                time.sleep(5)
    
    def _update_account_equity(self) -> None:
        """Update account equity based on open positions"""
        if not self.account_info:
            return
        
        total_profit = 0.0
        positions = self.positions_get()
        
        for position in positions:
            total_profit += position.profit
        
        self.account_info.profit = total_profit
        self.account_info.equity = self.account_info.balance + total_profit
        
        # Update margin level
        if self.account_info.margin > 0:
            self.account_info.margin_level = (self.account_info.equity / self.account_info.margin) * 100
        else:
            self.account_info.margin_level = 0.0


# Create global simulator instance
_simulator = MT5Simulator()

# Export MT5-like functions
def initialize(login: int = 0, password: str = "", server: str = "", 
               timeout: int = 60000, portable: bool = False) -> bool:
    return _simulator.initialize(login, password, server, timeout, portable)

def shutdown() -> None:
    _simulator.shutdown()

def terminal_info():
    return _simulator.terminal_info()

def account_info():
    return _simulator.account_info()

def symbol_info(symbol: str):
    return _simulator.symbol_info(symbol)

def symbol_info_tick(symbol: str):
    return _simulator.symbol_info_tick(symbol)

def symbols_get():
    return _simulator.symbols_get()

def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int):
    return _simulator.copy_rates_from_pos(symbol, timeframe, start_pos, count)

def copy_rates_range(symbol: str, timeframe: int, date_from: datetime, date_to: datetime):
    return _simulator.copy_rates_range(symbol, timeframe, date_from, date_to)

def order_send(request: Dict[str, Any]):
    return _simulator.order_send(request)

def positions_get(symbol: str = None, ticket: int = None):
    return _simulator.positions_get(symbol, ticket)

def last_error():
    return _simulator.last_error()

