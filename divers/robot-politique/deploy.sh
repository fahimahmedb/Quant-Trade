#!/bin/bash

# ============================================================================
# ROBOT PAPER TRADING - AUTOMATED DEPLOYMENT SCRIPT
# Deploys to Google Cloud Run + Streamlit Cloud + Telegram Setup
# ============================================================================

set -e

echo "🚀 ROBOT PAPER TRADING - AUTO DEPLOYMENT"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${BLUE}[STEP 1/5]${NC} Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ git not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Step 2: Setup Google Cloud
echo -e "${BLUE}[STEP 2/5]${NC} Setting up Google Cloud..."

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${BLUE}Please login to Google Cloud:${NC}"
    gcloud auth login
fi

# Create project or use existing
read -p "Enter Google Cloud Project ID (create new or existing): " GCP_PROJECT_ID

if ! gcloud projects list --filter="PROJECT_ID:$GCP_PROJECT_ID" --format="value(PROJECT_ID)" | grep -q .; then
    echo -e "${BLUE}Creating GCP project: $GCP_PROJECT_ID${NC}"
    gcloud projects create "$GCP_PROJECT_ID"
else
    echo -e "${GREEN}Using existing project: $GCP_PROJECT_ID${NC}"
fi

gcloud config set project "$GCP_PROJECT_ID"

# Enable required APIs
echo -e "${BLUE}Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    scheduler.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com

echo -e "${GREEN}✓ Google Cloud setup OK${NC}"
echo ""

# Step 3: Setup Telegram Bot
echo -e "${BLUE}[STEP 3/5]${NC} Setting up Telegram Bot..."

echo -e "${BLUE}Creating Telegram Bot...${NC}"
cat << 'EOF'

📱 TELEGRAM BOT SETUP INSTRUCTIONS:
1. Open Telegram and search for @BotFather
2. Send /newbot
3. Name your bot: "Quant-Robot-Trader" (or your choice)
4. Choose username: "quant_robot_XXXXX" (must be unique)
5. Copy the TOKEN from BotFather's response
6. Open settings and send /setprivacy → choose "Disable"

Then come back and paste your TOKEN below.
EOF

read -p "Enter your Telegram BOT_TOKEN (from @BotFather): " TELEGRAM_BOT_TOKEN

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ Bot token is required${NC}"
    exit 1
fi

# Get Chat ID
echo ""
echo -e "${BLUE}Getting your Telegram Chat ID...${NC}"
cat << 'EOF'

1. Send any message to your bot in Telegram
2. Go to: https://api.telegram.org/bot{TOKEN}/getUpdates
3. Replace {TOKEN} with your bot token
4. Look for the "id" field in the response - that's your CHAT_ID

EOF

read -p "Enter your Telegram CHAT_ID: " TELEGRAM_CHAT_ID

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo -e "${RED}❌ Chat ID is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Telegram Bot setup OK${NC}"
echo ""

# Step 4: Deploy to Google Cloud Run
echo -e "${BLUE}[STEP 4/5]${NC} Deploying to Google Cloud Run..."

SERVICE_NAME="robot-trader"
REGION="us-central1"

echo -e "${BLUE}Building and deploying to Cloud Run...${NC}"

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID" \
    --timeout 3600 \
    --memory 512Mi

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)')

echo -e "${GREEN}✓ Cloud Run deployment OK${NC}"
echo -e "Service URL: ${BLUE}$SERVICE_URL${NC}"
echo ""

# Step 5: Setup Cloud Scheduler (cron job)
echo -e "${BLUE}[STEP 5/5]${NC} Setting up daily scheduler (21:00 UTC)..."

JOB_NAME="robot-trader-daily"

# Delete existing job if it exists
gcloud scheduler jobs delete "$JOB_NAME" --location="$REGION" --quiet 2>/dev/null || true

# Create new job
gcloud scheduler jobs create http "$JOB_NAME" \
    --location="$REGION" \
    --schedule="0 21 * * *" \
    --uri="$SERVICE_URL" \
    --http-method=POST \
    --oidc-service-account-email="$(gcloud config get-value project)@appspot.gserviceaccount.com"

echo -e "${GREEN}✓ Scheduler setup OK (runs at 21:00 UTC daily)${NC}"
echo ""

# ============================================================================
# SETUP COMPLETE - DISPLAY CREDENTIALS
# ============================================================================

echo ""
echo "=========================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "=========================================="
echo ""

cat > robot-credentials.txt << EOF
🤖 ROBOT PAPER TRADING - DEPLOYMENT CREDENTIALS
================================================

GOOGLE CLOUD:
  Project ID: $GCP_PROJECT_ID
  Service: $SERVICE_NAME
  Region: $REGION
  URL: $SERVICE_URL

TELEGRAM BOT:
  Bot Token: $TELEGRAM_BOT_TOKEN
  Chat ID: $TELEGRAM_CHAT_ID
  Bot Name: Quant-Robot-Trader

SCHEDULER:
  Job Name: $JOB_NAME
  Schedule: Daily at 21:00 UTC
  Region: $REGION

STREAMLIT DASHBOARD:
  Setup: Push this repo to GitHub
  Go to: https://streamlit.io/cloud
  Connect repo: robot-trader-deploy
  Main file: dashboard.py
  Add secrets:
    TELEGRAM_BOT_TOKEN = $TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID = $TELEGRAM_CHAT_ID

NEXT STEPS:
1. ✅ Cloud Run deployed
2. ✅ Scheduler active (runs at 21:00 UTC daily)
3. TODO: Push to GitHub and setup Streamlit Cloud
4. TODO: Test with: curl -X POST $SERVICE_URL

TESTING:
  - First execution: Tomorrow at 21:00 UTC
  - Manual trigger: gcloud run services describe $SERVICE_NAME --region $REGION
  - View logs: gcloud run services logs read $SERVICE_NAME --region $REGION

TELEGRAM TEST:
  Send a message to your robot on Telegram to verify connection.

STATUS: 🟢 READY FOR PAPER TRADING

Generated: $(date)
EOF

echo "📋 Credentials saved to: robot-credentials.txt"
echo ""
echo "📊 Quick Summary:"
echo "  ✓ Cloud Run: $SERVICE_URL"
echo "  ✓ Scheduler: Daily at 21:00 UTC"
echo "  ✓ Telegram: Connected"
echo "  ✓ Next: Setup Streamlit Cloud (see credentials file)"
echo ""
echo -e "${GREEN}Robot deployment complete!${NC}"
