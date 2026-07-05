"""Bridge file so Vercel can import the FastAPI app from studymate/server/.
Python module paths cannot contain hyphens, so this file lives at repo root and
re-exports the FastAPI app from the server directory.
"""
import os
import sys

# Make server/ modules importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "studymate", "server"))

from main import app  # noqa: E402
