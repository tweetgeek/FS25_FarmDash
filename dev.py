"""
Development server with hot-reload.

Usage:
    python dev.py                  # API on http://localhost:9988
    cd app && npm run dev          # Vue HMR on http://localhost:5173 (proxies /api → 9988)
"""
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api.routes import router

app = FastAPI(title="FarmDash [dev]")
app.include_router(router, prefix="/api")


@app.get("/{full_path:path}")
def dev_frontend(full_path: str):
    """In dev mode the frontend is served by Vite on :5173."""
    return RedirectResponse("http://localhost:5173/" + full_path)

if __name__ == "__main__":
    uvicorn.run(
        "dev:app",
        host="0.0.0.0",
        port=9988,
        reload=True,
        reload_dirs=["api"],  # watch only api/ — parsers, routes, config
    )
