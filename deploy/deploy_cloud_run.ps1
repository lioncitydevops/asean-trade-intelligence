# Automated Google Cloud Run Deployment Script (PowerShell)
param (
    [string]$ProjectID = "",
    [string]$Region = "us-central1",
    [string]$ServiceName = "oil-tanker-traffic"
)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " MARITIME OIL FLOW INTELLIGENCE - CLOUD RUN DEPLOYER" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

if (-not $ProjectID) {
    $ProjectID = gcloud config get-value project 2>$null
}

if (-not $ProjectID) {
    Write-Error "Google Cloud Project ID is not configured. Run 'gcloud config set project <PROJECT_ID>' or pass -ProjectID <ID>."
    exit 1
}

Write-Host "[*] Deploying to Project: $ProjectID | Region: $Region | Service: $ServiceName" -ForegroundColor Yellow

gcloud run deploy $ServiceName `
    --source . `
    --project $ProjectID `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --port 8000 `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Deployment complete! Live service ready on Google Cloud Run." -ForegroundColor Green
} else {
    Write-Host "[ERROR] Cloud Run deployment failed." -ForegroundColor Red
}
