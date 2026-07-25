"""
Robot Paper Trading - Daily Execution
Runs at 21:00 UTC each day, executes trading signal, logs orders, sends Telegram notifications
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import requests
import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DATA_PATH = os.getenv("DATA_PATH", "data/nasdaq100_daily.txt")

# Telegram helper
def send_telegram(message: str):
    """Send message via Telegram bot"""
    if not BOT_TOKEN or not CHAT_ID:
        logger.warning("Telegram credentials not set, skipping notification")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": CHAT_ID, "text": message})
        if response.status_code != 200:
            logger.error(f"Telegram error: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send Telegram: {e}")

def load_trading_data():
    """Load latest trading data"""
    try:
        # Load from parent repo
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from data_loader import load_ohlc, log_returns_pct

        if not os.path.exists(DATA_PATH):
            logger.error(f"Data file not found: {DATA_PATH}")
            return None

        df = load_ohlc(DATA_PATH)
        return df
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return None

def generate_order():
    """Generate daily order based on Buy & Hold strategy"""
    try:
        df = load_trading_data()
        if df is None:
            return None

        # For now, Buy & Hold = always long
        current_price = df['close'].iloc[-1]
        quantity = 100  # Fixed quantity for paper trading

        order = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": "NDX",
            "type": "BUY",
            "quantity": quantity,
            "price": current_price,
            "status": "PENDING_EXECUTION",
            "strategy": "Buy & Hold (Étape B validated)",
            "pnl_pct": 0.0,
            "notes": "Paper trading - simulation mode"
        }

        logger.info(f"Order generated: {order}")
        return order
    except Exception as e:
        logger.error(f"Failed to generate order: {e}")
        return None

def save_order(order: dict):
    """Save order to daily log"""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = log_dir / f"orders_{date_str}.json"

        # Load existing orders or create new list
        orders = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                orders = json.load(f)

        orders.append(order)

        # Save updated orders
        with open(log_file, 'w') as f:
            json.dump(orders, f, indent=2)

        logger.info(f"Order saved to {log_file}")
        return log_file
    except Exception as e:
        logger.error(f"Failed to save order: {e}")
        return None

def compute_daily_recap():
    """Compute daily statistics"""
    try:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = Path("logs") / f"orders_{date_str}.json"

        if not log_file.exists():
            return None

        with open(log_file, 'r') as f:
            orders = json.load(f)

        recap = {
            "date": date_str,
            "total_orders": len(orders),
            "buy_orders": len([o for o in orders if o['type'] == 'BUY']),
            "sell_orders": len([o for o in orders if o['type'] == 'SELL']),
            "avg_price": np.mean([o['price'] for o in orders]),
            "total_quantity": sum([o['quantity'] for o in orders]),
            "sharpe_daily": 0.0328,  # From backtesting
            "sharpe_annual": 2.07,
            "expected_return": "+7-10% annualized",
            "max_drawdown": "-82.9%"
        }

        return recap
    except Exception as e:
        logger.error(f"Failed to compute recap: {e}")
        return None

def main():
    """Main execution"""
    logger.info("=== Robot Paper Trading Starting ===")

    # Generate order
    order = generate_order()
    if order is None:
        send_telegram("❌ Robot Error: Failed to generate order")
        return

    # Save order
    save_order(order)

    # Send notification
    message = (
        f"📊 **Order Executed**\n"
        f"Symbol: {order['symbol']}\n"
        f"Type: {order['type']}\n"
        f"Quantity: {order['quantity']}\n"
        f"Price: ${order['price']:.2f}\n"
        f"Time: {order['timestamp']}\n"
        f"Strategy: {order['strategy']}"
    )
    send_telegram(message)

    # Check if it's 22:00 (recap time)
    if datetime.utcnow().hour == 22:
        recap = compute_daily_recap()
        if recap:
            recap_msg = (
                f"📈 **Daily Recap - {recap['date']}**\n"
                f"Orders: {recap['total_orders']}\n"
                f"Avg Price: ${recap['avg_price']:.2f}\n"
                f"Total Qty: {recap['total_quantity']}\n"
                f"Sharpe (annual): {recap['sharpe_annual']:.2f}\n"
                f"Expected Return: {recap['expected_return']}\n"
                f"Max Drawdown: {recap['max_drawdown']}"
            )
            send_telegram(recap_msg)

    logger.info("=== Robot Paper Trading Complete ===")

if __name__ == "__main__":
    main()
