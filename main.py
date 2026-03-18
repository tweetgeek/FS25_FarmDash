import uvicorn
import webbrowser
import threading
import time
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router

app = FastAPI(title="FS25 Farming Dashboard")

app.include_router(router, prefix="/api")

app.mount("/assets", StaticFiles(directory="api/static/assets"), name="assets")


@app.get("/{full_path:path}")
async def spa(full_path: str):
    return FileResponse("api/static/index.html")


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:9988")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("main:app", host="localhost", port=9988, reload=False)
