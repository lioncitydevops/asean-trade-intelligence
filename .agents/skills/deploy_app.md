# Skill: Deploy App

## Objective
Your goal as DevOps (@devops) is to configure dependencies, start local development and production servers, and report live interactive links.

## Instructions
1. **Environment Verification**: Inspect `requirements.txt` and python environment.
2. **Dependency Installation**: If new packages were introduced, install them via `pip install -r requirements.txt`.
3. **Launch Service**: Start the platform locally using `python main.py --serve` or `uvicorn src.api.server:app --port 8000`.
4. **Health Check**: Validate that `http://127.0.0.1:8000` is healthy and responsive.
5. **Report**: Provide clickable localhost links and endpoint summaries to the user.
