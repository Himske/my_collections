from fastapi import FastAPI
from sqlmodel import select

from db import SessionDep
from models import Author

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/authors/", response_model=list[Author])
async def read_authors(session: SessionDep) -> list[Author]:
    authors = session.exec(select(Author)).all()
    return authors


@app.get("/authors/{id}", response_model=Author)
async def get_author(id: int, session: SessionDep):
    author = session.exec(select(Author).where(Author.id == id)).one()
    for book in author.books:
        print(book)
    return author
