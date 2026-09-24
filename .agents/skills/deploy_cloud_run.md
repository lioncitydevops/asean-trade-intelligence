# Skill: Deploy to Cloud Run

## Objective
Your goal as DevOps (@devops) is to package the Maritime Oil Flow platform into a container and deploy it to Google Cloud Run or serverless environments.

## Instructions
1. **Container Verification**: Inspect `Dockerfile` and ensure all assets (exhibits, fonts, static web assets) are included.
2. **Build & Deploy**:
   ```bash
   gcloud run deploy oil-tanker-traffic --source . --region us-central1 --allow-unauthenticated
   ```
3. **Configure Environment Variables**: Ensure `GEMINI_API_KEY`, `PROJECT_ID`, and BigQuery credentials are set if using cloud resources.
4. **Report**: Output the live production Cloud Run URL and health check status.
