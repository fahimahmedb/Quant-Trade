#!/usr/bin/env python3
"""
Setup Telegram Bot - Interactive guide
Walks through creating a Telegram bot and getting credentials
"""
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key

def print_header(text):
    print("\n" + "="*60)
    print(text.center(60))
    print("="*60 + "\n")

def print_step(num, text):
    print(f"\n{num}️⃣ {text}")
    print("-" * 60)

def test_telegram_connection(bot_token):
    """Test if bot token is valid"""
    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getMe",
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get('ok'):
                return True, data['result']
        return False, None
    except:
        return False, None

def main():
    print_header("🤖 QUANT-TRADE ROBOT - TELEGRAM BOT SETUP")

    # Step 1: Instructions
    print_step("1", "CREATE BOT ON TELEGRAM")
    print("""
1. Open Telegram app
2. Search for: @BotFather
3. Send: /newbot
4. Follow instructions:
   - Name: "Quant-Robot-Trader"
   - Username: "quant_robot_XXXXX" (must be unique, add your username)
5. BotFather will give you a TOKEN

⏸️  PAUSE HERE and complete steps above
    """)

    input("Press ENTER when bot is created...")

    # Step 2: Get bot token
    print_step("2", "ENTER BOT TOKEN")
    print("Copy the TOKEN from BotFather's message:")
    print("Example: 6234567890:ABCDEfGhIjKlMnOpQrStUvWxYz")

    bot_token = input("\n🔐 Paste your BOT_TOKEN: ").strip()

    if not bot_token or ":" not in bot_token:
        print("❌ Invalid token format")
        return 1

    # Test token
    print("\n⏳ Testing bot token...")
    valid, bot_info = test_telegram_connection(bot_token)

    if not valid:
        print("❌ Token is invalid or bot is offline")
        print("Please check your token and try again")
        return 1

    print(f"✅ Bot connected: @{bot_info.get('username', 'unknown')}")

    # Step 3: Get Chat ID
    print_step("3", "GET YOUR CHAT ID")
    print(f"""
1. Send any message to your new bot @{bot_info.get('username')}
2. Open this link (replace TOKEN with your token):

   https://api.telegram.org/bot{bot_token}/getUpdates

3. Look for "id" field in the response
4. Example response:
   {{"message":{{"chat":{{"id":123456789}}}}}}

   Your Chat ID is: 123456789

⏸️  PAUSE HERE and get your Chat ID
    """)

    input("Press ENTER when ready...")

    print("\n🔐 Enter your Chat ID:")
    chat_id = input("Paste your CHAT_ID: ").strip()

    if not chat_id or not chat_id.isdigit():
        print("❌ Invalid Chat ID")
        return 1

    # Step 4: Test connection to chat
    print("\n⏳ Testing Telegram message...")
    try:
        test_msg = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": "✅ Robot setup test - Connection successful!"
            },
            timeout=5
        )
        if test_msg.status_code == 200:
            print("✅ Message sent successfully!")
        else:
            print(f"⚠️  Message not sent: {test_msg.status_code}")
    except Exception as e:
        print(f"⚠️  Error: {e}")

    # Step 5: Save credentials
    print_step("4", "SAVE CREDENTIALS")

    env_file = Path(".env")
    if env_file.exists():
        # Update existing .env
        set_key(".env", "TELEGRAM_BOT_TOKEN", bot_token)
        set_key(".env", "TELEGRAM_CHAT_ID", chat_id)
        print(f"✅ Updated {env_file}")
    else:
        # Create new .env from template
        env_template = Path(".env.example")
        if env_template.exists():
            with open(env_template) as f:
                content = f.read()
            content = content.replace("your_bot_token_here", bot_token)
            content = content.replace("your_chat_id_here", chat_id)
            with open(".env", "w") as f:
                f.write(content)
            print(f"✅ Created {env_file}")
        else:
            print("⚠️  .env.example not found")
            with open(".env", "w") as f:
                f.write(f"TELEGRAM_BOT_TOKEN={bot_token}\n")
                f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
            print(f"✅ Created {env_file}")

    # Step 6: Verify setup
    print_step("5", "VERIFY SETUP")

    load_dotenv()
    stored_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    stored_chat = os.getenv("TELEGRAM_CHAT_ID", "")

    if stored_token == bot_token and stored_chat == chat_id:
        print("✅ Credentials saved correctly")
    else:
        print("❌ Credentials not saved properly")
        return 1

    # Summary
    print_header("✅ TELEGRAM BOT SETUP COMPLETE")

    print(f"""
Bot Configuration:
  Bot Name: @{bot_info.get('username')}
  Bot Token: {bot_token[:20]}...
  Chat ID: {chat_id}

File: .env (don't commit to Git!)

Next Steps:
  1. Run tests: python test_local.py
  2. Deploy: ./deploy.sh

The robot will send messages to this chat.
    """)

    return 0

if __name__ == "__main__":
    sys.exit(main())
