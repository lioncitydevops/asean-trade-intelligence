#!/usr/bin/env bash
# Automated Google Cloud Run Deployment Script (Bash)
set -e

PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION=${2:-"us-central1"}
SERVICE_NAME=${3:-"oil-tanker-traffic"}

if [ -z "$PROJECT_ID" ]; then
    echo "[ERROR] Google Cloud Project ID is not configured."
    echo "Usage: ./deploy_cloud_run.sh [PROJECT_ID] [REGION] [SERVICE_NAME]"
    exit 1
fi

echo "================================================================="
echo " MARITIME OIL FLOW INTELLIGENCE - CLOUD RUN DEPLOYER"
echo "================================================================="
echo "[*] Deploying to Project: $PROJECT_ID | Region: $REGION | Service: $SERVICE_NAME"

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --port 8000 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300

echo "[OK] Deployment complete! Live service ready on Google Cloud Run."
