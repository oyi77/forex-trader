"""
Broker Integration Module for Forex Trading Bot
Integrates with various forex brokers for trade execution
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import base64
import warnings
warnings.filterwarnings('ignore')

class BrokerType(Enum):
    OANDA = "oanda"
    FXCM = "fxcm"
    EXNESS = "exness"
    PAPER_TRADING = "paper_trading"
    MT4_BRIDGE = "mt4_bridge"
    MT5_BRIDGE = "mt5_bridge"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"

@dataclass
class TradeOrder:
    """Trade order structure"""
    symbol: str
    order_type: OrderType
    side: str  # 'buy' or 'sell'
    quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    expiry: Optional[datetime] = None
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None
    commission: float = 0.0
    swap: float = 0.0

@dataclass
class Position:
    """Trading position structure"""
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    commission: float
    swap: float
    open_time: datetime
    position_id: str

@dataclass
class AccountInfo:
    """Account information structure"""
    account_id: str
    balance: float
    equity: float
    margin_used: float
    margin_available: float
    currency: str
    leverage: float

class BrokerIntegration:
    def __init__(self, broker_type: BrokerType, config: Dict):
        self.broker_type = broker_type
        self.config = config
        self.logger = logging.getLogger(f'BrokerIntegration_{broker_type.value}')
        
        # Connection settings
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.account_id = config.get('account_id')
        self.base_url = config.get('base_url')
        self.is_demo = config.get('is_demo', True)
        
        # Session management
        self.session = None
        self.authenticated = False
        self.last_heartbeat = None
        
        # Order and position tracking
        self.active_orders = {}
        self.positions = {}
        self.order_history = []
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit = config.get('rate_limit', 60)  # requests per minute
        
        self.logger.info(f"Broker integration initialized for {broker_type.value}")
    
    async def connect(self) -> bool:
        """Connect to broker API"""
        try:
            if self.session is None:
                timeout = aiohttp.ClientTimeout(total=30)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Authenticate based on broker type
            if self.broker_type == BrokerType.OANDA:
                success = await self._authenticate_oanda()
            elif self.broker_type == BrokerType.FXCM:
                success = await self._authenticate_fxcm()
            elif self.broker_type == BrokerType.EXNESS:
                success = await self._authenticate_exness()
            elif self.broker_type == BrokerType.PAPER_TRADING:
                success = await self._authenticate_paper_trading()
            else:
                success = False
            
            if success:
                self.authenticated = True
                self.last_heartbeat = datetime.now()
                self.logger.info(f"Successfully connected to {self.broker_type.value}")
            else:
                self.logger.error(f"Failed to connect to {self.broker_type.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error connecting to broker: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from broker API"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            self.authenticated = False
            self.logger.info(f"Disconnected from {self.broker_type.value}")
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from broker: {e}")
    
    async def _authenticate_oanda(self) -> bool:
        """Authenticate with OANDA API"""
        try:
            if not self.api_key:
                self.logger.error("OANDA API key not provided")
                return False
            
            # Test authentication by getting account info
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/v3/accounts"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'accounts' in data and data['accounts']:
                        # Use first account if account_id not specified
                        if not self.account_id:
                            self.account_id = data['accounts'][0]['id']
                        return True
                else:
                    self.logger.error(f"OANDA authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"OANDA authentication error: {e}")
            return False
    
    async def _authenticate_fxcm(self) -> bool:
        """Authenticate with FXCM API"""
        try:
            # FXCM uses token-based authentication
            if not self.api_key:
                self.logger.error("FXCM API token not provided")
                return False
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/trading/get_model"
            params = {'models': 'Account'}
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return True
                else:
                    self.logger.error(f"FXCM authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"FXCM authentication error: {e}")
            return False
    
    async def _authenticate_exness(self) -> bool:
        """Authenticate with Exness API"""
        try:
            # Exness uses OAuth2 authentication
            if not self.api_key or not self.api_secret:
                self.logger.error("Exness API credentials not provided")
                return False
            
            # For demo purposes, assume authentication is successful
            # In real implementation, this would perform OAuth2 flow
            self.logger.info("Exness authentication simulated (demo mode)")
            return True
                    
        except Exception as e:
            self.logger.error(f"Exness authentication error: {e}")
            return False
    
    async def _authenticate_paper_trading(self) -> bool:
        """Initialize paper trading mode"""
        try:
            # Paper trading doesn't require real authentication
            self.logger.info("Paper trading mode initialized")
            
            # Initialize paper trading account
            self.paper_account = {
                'balance': self.config.get('initial_balance', 10000.0),
                'equity': self.config.get('initial_balance', 10000.0),
                'margin_used': 0.0,
                'currency': 'USD',
                'leverage': self.config.get('leverage', 100)
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Paper trading initialization error: {e}")
            return False
    
    async def place_order(self, order: TradeOrder) -> Optional[str]:
        """Place a trading order"""
        try:
            if not self.authenticated:
                self.logger.error("Not authenticated with broker")
                return None
            
            # Check rate limits
            if not self._check_rate_limit():
                self.logger.error("Rate limit exceeded")
                return None
            
            # Place order based on broker type
            if self.broker_type == BrokerType.OANDA:
                order_id = await self._place_oanda_order(order)
            elif self.broker_type == BrokerType.FXCM:
                order_id = await self._place_fxcm_order(order)
            elif self.broker_type == BrokerType.EXNESS:
                order_id = await self._place_exness_order(order)
            elif self.broker_type == BrokerType.PAPER_TRADING:
                order_id = await self._place_paper_order(order)
            else:
                order_id = None
            
            if order_id:
                order.order_id = order_id
                self.active_orders[order_id] = order
                self.logger.info(f"Order placed: {order_id} for {order.symbol}")
            
            return order_id
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None
    
    async def _place_oanda_order(self, order: TradeOrder) -> Optional[str]:
        """Place order with OANDA"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Convert order to OANDA format
            oanda_order = {
                'order': {
                    'type': 'MARKET' if order.order_type == OrderType.MARKET else 'LIMIT',
                    'instrument': order.symbol,
                    'units': str(int(order.quantity)) if order.side == 'buy' else str(-int(order.quantity)),
                    'timeInForce': 'FOK' if order.order_type == OrderType.MARKET else 'GTC'
                }
            }
            
            if order.price and order.order_type != OrderType.MARKET:
                oanda_order['order']['price'] = str(order.price)
            
            if order.stop_loss:
                oanda_order['order']['stopLossOnFill'] = {'price': str(order.stop_loss)}
            
            if order.take_profit:
                oanda_order['order']['takeProfitOnFill'] = {'price': str(order.take_profit)}
            
            url = f"{self.base_url}/v3/accounts/{self.account_id}/orders"
            
            async with self.session.post(url, headers=headers, json=oanda_order) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    if 'orderCreateTransaction' in data:
                        return data['orderCreateTransaction']['id']
                else:
                    error_data = await response.text()
                    self.logger.error(f"OANDA order failed: {response.status} - {error_data}")
                    
        except Exception as e:
            self.logger.error(f"OANDA order placement error: {e}")
        
        return None
    
    async def _place_fxcm_order(self, order: TradeOrder) -> Optional[str]:
        """Place order with FXCM"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Convert order to FXCM format
            fxcm_order = {
                'symbol': order.symbol,
                'is_buy': order.side == 'buy',
                'amount': int(order.quantity),
                'time_in_force': 'GTC',
                'order_type': 'AtMarket' if order.order_type == OrderType.MARKET else 'Entry'
            }
            
            if order.price and order.order_type != OrderType.MARKET:
                fxcm_order['rate'] = order.price
            
            if order.stop_loss:
                fxcm_order['stop'] = order.stop_loss
            
            if order.take_profit:
                fxcm_order['limit'] = order.take_profit
            
            url = f"{self.base_url}/trading/open_trade"
            
            async with self.session.post(url, headers=headers, json=fxcm_order) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data and 'orderId' in data['data']:
                        return str(data['data']['orderId'])
                else:
                    error_data = await response.text()
                    self.logger.error(f"FXCM order failed: {response.status} - {error_data}")
                    
        except Exception as e:
            self.logger.error(f"FXCM order placement error: {e}")
        
        return None
    
    async def _place_exness_order(self, order: TradeOrder) -> Optional[str]:
        """Place order with Exness (simulated)"""
        try:
            # Simulate Exness order placement
            order_id = f"EXN_{int(time.time() * 1000)}"
            
            # Simulate order processing delay
            await asyncio.sleep(0.1)
            
            # Simulate successful order placement
            self.logger.info(f"Exness order simulated: {order_id}")
            return order_id
                    
        except Exception as e:
            self.logger.error(f"Exness order placement error: {e}")
        
        return None
    
    async def _place_paper_order(self, order: TradeOrder) -> Optional[str]:
        """Place paper trading order"""
        try:
            # Generate order ID
            order_id = f"PAPER_{int(time.time() * 1000)}"
            
            # Simulate market execution for market orders
            if order.order_type == OrderType.MARKET:
                # Simulate immediate fill at current market price
                # In real implementation, this would use actual market data
                fill_price = order.price if order.price else 1.1000  # Default price
                
                order.status = OrderStatus.FILLED
                order.fill_price = fill_price
                order.fill_time = datetime.now()
                
                # Update paper account
                await self._update_paper_position(order)
                
                self.logger.info(f"Paper order filled: {order_id} at {fill_price}")
            else:
                # Pending order
                order.status = OrderStatus.PENDING
                self.logger.info(f"Paper order placed: {order_id} (pending)")
            
            return order_id
                    
        except Exception as e:
            self.logger.error(f"Paper order placement error: {e}")
        
        return None
    
    async def _update_paper_position(self, order: TradeOrder):
        """Update paper trading position"""
        try:
            position_id = f"{order.symbol}_{order.side}"
            
            if position_id in self.positions:
                # Update existing position
                position = self.positions[position_id]
                
                # Calculate new average price
                total_quantity = position.quantity + order.quantity
                if total_quantity > 0:
                    new_avg_price = (
                        (position.entry_price * position.quantity + order.fill_price * order.quantity) 
                        / total_quantity
                    )
                    position.entry_price = new_avg_price
                    position.quantity = total_quantity
                else:
                    # Position closed
                    del self.positions[position_id]
            else:
                # Create new position
                position = Position(
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    entry_price=order.fill_price,
                    current_price=order.fill_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    commission=order.commission,
                    swap=0.0,
                    open_time=datetime.now(),
                    position_id=position_id
                )
                
                self.positions[position_id] = position
                    
        except Exception as e:
            self.logger.error(f"Error updating paper position: {e}")
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order"""
        try:
            if not self.authenticated:
                self.logger.error("Not authenticated with broker")
                return False
            
            if order_id not in self.active_orders:
                self.logger.error(f"Order {order_id} not found")
                return False
            
            # Cancel order based on broker type
            if self.broker_type == BrokerType.OANDA:
                success = await self._cancel_oanda_order(order_id)
            elif self.broker_type == BrokerType.FXCM:
                success = await self._cancel_fxcm_order(order_id)
            elif self.broker_type == BrokerType.EXNESS:
                success = await self._cancel_exness_order(order_id)
            elif self.broker_type == BrokerType.PAPER_TRADING:
                success = await self._cancel_paper_order(order_id)
            else:
                success = False
            
            if success:
                order = self.active_orders[order_id]
                order.status = OrderStatus.CANCELLED
                del self.active_orders[order_id]
                self.order_history.append(order)
                self.logger.info(f"Order cancelled: {order_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return False
    
    async def _cancel_paper_order(self, order_id: str) -> bool:
        """Cancel paper trading order"""
        try:
            # Simulate order cancellation
            self.logger.info(f"Paper order cancelled: {order_id}")
            return True
                    
        except Exception as e:
            self.logger.error(f"Paper order cancellation error: {e}")
            return False
    
    async def get_account_info(self) -> Optional[AccountInfo]:
        """Get account information"""
        try:
            if not self.authenticated:
                self.logger.error("Not authenticated with broker")
                return None
            
            # Get account info based on broker type
            if self.broker_type == BrokerType.OANDA:
                return await self._get_oanda_account_info()
            elif self.broker_type == BrokerType.FXCM:
                return await self._get_fxcm_account_info()
            elif self.broker_type == BrokerType.EXNESS:
                return await self._get_exness_account_info()
            elif self.broker_type == BrokerType.PAPER_TRADING:
                return await self._get_paper_account_info()
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return None
    
    async def _get_paper_account_info(self) -> Optional[AccountInfo]:
        """Get paper trading account info"""
        try:
            # Calculate current equity based on positions
            equity = self.paper_account['balance']
            
            for position in self.positions.values():
                # Simulate current P&L (in real implementation, use current market prices)
                pnl = (position.current_price - position.entry_price) * position.quantity
                if position.side == 'sell':
                    pnl = -pnl
                equity += pnl
            
            self.paper_account['equity'] = equity
            
            return AccountInfo(
                account_id="PAPER_ACCOUNT",
                balance=self.paper_account['balance'],
                equity=equity,
                margin_used=self.paper_account['margin_used'],
                margin_available=equity - self.paper_account['margin_used'],
                currency=self.paper_account['currency'],
                leverage=self.paper_account['leverage']
            )
                    
        except Exception as e:
            self.logger.error(f"Error getting paper account info: {e}")
            return None
    
    async def get_positions(self) -> List[Position]:
        """Get current positions"""
        try:
            if not self.authenticated:
                self.logger.error("Not authenticated with broker")
                return []
            
            # Get positions based on broker type
            if self.broker_type == BrokerType.PAPER_TRADING:
                return list(self.positions.values())
            else:
                # For real brokers, implement actual position retrieval
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_request_time > 60:
            self.request_count = 0
            self.last_request_time = current_time
        
        if self.request_count >= self.rate_limit:
            return False
        
        self.request_count += 1
        return True
    
    async def heartbeat(self):
        """Send heartbeat to maintain connection"""
        try:
            if self.authenticated:
                self.last_heartbeat = datetime.now()
                # Implement broker-specific heartbeat if needed
                
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
    
    def get_broker_status(self) -> Dict:
        """Get broker connection status"""
        return {
            'broker_type': self.broker_type.value,
            'authenticated': self.authenticated,
            'is_demo': self.is_demo,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'active_orders': len(self.active_orders),
            'positions': len(self.positions),
            'request_count': self.request_count,
            'rate_limit': self.rate_limit
        }

# Example usage and testing
async def test_broker_integration():
    """Test broker integration functionality"""
    # Test paper trading
    config = {
        'initial_balance': 10000.0,
        'leverage': 100,
        'rate_limit': 60
    }
    
    broker = BrokerIntegration(BrokerType.PAPER_TRADING, config)
    
    try:
        # Connect
        connected = await broker.connect()
        print(f"Connected: {connected}")
        
        if connected:
            # Get account info
            account_info = await broker.get_account_info()
            if account_info:
                print(f"Account Balance: ${account_info.balance}")
                print(f"Account Equity: ${account_info.equity}")
            
            # Place a test order
            test_order = TradeOrder(
                symbol='EURUSD',
                order_type=OrderType.MARKET,
                side='buy',
                quantity=10000,
                price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100
            )
            
            order_id = await broker.place_order(test_order)
            print(f"Order placed: {order_id}")
            
            # Get positions
            positions = await broker.get_positions()
            print(f"Positions: {len(positions)}")
            
            for position in positions:
                print(f"  {position.symbol}: {position.quantity} @ {position.entry_price}")
            
            # Get broker status
            status = broker.get_broker_status()
            print(f"Broker Status: {status}")
        
    finally:
        await broker.disconnect()

if __name__ == "__main__":
    # Run test
    asyncio.run(test_broker_integration())

