"""StudyMate Learning Planet - FastAPI Backend Server."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from database import init_db
from routes import auth, plans, tasks, cards, mistakes, farm, ai, upload, focus, subjects


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="StudyMate 学习星球 API",
    description="AI抗遗忘备考工具后端服务",
    version="1.0.3",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False if CORS_ORIGINS == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle OPTIONS preflight explicitly (needed for Vercel Python serverless)
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "ok"}

# Register routers
app.include_router(auth.router)
app.include_router(plans.router)
app.include_router(tasks.router)
app.include_router(cards.router)
app.include_router(mistakes.router)
app.include_router(farm.router)
app.include_router(ai.router)
app.include_router(upload.router)
app.include_router(focus.router)
app.include_router(subjects.router)


@app.get("/")
def root():
    return {
        "name": "StudyMate 学习星球 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    from config import PORT, RELOAD
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=RELOAD)