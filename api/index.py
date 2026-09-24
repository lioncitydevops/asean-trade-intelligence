import sys
import os
import traceback

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from src.api.server import app
    handler = app
except Exception as e:
    err_msg = str(e)
    err_tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        return JSONResponse(status_code=500, content={"error": err_msg, "traceback": err_tb})
    handler = app


