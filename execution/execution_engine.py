import ccxt

class ExecutionEngine:
    def __init__(self, exchange_id='binance', config=None, demo_mode=True):
        self.exchange_id = exchange_id
        self.demo_mode = demo_mode
        self.exchange = getattr(ccxt, exchange_id)()
        if config and not demo_mode:
            self.exchange.apiKey = config.get(f'{exchange_id.upper()}_API_KEY')
            self.exchange.secret = config.get(f'{exchange_id.upper()}_API_SECRET')
            self.exchange.load_markets()

    def place_order(self, symbol, order_type, side, amount, price=None, params={}):
        if self.demo_mode:
            print(f"DEMO MODE: Placing {side} {order_type} order for {amount} {symbol} at {price if price else 'market'}")
            return {
                'info': 'demo_order',
                'id': 'demo_order_id_123',
                'datetime': self.exchange.iso8601(self.exchange.milliseconds()),
                'symbol': symbol,
                'type': order_type,
                'side': side,
                'price': price,
                'amount': amount,
                'cost': amount * price if price else None,
                'status': 'closed' if order_type == 'market' else 'open'
            }
        else:
            try:
                if order_type == 'limit':
                    order = self.exchange.create_limit_order(symbol, side, amount, price, params)
                elif order_type == 'market':
                    order = self.exchange.create_market_order(symbol, side, amount, params)
                else:
                    raise ValueError("Unsupported order type")
                print(f"Placed {side} {order_type} order for {amount} {symbol}. Order ID: {order['id']}")
                return order
            except Exception as e:
                print(f"Error placing order: {e}")
                return None

    def get_open_orders(self, symbol=None):
        if self.demo_mode:
            print("DEMO MODE: Fetching open orders (simulated).")
            return [] # Simulate no open orders in demo
        else:
            try:
                orders = self.exchange.fetch_open_orders(symbol)
                return orders
            except Exception as e:
                print(f"Error fetching open orders: {e}")
                return []

    def cancel_order(self, order_id, symbol=None):
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

    def apply_trailing_sl_or_breakeven(self, position, current_price, tp1_hit=False):
        # This is a simplified logic. In a real system, this would involve:
        # 1. Checking if TP1 is hit (passed as argument or determined internally)
        # 2. Calculating new SL based on trailing logic (e.g., X pips/percentage behind current price)
        # 3. Modifying existing SL order or placing a new one.

        if self.demo_mode:
            print(f"DEMO MODE: Applying trailing SL/breakeven for position {position.get('symbol')}.")
            return

        if tp1_hit:
            print(f"TP1 hit for {position.get('symbol')}. Moving SL to breakeven.")
            # Logic to modify SL to entry price (breakeven)
            # This would typically involve cancelling the old SL order and placing a new one.
        else:
            print(f"Applying trailing SL for {position.get('symbol')}.")
            # Logic to trail SL based on current price and a defined offset

# Example Usage (will be integrated into main.py later)
# if __name__ == "__main__":
#     # This would typically come from config.yaml
#     mock_config = {
#         'BINANCE_API_KEY': 'YOUR_BINANCE_API_KEY',
#         'BINANCE_API_SECRET': 'YOUR_BINANCE_API_SECRET',
#     }
#     exec_engine = ExecutionEngine(exchange_id='binance', config=mock_config, demo_mode=True)

#     # Simulate a buy signal
#     symbol = 'BTC/USDT'
#     entry_price = 30000
#     amount = 0.001

#     # Place a simulated market buy order
#     order_result = exec_engine.place_order(symbol, 'market', 'buy', amount)
#     print(f"\nOrder Result: {order_result}")

#     # Simulate a position for trailing SL/breakeven
#     simulated_position = {
#         'symbol': symbol,
#         'entry_price': entry_price,
#         'current_sl': entry_price * 0.99,
#         'side': 'buy',
#         'amount': amount
#     }

#     # Apply trailing SL (no TP1 hit yet)
#     exec_engine.apply_trailing_sl_or_breakeven(simulated_position, 30100, tp1_hit=False)

#     # Simulate TP1 hit and apply breakeven
#     exec_engine.apply_trailing_sl_or_breakeven(simulated_position, 30500, tp1_hit=True)


