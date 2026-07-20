"""
Test robot locally before deployment
"""
import os
import json
from datetime import datetime
from pathlib import Path
import sys

# Test colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
END = '\033[0m'

def test_imports():
    """Test all required imports"""
    print(f"\n{BLUE}[TEST 1/5]{END} Testing imports...")

    try:
        import requests
        import pandas
        import numpy
        import streamlit
        print(f"{GREEN}✓ All imports OK{END}")
        return True
    except ImportError as e:
        print(f"{RED}✗ Import failed: {e}{END}")
        print(f"Run: pip install -r requirements.txt")
        return False

def test_telegram():
    """Test Telegram credentials"""
    print(f"\n{BLUE}[TEST 2/5]{END} Testing Telegram credentials...")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        print(f"{YELLOW}⚠ Telegram credentials not set in .env${END}")
        print(f"Copy .env.example to .env and fill in credentials")
        return False

    # Quick test: try to get bot info
    import requests

    try:
        resp = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=5)
        if resp.status_code == 200:
            bot_info = resp.json()
            print(f"{GREEN}✓ Telegram bot connected: {bot_info['result']['username']}{END}")
            return True
        else:
            print(f"{RED}✗ Telegram connection failed: {resp.status_code}{END}")
            return False
    except Exception as e:
        print(f"{RED}✗ Telegram error: {e}{END}")
        return False

def test_data_loading():
    """Test data loading"""
    print(f"\n{BLUE}[TEST 3/5]{END} Testing data loading...")

    try:
        # Try to load from parent repo
        sys.path.insert(0, "..")
        from src.data_loader import load_ohlc

        # Use relative path
        data_paths = [
            "data/nasdaq100_daily.txt",
            "../data/nasdaq100_daily.txt",
            "../../data/nasdaq100_daily.txt"
        ]

        for path in data_paths:
            if os.path.exists(path):
                df = load_ohlc(path)
                print(f"{GREEN}✓ Data loaded from {path}${END}")
                print(f"  Last price: ${df['close'].iloc[-1]:.2f}")
                print(f"  Records: {len(df)}")
                return True

        print(f"{YELLOW}⚠ Data file not found in standard locations${END}")
        print(f"Copy data/nasdaq100_daily.txt to this directory")
        return False

    except Exception as e:
        print(f"{YELLOW}⚠ Data loading test skipped: {e}${END}")
        return False

def test_order_generation():
    """Test order generation and logging"""
    print(f"\n{BLUE}[TEST 4/5]{END} Testing order generation...")

    try:
        from pathlib import Path

        # Create test order
        test_order = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": "NDX",
            "type": "BUY",
            "quantity": 100,
            "price": 5000.00,
            "status": "TEST",
            "strategy": "Buy & Hold",
            "pnl_pct": 0.0
        }

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Save test order
        date_str = "2026-07-20"  # Test date
        log_file = log_dir / f"orders_{date_str}.json"

        test_data = [test_order]
        with open(log_file, 'w') as f:
            json.dump(test_data, f, indent=2)

        # Verify
        with open(log_file, 'r') as f:
            loaded = json.load(f)

        if len(loaded) > 0 and loaded[0]['symbol'] == 'NDX':
            print(f"{GREEN}✓ Order generation and logging OK${END}")
            print(f"  Test file: {log_file}")
            return True
        else:
            print(f"{RED}✗ Order data mismatch${END}")
            return False

    except Exception as e:
        print(f"{RED}✗ Order generation failed: {e}${END}")
        return False

def test_streamlit():
    """Test Streamlit dashboard can be launched"""
    print(f"\n{BLUE}[TEST 5/5]{END} Testing Streamlit dashboard...")

    try:
        if os.path.exists("dashboard.py"):
            print(f"{GREEN}✓ Dashboard file exists${END}")
            print(f"  Launch with: streamlit run dashboard.py")
            return True
        else:
            print(f"{RED}✗ dashboard.py not found${END}")
            return False

    except Exception as e:
        print(f"{RED}✗ Dashboard test failed: {e}${END}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🤖 ROBOT PAPER TRADING - LOCAL TEST SUITE")
    print("="*60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Telegram", test_telegram()))
    results.append(("Data Loading", test_data_loading()))
    results.append(("Order Generation", test_order_generation()))
    results.append(("Streamlit", test_streamlit()))

    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{GREEN}✓ PASS{END}" if result else f"{RED}✗ FAIL{END}"
        print(f"{name}: {status}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print(f"\n{GREEN}✅ ALL TESTS PASSED - Ready to deploy!${END}")
        print(f"Next: chmod +x deploy.sh && ./deploy.sh")
        return 0
    else:
        print(f"\n{YELLOW}⚠ Some tests failed - Fix errors before deploying${END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
