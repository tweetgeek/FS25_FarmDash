import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn
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


def _create_tray_image():
    from PIL import Image
    return Image.open(STATIC_BASE / "icon.png")


def _open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:9988")


def _get_local_ip() -> str:
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    PORT = 9988
    local_url = f"http://{_get_local_ip()}:{PORT}"

    log_config = None if getattr(sys, "frozen", False) else uvicorn.config.LOGGING_CONFIG

    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, reload=False, log_config=log_config)
    server = uvicorn.Server(config)

    threading.Thread(target=server.run, daemon=True).start()
    threading.Thread(target=_open_browser, daemon=True).start()

    import pystray
    import subprocess

    def on_open(icon, item):
        webbrowser.open("http://localhost:9988")

    def on_copy_address(icon, item):
        subprocess.run(["clip"], input=local_url.encode(), check=False)

    def on_quit(icon, item):
        server.should_exit = True
        icon.stop()

    tray = pystray.Icon(
        "FarmDash",
        _create_tray_image(),
        "FarmDash — FS25 Dashboard",
        menu=pystray.Menu(
            pystray.MenuItem("Open FarmDash", on_open, default=True),
            pystray.MenuItem(f"Copy network address  ({local_url})", on_copy_address),
            pystray.MenuItem("Quit", on_quit),
        ),
    )
    tray.run()
