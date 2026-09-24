# Maritime Oil Flow Intelligence Platform: Hybrid Deployment Playbook

This guide walks you through deploying the **Maritime Oil Flow Intelligence & Real-Time Macro Insights Platform** using **Option 2 (Hybrid Architecture)**:
* **Frontend Web Dashboard** on **Vercel** (Global Edge CDN, SSL, high availability).
* **Backend API & PDF Engine** on a **Container Host** (**Google Cloud Run**, **Render**, or **Railway**) using Docker for complete OS font libraries and unconstrained data computation.

---

## Architecture Flow

```
┌─────────────────────────────────────────┐
│          USER BROWSER                   │
│   https://maritime-intelligence.vercel.app│
└───────────────────┬─────────────────────┘
                    │ (Static Assets & Leaflet/Chart UI)
                    ▼
┌─────────────────────────────────────────┐
│          VERCEL EDGE CDN                │
│    Hosts /src/web (HTML, CSS, JS)       │
│    Rewrites /api/* ───┐                 │
└───────────────────────┼─────────────────┘
                        │ HTTPS Proxy / CORS
                        ▼
┌─────────────────────────────────────────┐
│        BACKEND CONTAINER HOST           │
│   (Google Cloud Run / Render / Railway) │
│                                         │
│   • FastAPI REST Endpoints              │
│   • AIS Telemetry & Dark Fleet Tracker  │
│   • Matplotlib High-Res Chart Engine    │
│   • ReportLab 6-Page PDF Newsletter     │
└─────────────────────────────────────────┘
```

---

## Step 1: Deploy the Backend Container

Choose **one** of the following options to deploy the containerized backend:

### Option A: Google Cloud Run (Recommended for Production & GCP)
Using the existing [`Dockerfile`](../Dockerfile) and [`deploy/terraform/main.tf`](./terraform/main.tf):

```bash
# 1. Build container with Google Cloud Build
gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/maritime-terminal:latest

# 2. Deploy to Cloud Run
gcloud run deploy maritime-backend \
  --image gcr.io/YOUR_GCP_PROJECT_ID/maritime-terminal:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8000
```
*Take note of the deployed URL (e.g., `https://maritime-backend-xyz.a.run.app`).*

---

### Option B: Render (Easiest 1-Click Container Host)
1. Push this repository to GitHub or GitLab.
2. Go to [dashboard.render.com](https://dashboard.render.com/) -> **New** -> **Web Service**.
3. Select your repository.
4. Render will automatically detect [`render.yaml`](../render.yaml) or select **Docker** environment.
5. Set Health Check Path to `/api/health`.
6. Click **Create Web Service**.
*Take note of the deployed URL (e.g., `https://maritime-backend.onrender.com`).*

---

### Option C: Railway / Fly.io
1. Go to [railway.app](https://railway.app/) -> **New Project** -> **Deploy from GitHub repo**.
2. Railway will automatically build and deploy the [`Dockerfile`](../Dockerfile).
3. Under service settings, click **Generate Domain**.
*Take note of your deployed URL.*

---

## Step 2: Deploy the Frontend to Vercel

### Method 1: Using Vercel CLI
```bash
# 1. Install Vercel CLI (if not installed)
npm i -g vercel

# 2. Log in and deploy from project root
vercel

# 3. For production deployment
vercel --prod
```

### Method 2: Via Vercel Web Dashboard (GitHub Integration)
1. Push your code to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) and import your repository.
3. Keep default settings (Root Directory `./`, Framework Preset: `Other`).
4. Click **Deploy**.

---

## Step 3: Link Vercel Frontend to Your Backend Container

You have **three seamless ways** to connect the frontend to the backend:

### Method A: Update `vercel.json` (Recommended for Zero-CORS Same-Origin Proxy)
Open [`vercel.json`](../vercel.json) and replace `YOUR_BACKEND_CONTAINER_URL` with your container URL:
```json
{
  "src": "/api/(.*)",
  "dest": "https://maritime-backend.onrender.com/api/$1"
}
```
Redeploy or push to git. Vercel will automatically route all `/api/*` calls from the frontend to your backend.

---

### Method B: URL Parameter (Instant Testing without Redeployment)
You can point your Vercel deployment to any backend instantly by adding `?api=...` to your URL:
```
https://maritime-intelligence.vercel.app/?api=https://maritime-backend.onrender.com
```
*The app will save this URL in `localStorage` for all subsequent sessions!*

---

### Method C: Global Window Configuration
In `src/web/index.html`, you can inject:
```html
<script>
  window.MARITIME_API_BASE = "https://maritime-backend.onrender.com";
</script>
```

---

## Step 4: Verification & Smoke Testing

1. Open your Vercel frontend URL in the browser:
   - Check that the header market ticker updates (`BRENT PROMPT: $104.50`, `DEC HORIZON: $101.20`).
   - Check that the Leaflet Dark Map shows moving oil tankers in Hormuz and Fujairah.
   - Click the **Exhibit 1**, **Exhibit 2**, and **Exhibit 3** tabs to verify interactive Chart.js line charts.
2. Test PDF Report Generation:
   - Click **Generate Real-Time Newsletter (PDF)** in the header.
   - Click **Run AI Narrative & Compile PDF**.
   - Click **Download PDF** and open the generated 6-page institutional report.
