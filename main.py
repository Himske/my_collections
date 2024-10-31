from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Author(BaseModel):
    name: str


class Book(BaseModel):
    title: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/authors/", response_model=list[Author])
async def read_authors() -> list[Author]:
    return [{"name": "Isaac Asimov"}, {"name": "Arthur C Clarke"}]
