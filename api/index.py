import sys
import os
from pathlib import Path

# Add workspace root to Python path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.api.server import app

# Top-level ASGI entrypoint exports for Vercel
handler = app
