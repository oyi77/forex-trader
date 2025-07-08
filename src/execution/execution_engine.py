import ccxt
import time
from datetime import datetime

class ExecutionEngine:
    def __init__(self, exchange_id='binance', config=None, demo_mode=True):
        self.exchange_id = exchange_id
        self.demo_mode = demo_mode
        self.exchange = getattr(ccxt, exchange_id)()
        self.positions = {}  # Track open positions
        
        if config and not demo_mode:
            self.exchange.apiKey = config.get(f'{exchange_id.upper()}_API_KEY')
            self.exchange.secret = config.get(f'{exchange_id.upper()}_API_SECRET')
            try:
                self.exchange.load_markets()
            except Exception as e:
                print(f"Error loading markets: {e}")

    def place_order(self, symbol, order_type, side, amount, price=None, params={}):
        """Place an order with proper error handling"""
        if self.demo_mode:
            print(f"DEMO MODE: Placing {side} {order_type} order for {amount} {symbol} at {price if price else 'market'}")
            
            # Simulate order execution
            order_result = {
                'info': 'demo_order',
                'id': f'demo_order_{int(time.time())}',
                'datetime': self.exchange.iso8601(self.exchange.milliseconds()),
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'price': price or self._get_mock_price(symbol),
                'amount': amount,
                'cost': amount * (price or self._get_mock_price(symbol)),
                'status': 'closed' if order_type == 'market' else 'open',
                'filled': amount if order_type == 'market' else 0,
                'remaining': 0 if order_type == 'market' else amount
            }
            
            # Track position in demo mode
            if order_type == 'market' and order_result['status'] == 'closed':
                self._track_position(symbol, side, amount, order_result['price'])
            
            return order_result
        else:
            try:
                if order_type == 'limit':
                    order = self.exchange.create_limit_order(symbol, side, amount, price, params)
                elif order_type == 'market':
                    order = self.exchange.create_market_order(symbol, side, amount, params)
                elif order_type == 'stop':
                    order = self.exchange.create_stop_order(symbol, side, amount, price, params)
                else:
                    raise ValueError(f"Unsupported order type: {order_type}")
                
                print(f"Placed {side} {order_type} order for {amount} {symbol}. Order ID: {order['id']}")
                return order
            except Exception as e:
                print(f"Error placing order: {e}")
                return None

    def _get_mock_price(self, symbol):
        """Get mock price for demo mode"""
        # Simple mock price generation
        base_prices = {
            'BTC/USDT': 45000,
            'ETH/USDT': 3000,
            'XRP/USDT': 0.5,
            'LTC/USDT': 150,
            'BCH/USDT': 250,
            'ADA/USDT': 0.4,
            'DOT/USDT': 7,
            'LINK/USDT': 15,
            'SOL/USDT': 100,
            'BNB/USDT': 300
        }
        return base_prices.get(symbol, 100) + (hash(symbol) % 1000) / 100

    def _track_position(self, symbol, side, amount, price):
        """Track position in demo mode"""
        if symbol not in self.positions:
            self.positions[symbol] = []
        
        position = {
            'side': side,
            'amount': amount,
            'entry_price': price,
            'entry_time': datetime.now(),
            'pnl': 0
        }
        self.positions[symbol].append(position)

    def get_open_orders(self, symbol=None):
        """Get open orders"""
        if self.demo_mode:
            print("DEMO MODE: Fetching open orders (simulated).")
            return []  # Simulate no open orders in demo
        else:
            try:
                orders = self.exchange.fetch_open_orders(symbol)
                return orders
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
            try:
                positions = self.exchange.fetch_positions(symbol)
                return positions
            except Exception as e:
                print(f"Error fetching positions: {e}")
                return []

    def cancel_order(self, order_id, symbol=None):
        """Cancel an order"""
        if self.demo_mode:
            print(f"DEMO MODE: Cancelling order {order_id} (simulated).")
            return {'status': 'canceled', 'id': order_id}
        else:
            try:
                cancel_result = self.exchange.cancel_order(order_id, symbol)
                print(f"Order {order_id} cancelled.")
                return cancel_result
            except Exception as e:
                print(f"Error cancelling order {order_id}: {e}")
                return None

    def modify_order(self, order_id, symbol, order_type, side, amount, price, params={}):
        """Modify an existing order"""
        if self.demo_mode:
            print(f"DEMO MODE: Modifying order {order_id} (simulated).")
            return {
                'id': order_id,
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'amount': amount,
                'price': price,
                'status': 'open'
            }
        else:
            try:
                modified_order = self.exchange.edit_order(order_id, symbol, order_type, side, amount, price, params)
                print(f"Order {order_id} modified.")
                return modified_order
            except Exception as e:
                print(f"Error modifying order {order_id}: {e}")
                return None

    def apply_trailing_sl_or_breakeven(self, position, current_price, tp1_hit=False):
        """Apply trailing stop loss or move to breakeven"""
        if self.demo_mode:
            print(f"DEMO MODE: Applying trailing SL/breakeven for position {position.get('symbol')}.")
            return

        try:
            symbol = position.get('symbol')
            entry_price = position.get('entry_price')
            side = position.get('side')
            
            if tp1_hit:
                print(f"TP1 hit for {symbol}. Moving SL to breakeven.")
                # Move SL to entry price (breakeven)
                new_sl = entry_price
            else:
                print(f"Applying trailing SL for {symbol}.")
                # Calculate trailing SL based on current price
                if side == 'buy':
                    new_sl = current_price * 0.995  # 0.5% below current price
                else:
                    new_sl = current_price * 1.005  # 0.5% above current price
            
            # In a real implementation, you would modify the existing SL order
            # or place a new one with the updated price
            print(f"New SL for {symbol}: {new_sl}")
            
        except Exception as e:
            print(f"Error applying trailing SL: {e}")

    def get_account_balance(self):
        """Get account balance"""
        if self.demo_mode:
            return {
                'USDT': {'free': 10000, 'used': 0, 'total': 10000},
                'BTC': {'free': 0.1, 'used': 0, 'total': 0.1},
                'ETH': {'free': 1.0, 'used': 0, 'total': 1.0}
            }
        else:
            try:
                balance = self.exchange.fetch_balance()
                return balance
            except Exception as e:
                print(f"Error fetching balance: {e}")
                return {}

    def get_ticker(self, symbol):
        """Get current ticker for a symbol"""
        if self.demo_mode:
            mock_price = self._get_mock_price(symbol)
            return {
                'symbol': symbol,
                'last': mock_price,
                'bid': mock_price * 0.999,
                'ask': mock_price * 1.001,
                'high': mock_price * 1.02,
                'low': mock_price * 0.98,
                'volume': 1000
            }
        else:
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                return ticker
            except Exception as e:
                print(f"Error fetching ticker for {symbol}: {e}")
                return None

# Example Usage (will be integrated into main.py later)
if __name__ == "__main__":
    # This would typically come from config.yaml
    mock_config = {
        'BINANCE_API_KEY': 'YOUR_BINANCE_API_KEY',
        'BINANCE_API_SECRET': 'YOUR_BINANCE_API_SECRET',
    }
    exec_engine = ExecutionEngine(exchange_id='binance', config=mock_config, demo_mode=True)

    # Simulate a buy signal
    symbol = 'BTC/USDT'
    entry_price = 30000
    amount = 0.001

    # Place a simulated market buy order
    order_result = exec_engine.place_order(symbol, 'market', 'buy', amount)
    print(f"\nOrder Result: {order_result}")

    # Get account balance
    balance = exec_engine.get_account_balance()
    print(f"\nAccount Balance: {balance}")

    # Get current positions
    positions = exec_engine.get_positions()
    print(f"\nCurrent Positions: {positions}")


