import sys
import uvicorn
import webbrowser
import threading
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router


def _static_base() -> Path:
    """Returns the base path for bundled static files (handles PyInstaller _MEIPASS)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


STATIC_BASE = _static_base()

app = FastAPI(title="FS25 Farming Dashboard")

app.include_router(router, prefix="/api")

app.mount(
    "/assets",
    StaticFiles(directory=str(STATIC_BASE / "api" / "static" / "assets")),
    name="assets",
)


@app.get("/{full_path:path}")
async def spa(full_path: str):
    return FileResponse(str(STATIC_BASE / "api" / "static" / "index.html"))


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:9988")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    # Pass app object directly — string import doesn't work in PyInstaller bundle
    uvicorn.run(app, host="localhost", port=9988, reload=False)
