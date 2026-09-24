import sys
import os

# Add workspace root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.server import app

# Vercel Serverless Function entrypoint
