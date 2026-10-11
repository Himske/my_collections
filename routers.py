import logging

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from db import SessionDep
from models import (
    Author,
    AuthorCreate,
    AuthorRead,
    AuthorUpdate,
    AuthorWithBooks,
    Book,
    BookCreate,
    BookRead,
    BookUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/authors/", response_model=list[Author])
async def read_authors(session: SessionDep) -> list[Author]:
    logger.info("Reading all authors")
    authors = session.exec(select(Author)).all()
    logger.info("Found %d authors", len(authors))
    return authors


@router.post("/authors/", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(author_data: AuthorCreate, session: SessionDep) -> Author:
    logger.info("Creating author")
    author = Author(name=author_data.name)
    session.add(author)
    session.commit()
    session.refresh(author)
    logger.info("Created author with ID %s", author.id)
    return author


@router.get("/authors/{id}", response_model=AuthorWithBooks)
async def get_author(id: int, session: SessionDep) -> AuthorWithBooks:
    logger.info("Reading author with ID %s", id)
    author = session.exec(select(Author).where(Author.id == id)).one_or_none()
    if not author:
        logger.warning("Author with ID %s was not found", id)
        raise HTTPException(status_code=404, detail="Author not found")
    logger.info("Found author with ID %s", id)
    return author


@router.put("/authors/{id}", response_model=AuthorRead)
async def update_author(id: int, author_data: AuthorUpdate, session: SessionDep) -> Author:
    logger.info("Updating author with ID %s", id)
    author = session.exec(select(Author).where(Author.id == id)).one_or_none()
    if not author:
        logger.warning("Cannot update author with ID %s: not found", id)
        raise HTTPException(status_code=404, detail="Author not found")

    author.name = author_data.name
    session.add(author)
    session.commit()
    session.refresh(author)
    logger.info("Updated author with ID %s", id)
    return author


@router.delete("/authors/{id}")
async def delete_author(id: int, session: SessionDep) -> dict[str, str]:
    logger.info("Deleting author with ID %s", id)
    author = session.exec(select(Author).where(Author.id == id)).one_or_none()
    if author:
        session.delete(author)
        session.commit()
        logger.info("Deleted author with ID %s", id)
        return {"message": f"Author: {author.name} deleted!"}
    else:
        logger.warning("Cannot delete author with ID %s: not found", id)
        return {"message": "Author not found!"}


def _get_authors_by_ids(author_ids: list[int], session: SessionDep) -> list[Author]:
    unique_ids = set(author_ids)
    if not unique_ids:
        return []

    authors = session.exec(select(Author).where(Author.id.in_(unique_ids))).all()
    found_ids = {author.id for author in authors}
    missing_ids = unique_ids - found_ids
    if missing_ids:
        logger.warning("Cannot link book to missing author IDs %s", sorted(missing_ids))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authors not found: {sorted(missing_ids)}",
        )
    return authors


@router.post("/books/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, session: SessionDep) -> Book:
    logger.info("Creating book")
    authors = _get_authors_by_ids(book_data.author_ids, session)
    book = Book.model_validate(book_data.model_dump(exclude={"author_ids"}))
    book.authors = authors
    session.add(book)
    session.commit()
    session.refresh(book)
    logger.info("Created book with ID %s", book.id)
    return book


@router.put("/books/{id}", response_model=BookRead)
async def update_book(id: int, book_data: BookUpdate, session: SessionDep) -> Book:
    logger.info("Updating book with ID %s", id)
    book = session.exec(select(Book).where(Book.id == id)).one_or_none()
    if not book:
        logger.warning("Cannot update book with ID %s: not found", id)
        raise HTTPException(status_code=404, detail="Book not found")

    authors = _get_authors_by_ids(book_data.author_ids, session)
    book.sqlmodel_update(book_data.model_dump(exclude={"author_ids"}))
    book.authors = authors
    session.add(book)
    session.commit()
    session.refresh(book)
    logger.info("Updated book with ID %s", id)
    return book


@router.delete("/books/{id}")
async def delete_book(id: int, session: SessionDep) -> dict[str, str]:
    logger.info("Deleting book with ID %s", id)
    book = session.exec(select(Book).where(Book.id == id)).one_or_none()
    if book:
        session.delete(book)
        session.commit()
        logger.info("Deleted book with ID %s", id)
        return {"message": f"Book: {book.title}, deleted!"}
    else:
        logger.warning("Cannot delete book with ID %s: not found", id)
        return {"message": "Book not found!"}
