#!/bin/bash

# ============================================================================
# QUICK SETUP SCRIPT - Automated Robot Deployment
# All-in-one setup for paper trading robot
# ============================================================================

set -e

echo ""
echo "🚀 QUANT-TRADE ROBOT - QUICK SETUP"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${BLUE}[1/4]${NC} Installing Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${BLUE}[2/4]${NC} Setting up Telegram Bot..."
python3 setup_telegram.py

echo ""
echo -e "${BLUE}[3/4]${NC} Running local tests..."
python3 test_local.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[4/4]${NC} Deploying to Google Cloud..."
echo ""
echo -e "${BLUE}Make sure you're logged in to Google Cloud:${NC}"
echo "  gcloud auth login"
echo ""
read -p "Continue with Cloud deployment? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Skipping Cloud deployment${NC}"
    echo ""
    echo "To deploy later, run: ./deploy.sh"
else
    chmod +x deploy.sh
    ./deploy.sh
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Launch dashboard locally: streamlit run dashboard.py"
echo "2. Push to GitHub and setup Streamlit Cloud"
echo "3. Check robot-credentials.txt for deployment info"
echo ""
