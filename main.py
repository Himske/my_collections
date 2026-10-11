import logging
import os
import uvicorn

from fastapi import FastAPI

from routers import router

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "app.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    encoding="utf-8",
)

app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app)
