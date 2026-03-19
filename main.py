import logging
import logging.handlers
import sys
import threading
import time
import traceback as tb
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from api.routes import router
from api import VERSION
from api.config import read_config, write_config


# ── Logging setup ─────────────────────────────────────────────────────────────

def _log_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def _setup_logging() -> Path:
    log_path = _log_dir() / "farmdash.log"
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=2_000_000, backupCount=2, encoding="utf-8"
    )
    fh.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(fh)

    # In dev mode also log to stdout
    if not getattr(sys, "frozen", False):
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        root.addHandler(sh)

    # Let uvicorn logs flow through root (we manage log_config=None below)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = []
        lg.propagate = True

    logging.getLogger("farmdash").info("FarmDash v%s start. Log: %s", VERSION, log_path)
    return log_path


LOG_PATH = _setup_logging()
logger = logging.getLogger("farmdash")


def _static_base() -> Path:
    """Returns the base path for bundled static files (handles PyInstaller _MEIPASS)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


STATIC_BASE = _static_base()

app = FastAPI(title="FS25 Farming Dashboard")

app.include_router(router, prefix="/api")


@app.middleware("http")
async def _log_errors(request: Request, call_next):
    try:
        response = await call_next(request)
        if response.status_code >= 500:
            logger.error("HTTP 500  %s  %s", request.method, request.url.path)
        return response
    except Exception:
        logger.error("EXCEPTION  %s  %s\n%s", request.method, request.url.path, tb.format_exc())
        return JSONResponse(
            {"detail": f"Błąd serwera — szczegóły w farmdash.log"},
            status_code=500,
        )

_assets_dir = STATIC_BASE / "api" / "static" / "assets"
if _assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")


@app.get("/{full_path:path}")
async def spa(full_path: str):
    index = STATIC_BASE / "api" / "static" / "index.html"
    if not index.exists():
        return HTMLResponse(
            "<h2>Frontend not built</h2><p>Run: <code>cd app &amp;&amp; npm run build</code></p>",
            status_code=503,
        )
    return FileResponse(str(index))


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


def _ensure_single_instance():
    """Prevent multiple instances on Windows using a named mutex."""
    if sys.platform != "win32":
        return None
    import ctypes
    mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "Global\\FarmDash_SingleInstance_v1")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(
            0,
            "FarmDash jest już uruchomiony.\nSprawdź pasek systemowy (prawy dolny róg ekranu).",
            "FarmDash — już działa",
            0x40,  # MB_ICONINFORMATION
        )
        sys.exit(0)
    return mutex  # keep reference alive for process lifetime


if __name__ == "__main__":
    _mutex = _ensure_single_instance()
    PORT = 9988
    local_url = f"http://{_get_local_ip()}:{PORT}"

    def _make_server():
        cfg = uvicorn.Config(app, host="0.0.0.0", port=PORT, reload=False, log_config=None)
        return uvicorn.Server(cfg)

    server_holder = [_make_server()]
    threading.Thread(target=server_holder[0].run, daemon=True).start()
    if read_config().get("open_browser_on_start", False):
        threading.Thread(target=_open_browser, daemon=True).start()

    import pystray
    import subprocess

    def on_open(icon, item):
        webbrowser.open("http://localhost:9988")

    def on_copy_address(icon, item):
        subprocess.run(["clip"], input=local_url.encode(), check=False)

    def on_restart(icon, item):
        server_holder[0].should_exit = True
        time.sleep(2)
        server_holder[0] = _make_server()
        threading.Thread(target=server_holder[0].run, daemon=True).start()
        if read_config().get("open_browser_on_start", False):
            threading.Thread(target=_open_browser, daemon=True).start()

    def on_toggle_browser(icon, item):
        cfg = read_config()
        cfg["open_browser_on_start"] = not cfg.get("open_browser_on_start", False)
        write_config(cfg)

    def on_open_log(icon, item):
        import os
        if LOG_PATH.exists():
            os.startfile(str(LOG_PATH))

    def on_quit(icon, item):
        server_holder[0].should_exit = True
        icon.stop()

    tray = pystray.Icon(
        "FarmDash",
        _create_tray_image(),
        f"FarmDash v{VERSION} — FS25 Dashboard",
        menu=pystray.Menu(
            pystray.MenuItem("Open FarmDash", on_open, default=True),
            pystray.MenuItem(f"Copy network address  ({local_url})", on_copy_address),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"FarmDash v{VERSION}", None, enabled=False),
            pystray.MenuItem("Open browser on start", on_toggle_browser,
                             checked=lambda item: read_config().get("open_browser_on_start", False)),
            pystray.MenuItem("Restart server", on_restart),
            pystray.MenuItem("Open log file", on_open_log),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_quit),
        ),
    )
    tray.run()
