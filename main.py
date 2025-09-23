import uvicorn

from fastapi import FastAPI
from sqlmodel import select

from db import SessionDep
from models import Author, AuthorWithBooks, Book

app = FastAPI()


@app.get("/authors/", response_model=list[Author])
async def read_authors(session: SessionDep) -> list[Author]:
    authors = session.exec(select(Author)).all()
    return authors


@app.get("/authors/{id}", response_model=AuthorWithBooks)
async def get_author(id: int, session: SessionDep) -> AuthorWithBooks:
    author = session.exec(select(Author).where(Author.id == id)).one()
    return author


@app.delete("/authors/{id}")
async def delete_author(id: int, session: SessionDep) -> dict[str, str]:
    author = session.exec(select(Author).where(Author.id == id)).one_or_none()
    if author:
        session.delete(author)
        session.commit()
        return {"message": f"Author: {author.name} deleted!"}
    else:
        return {"message": "Author not found!"}


@app.delete("/books/{id}")
async def delete_book(id: int, session: SessionDep) -> dict[str, str]:
    book = session.exec(select(Book).where(Book.id == id)).one_or_none()
    if book:
        session.delete(book)
        session.commit()
        return {"message": f"Book: {book.title}, deleted!"}
    else:
        return {"message": "Book not found!"}


if __name__ == "__main__":
    uvicorn.run(app)
