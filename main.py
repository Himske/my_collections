from fastapi import FastAPI
from sqlmodel import select

from db import SessionDep
from models import Author, AuthorWithBooks

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/authors/", response_model=list[Author])
async def read_authors(session: SessionDep) -> list[Author]:
    authors = session.exec(select(Author)).all()
    return authors


@app.get("/authors/{id}", response_model=AuthorWithBooks)
async def get_author(id: int, session: SessionDep) -> AuthorWithBooks:
    author = session.exec(select(Author).where(Author.id == id)).one()
    return author
