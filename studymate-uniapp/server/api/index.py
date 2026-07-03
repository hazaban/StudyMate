"""Vercel Serverless Function entrypoint for StudyMate API.

This file wraps the FastAPI app with Mangum so it can run on Vercel's
Python serverless runtime. All FastAPI logic stays in main.py.
"""

import os
import sys

# Make sure the server root is on the import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from main import app  # noqa: E402

# Mangum adapter for AWS Lambda / Vercel serverless
handler = Mangum(app, lifespan="off")
