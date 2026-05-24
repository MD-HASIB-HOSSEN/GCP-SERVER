#!/bin/bash


set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

clear
echo -e "${CYAN}${BOLD}"
echo "██╗  ██╗ █████╗ ███████╗██╗██████╗ "
echo "███║  ██║██╔══██╗██╔════╝██║██╔══██╗"
echo "███████║███████║███████╗██║██████╔╝"
echo "██╔══██║██╔══██║╚════██║██║██╔══██╗"
echo "██║  ██║██║  ██║███████║██║██████╔╝"
echo "╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═════╝ "
echo -e "${RESET}"
echo -e "${GREEN} AUTO DEPLOY STARTED${RESET}"
echo ""

# =============================
# STEP 1: PROJECT
# =============================

echo -e "${CYAN}[STEP 1] Project Detection${RESET}"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
  echo -e "${RED}[!] No project selected${RESET}"
  read -p "Enter project ID: " PROJECT_ID
  gcloud config set project "$PROJECT_ID"
fi

echo -e "${GREEN}[✓] Project: $PROJECT_ID${RESET}"

# =============================
# STEP 2: API
# =============================

echo ""
echo -e "${CYAN}[STEP 2] API Setup${RESET}"

gcloud auth configure-docker -q

APIS=(
run.googleapis.com
cloudbuild.googleapis.com
artifactregistry.googleapis.com
containerregistry.googleapis.com
compute.googleapis.com
)

for API in "${APIS[@]}"; do
  echo -e "${YELLOW}[*] Enabling $API...${RESET}"
  gcloud services enable "$API" --project="$PROJECT_ID" >/dev/null 2>&1 || true
  echo -e "${GREEN}[✓] $API ready${RESET}"
done

# =============================
# STEP 3: REGION
# =============================

echo ""
echo -e "${CYAN}[STEP 3] Region${RESET}"

if [[ "$PROJECT_ID" == qwiklabs-* ]]; then
  REGION="us-central1"
  echo -e "${GREEN}[✓] Region locked: $REGION${RESET}"
else
  read -p "Region [us-central1]: " REGION
  REGION=${REGION:-us-central1}
fi

# =============================
# STEP 4: SERVICE
# =============================

echo ""
echo -e "${CYAN}[STEP 4] Service Name${RESET}"
read -p "Service name [imran-vip]: " SERVICE_NAME
SERVICE_NAME=${SERVICE_NAME:-imran-vip}

echo -e "${GREEN}[✓] Service: $SERVICE_NAME${RESET}"

# =============================
# STEP 5: CPU
# =============================

echo ""
echo -e "${CYAN}[STEP 5] CPU & RAM${RESET}"

echo "[1] 1 vCPU, 1Gi"
echo "[2] 1 vCPU, 2Gi"
echo "[3] 2 vCPU, 2Gi"
echo "[4] 2 vCPU, 4Gi (recommended)"
echo "[5] 4 vCPU, 8Gi"
echo "[6] 4 vCPU, 16Gi"

read -p "Select [1-6]: " CHOICE
CHOICE=${CHOICE:-4}

case $CHOICE in
  1) CPU=1; MEMORY="1Gi" ;;
  2) CPU=1; MEMORY="2Gi" ;;
  3) CPU=2; MEMORY="2Gi" ;;
  4) CPU=2; MEMORY="4Gi" ;;
  5) CPU=4; MEMORY="8Gi" ;;
  6) CPU=4; MEMORY="16Gi" ;;
  *) CPU=2; MEMORY="4Gi" ;;
esac

echo -e "${GREEN}[✓] CPU: $CPU | RAM: $MEMORY${RESET}"

# =============================
# STEP 6: BUILD
# =============================

echo ""
echo -e "${CYAN}[STEP 6] Building Image${RESET}"

IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

gcloud builds submit --tag "$IMAGE" \
  --project="$PROJECT_ID" \
  --timeout=20m \
  --quiet

echo -e "${GREEN}[✓] Build Done${RESET}"

# =============================
# STEP 7: DEPLOY
# =============================

echo ""
echo -e "${CYAN}[STEP 7] Deploying${RESET}"

gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --cpu "$CPU" \
  --memory "$MEMORY" \
  --timeout 3600 \
  --min-instances 0 \
  --max-instances 1 \
  --project "$PROJECT_ID"

# =============================
# RESULT
# =============================

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --format='value(status.url)')

HOST=$(echo "$SERVICE_URL" | sed 's|https://||')

UUID="HASIBHOSSENTECH"
WS_PATH="/@bouchor"
ENCODED_PATH="%40bouchor"

VLESS="vless://${UUID}@${HOST}:443?encryption=none&security=tls&type=ws&path=${ENCODED_PATH}&host=${HOST}#${SERVICE_NAME}"

echo ""
echo -e "${GREEN}${BOLD}DEPLOY SUCCESSFUL${RESET}"
echo "================================"
echo "Host: $HOST"
echo "UUID: $UUID"
echo "Path: $WS_PATH"
echo "================================"
echo "$VLESS"

# =============================
# DOWNLOAD FILE
# =============================

FILE="/tmp/imran.vless"
echo "$VLESS" > $FILE

echo ""
echo -e "${CYAN}Generating Download Link...${RESET}"

DOWNLOAD_LINK=$(curl --upload-file $FILE https://transfer.sh/imran.vless 2>/dev/null)

echo -e "${GREEN}[✓] Download Ready${RESET}"
echo ""
echo "$DOWNLOAD_LINK"
echo ""