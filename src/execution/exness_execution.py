import time
from datetime import datetime
import pytz

# Try to import MetaTrader5, but handle case where it's not available
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("Warning: MetaTrader5 not available on this platform. Using demo mode only.")

class ExnessExecutionEngine:
    def __init__(self, config=None, demo_mode=True):
        self.demo_mode = demo_mode
        self.positions = {}  # Track open positions
        self.connected = False
        
        # Check if MT5 is available for live trading
        if not MT5_AVAILABLE and not demo_mode:
            print("Warning: MetaTrader5 not available. Forcing demo mode.")
            self.demo_mode = True
        
        if not self.demo_mode and config and MT5_AVAILABLE:
            self._connect_mt5(config)
        else:
            print("DEMO MODE: Exness execution engine initialized in demo mode")

    def _connect_mt5(self, config):
        """Connect to MetaTrader 5"""
        if not MT5_AVAILABLE:
            print("MetaTrader5 not available on this platform")
            return
            
        try:
            # Initialize MT5
            if not mt5.initialize():
                print(f"MT5 initialization failed: {mt5.last_error()}")
                return
            
            # Login to account
            login_result = mt5.login(
                login=config.get('EXNESS_LOGIN'),
                password=config.get('EXNESS_PASSWORD'),
                server=config.get('EXNESS_SERVER', 'Exness-MT5')
            )
            
            if login_result:
                self.connected = True
                print("Successfully connected to Exness MT5")
                # Get account info
                account_info = mt5.account_info()
                if account_info:
                    print(f"Account: {account_info.login}, Balance: {account_info.balance}, Equity: {account_info.equity}")
            else:
                print(f"MT5 login failed: {mt5.last_error()}")
                
        except Exception as e:
            print(f"Error connecting to MT5: {e}")

    def place_order(self, symbol, order_type, side, amount, price=None, sl=None, tp=None, params={}):
        """Place a forex order with Exness"""
        if self.demo_mode:
            return self._place_demo_order(symbol, order_type, side, amount, price, sl, tp)
        else:
            return self._place_live_order(symbol, order_type, side, amount, price, sl, tp)

    def _place_demo_order(self, symbol, order_type, side, amount, price, sl, tp):
        """Place a demo order"""
        print(f"DEMO MODE: Placing {side} {order_type} order for {amount} {symbol}")
        
        # Simulate order execution
        order_result = {
            'ticket': f'demo_{int(time.time())}',
            'symbol': symbol,
            'type': order_type,
            'side': side,
            'volume': amount,
            'price_open': price or self._get_mock_forex_price(symbol),
            'sl': sl,
            'tp': tp,
            'profit': 0,
            'status': 'closed' if order_type == 'market' else 'open',
            'time': datetime.now()
        }
        
        # Track position in demo mode
        if order_type == 'market':
            self._track_position(symbol, side, amount, order_result['price_open'], sl, tp)
        
        return order_result

    def _place_live_order(self, symbol, order_type, side, amount, price, sl, tp):
        """Place a live order on Exness"""
        if not MT5_AVAILABLE:
            print("MetaTrader5 not available for live trading")
            return None
            
        if not self.connected:
            print("Not connected to MT5")
            return None
        
        try:
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": amount,
                "type": mt5.ORDER_TYPE_BUY if side == 'buy' else mt5.ORDER_TYPE_SELL,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 234000,
                "comment": "AI Trading Engine",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Order placed successfully: {result.order}")
                return {
                    'ticket': result.order,
                    'symbol': symbol,
                    'type': order_type,
                    'side': side,
                    'volume': amount,
                    'price_open': result.price,
                    'sl': sl,
                    'tp': tp,
                    'status': 'closed',
                    'time': datetime.now()
                }
            else:
                print(f"Order failed: {result.retcode}, {result.comment}")
                return None
                
        except Exception as e:
            print(f"Error placing live order: {e}")
            return None

    def _get_mock_forex_price(self, symbol):
        """Get mock forex price for demo mode"""
        base_prices = {
            'EURUSD': 1.0850,
            'GBPUSD': 1.2650,
            'USDJPY': 148.50,
            'USDCHF': 0.8650,
            'AUDUSD': 0.6650,
            'USDCAD': 1.3550,
            'NZDUSD': 0.6150,
            'EURGBP': 0.8580,
            'EURJPY': 161.20,
            'GBPJPY': 187.80
        }
        return base_prices.get(symbol, 1.0000) + (hash(symbol) % 100) / 10000

    def _track_position(self, symbol, side, amount, price, sl, tp):
        """Track position in demo mode"""
        if symbol not in self.positions:
            self.positions[symbol] = []
        
        position = {
            'ticket': f'demo_{int(time.time())}',
            'symbol': symbol,
            'side': side,
            'volume': amount,
            'price_open': price,
            'sl': sl,
            'tp': tp,
            'profit': 0,
            'time': datetime.now()
        }
        self.positions[symbol].append(position)

    def get_open_orders(self, symbol=None):
        """Get open orders"""
        if self.demo_mode:
            print("DEMO MODE: Fetching open orders (simulated).")
            return []
        else:
            if not MT5_AVAILABLE:
                print("MetaTrader5 not available")
                return []
            try:
                orders = mt5.orders_get(symbol=symbol)
                return orders if orders else []
            except Exception as e:
                print(f"Error fetching open orders: {e}")
                return []

    def get_positions(self, symbol=None):
        """Get current positions"""
        if self.demo_mode:
            if symbol:
                return self.positions.get(symbol, [])
            return self.positions
        else:
            if not MT5_AVAILABLE:
                print("MetaTrader5 not available")
                return []
            try:
                positions = mt5.positions_get(symbol=symbol)
                return positions if positions else []
            except Exception as e:
                print(f"Error fetching positions: {e}")
                return []

    def close_position(self, ticket, symbol=None, volume=None):
        """Close a position"""
        if self.demo_mode:
            print(f"DEMO MODE: Closing position {ticket} (simulated).")
            # Remove from tracked positions
            for symbol_positions in self.positions.values():
                self.positions[symbol] = [p for p in symbol_positions if p.get('ticket') != ticket]
            return {'status': 'closed', 'ticket': ticket}
        else:
            if not MT5_AVAILABLE:
                print("MetaTrader5 not available")
                return None
            try:
                position = mt5.positions_get(ticket=ticket)
                if position:
                    pos = position[0]
                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": pos.symbol,
                        "volume": volume or pos.volume,
                        "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                        "position": ticket,
                        "price": mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask,
                        "deviation": 20,
                        "magic": 234000,
                        "comment": "AI Trading Engine - Close",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"Position {ticket} closed successfully")
                        return {'status': 'closed', 'ticket': ticket}
                    else:
                        print(f"Failed to close position: {result.retcode}")
                        return None
                else:
                    print(f"Position {ticket} not found")
                    return None
            except Exception as e:
                print(f"Error closing position: {e}")
                return None

    def modify_position(self, ticket, sl=None, tp=None):
        """Modify position stop loss or take profit"""
        if self.demo_mode:
            print(f"DEMO MODE: Modifying position {ticket} (simulated).")
            return {'status': 'modified', 'ticket': ticket}
        else:
            if not MT5_AVAILABLE:
                print("MetaTrader5 not available")
                return None
            try:
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": ticket,
                    "sl": sl,
                    "tp": tp
                }
                
                result = mt5.order_send(request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"Position {ticket} modified successfully")
                    return {'status': 'modified', 'ticket': ticket}
                else:
                    print(f"Failed to modify position: {result.retcode}")
                    return None
            except Exception as e:
                print(f"Error modifying position: {e}")
                return None

    def get_account_balance(self):
        """Get account balance"""
        if self.demo_mode:
            return {
                'balance': 10000.0,
                'equity': 10000.0,
                'margin': 0.0,
                'free_margin': 10000.0,
                'profit': 0.0
            }
        else:
            if not MT5_AVAILABLE:
                print("MetaTrader5 not available")
                return {
                    'balance': 10000.0,
                    'equity': 10000.0,
                    'margin': 0.0,
                    'free_margin': 10000.0,
                    'profit': 0.0
                }
            try:
                account_info = mt5.account_info()
                if account_info:
                    return {
                        'balance': account_info.balance,
                        'equity': account_info.equity,
                        'margin': account_info.margin,
                        'free_margin': account_info.margin_free,
                        'profit': account_info.profit
                    }
                return None
            except Exception as e:
                print(f"Error fetching account balance: {e}")
                return None

    def get_ticker(self, symbol):
        """Get current ticker for a symbol"""
        if self.demo_mode:
            price = self._get_mock_forex_price(symbol)
            return {
                'symbol': symbol,
                'bid': price - 0.0001,
                'ask': price + 0.0001,
                'last': price,
                'time': datetime.now()
            }
        else:
            if not MT5_AVAILABLE:
                print("MetaTrader5 not available")
                price = self._get_mock_forex_price(symbol)
                return {
                    'symbol': symbol,
                    'bid': price - 0.0001,
                    'ask': price + 0.0001,
                    'last': price,
                    'time': datetime.now()
                }
            try:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    return {
                        'symbol': symbol,
                        'bid': tick.bid,
                        'ask': tick.ask,
                        'last': tick.last,
                        'time': datetime.fromtimestamp(tick.time)
                    }
                return None
            except Exception as e:
                print(f"Error fetching ticker: {e}")
                return None

    def get_symbol_info(self, symbol):
        """Get symbol information"""
        if self.demo_mode:
            return {
                'symbol': symbol,
                'digits': 5,
                'spread': 10,
                'trade_mode': 4,
                'volume_min': 0.01,
                'volume_max': 100.0,
                'volume_step': 0.01
            }
        else:
            if not MT5_AVAILABLE:
                print("MetaTrader5 not available")
                return {
                    'symbol': symbol,
                    'digits': 5,
                    'spread': 10,
                    'trade_mode': 4,
                    'volume_min': 0.01,
                    'volume_max': 100.0,
                    'volume_step': 0.01
                }
            try:
                info = mt5.symbol_info(symbol)
                if info:
                    return {
                        'symbol': info.name,
                        'digits': info.digits,
                        'spread': info.spread,
                        'trade_mode': info.trade_mode,
                        'volume_min': info.volume_min,
                        'volume_max': info.volume_max,
                        'volume_step': info.volume_step
                    }
                return None
            except Exception as e:
                print(f"Error fetching symbol info: {e}")
                return None

    def shutdown(self):
        """Shutdown MT5 connection"""
        if not self.demo_mode and MT5_AVAILABLE:
            mt5.shutdown()
            print("MT5 connection closed") 