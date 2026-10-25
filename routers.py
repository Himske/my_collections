import logging

from fastapi import APIRouter, HTTPException, status
import requests
from sqlmodel import func, select

from book_find import get_book_info
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
    BookScrapeResult,
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


def _parse_isbn(isbn: str) -> str:
    isbn = isbn.replace("-", "").strip()
    if not (len(isbn) == 13 and isbn.isdigit()):
        raise HTTPException(status_code=422, detail="ISBN-13 must be 13 digits")
    return isbn


def _scrape_book(isbn: str, save_image: bool = False) -> dict:
    try:
        info = get_book_info(isbn, save_image=save_image)
    except requests.RequestException:
        logger.exception("Book search failed for ISBN %s", isbn)
        raise HTTPException(status_code=502, detail="Book search service is unavailable")
    if not info["title"]:
        logger.info("No book found for ISBN %s", isbn)
        raise HTTPException(status_code=404, detail="No book found")
    return info


@router.get("/books/search/{isbn}", response_model=BookScrapeResult)
def search_book(isbn: str) -> BookScrapeResult:
    isbn = _parse_isbn(isbn)
    logger.info("Searching for book with ISBN %s", isbn)
    info = _scrape_book(isbn)
    info["isbn_13"] = info.pop("isbn-13")
    info["isbn_10"] = info.pop("isbn-10")
    return BookScrapeResult(**info)


@router.post("/books/import/{isbn}", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def import_book(isbn: str, session: SessionDep) -> Book:
    isbn = _parse_isbn(isbn)
    logger.info("Importing book with ISBN %s", isbn)
    if session.exec(select(Book).where(Book.isbn_13 == isbn)).first():
        logger.warning("Book with ISBN %s already exists", isbn)
        raise HTTPException(status_code=409, detail="Book already exists")

    info = _scrape_book(isbn, save_image=True)

    # The tables have no primary key constraint, so ids must be assigned here
    def next_id(model) -> int:
        return (session.exec(select(func.max(model.id))).one() or 0) + 1

    authors = []
    if info["author"]:
        author = session.exec(select(Author).where(Author.name == info["author"])).first()
        if not author:
            author = Author(id=next_id(Author), name=info["author"])
            session.add(author)
            session.flush()
        authors.append(author)

    pages = (info["nof_pages"] or "").strip()
    year = (info["publication_date"] or "")[:4]
    book = Book(
        id=next_id(Book),
        title=info["title"],
        sub_title=info["sub_title"],
        org_publication_year=int(year) if year.isdigit() else None,
        print_format=info["format"],
        pages=int(pages) if pages.isdigit() else None,
        publisher=info["publisher"],
        cover=info["image_name"] or "placeholder.png",
        language=info["language"],
        language_iso=info["language_iso"],
        isbn_13=isbn,
        isbn_10=(info["isbn-10"] or "").replace("-", "") or None,
        description=info["description"],
        authors=authors,
    )
    session.add(book)
    session.commit()
    session.refresh(book)
    logger.info("Imported book with ID %s", book.id)
    return book


@router.get("/books/{id}", response_model=BookRead)
async def get_book(id: int, session: SessionDep) -> Book:
    logger.info("Reading book with ID %s", id)
    book = session.exec(select(Book).where(Book.id == id)).one_or_none()
    if not book:
        logger.warning("Book with ID %s was not found", id)
        raise HTTPException(status_code=404, detail="Book not found")
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
