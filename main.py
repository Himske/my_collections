import logging
import os
import uvicorn
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import router

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler(
            os.path.join(LOG_DIR, "app.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
    ],
)

app = FastAPI()
app.include_router(router)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.get("/book", include_in_schema=False)
async def book_page() -> FileResponse:
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "book.html"))


@app.get("/find", include_in_schema=False)
async def find_page() -> FileResponse:
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "find.html"))


if __name__ == "__main__":
    uvicorn.run(app)
