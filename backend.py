"""Bridge file so Vercel can import the FastAPI app from studymate/server/."""
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "studymate", "server"))

try:
    from main import app  # noqa: E402
except Exception:
    traceback.print_exc()
    # Re-raise so Vercel reports the error
    raise
