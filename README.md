# My Collections

A FastAPI application for managing a book collection and its authors. It stores
books, authors, and their many-to-many relationships in a SQLite database.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup and run

Install the project dependencies:

```bash
uv sync
```

Create the SQLite database and tables if they do not already exist:

```bash
uv run python db.py
```

Start the API from the project directory:

```bash
uv run uvicorn main:app --reload
```

The database is `database.db` in the project directory. Application log
messages are written to `logs/app.log` beside `main.py`, rotating at 5 MB
with 3 backup files kept.

## Web interface

Open the application at `/` to browse authors and expand an author to see
their books. Select a book to open its details page. Use **Find a book by
ISBN** to search for a book by ISBN-13; search results can be previewed and
added to the collection.

The application looks up book details on Nicebooks, so finding or importing
a book requires an internet connection. Adding a book also creates its author
if they are not already in the collection and saves available cover images.

## Static files

Files in `static/` are served under `/static/`. The directory contains the
author list (`index.html` and `index.js`), book details (`book.html` and
`book.js`), ISBN finder (`find.html` and `find.js`), and shared `styles.css`.
Book cover images are stored in `static/book_covers/` and are available under
`/static/book_covers/`; imported covers include thumbnail and large versions.

## API

Interactive API documentation is available at `/docs` (Swagger UI) and
`/redoc` while the application is running.

All routes are relative to the server root. IDs in paths are integers.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/authors/` | List authors |
| `POST` | `/authors/` | Create an author |
| `GET` | `/authors/{id}` | Get an author and their books |
| `PUT` | `/authors/{id}` | Replace an author's name |
| `DELETE` | `/authors/{id}` | Delete an author |
| `GET` | `/books/search/{isbn}` | Find book details by ISBN-13 |
| `POST` | `/books/import/{isbn}` | Find and add a book by ISBN-13 |
| `POST` | `/books/` | Create a book and optionally associate authors |
| `GET` | `/books/{id}` | Get a book and its authors |
| `PUT` | `/books/{id}` | Replace a book's details and author associations |
| `DELETE` | `/books/{id}` | Delete a book |

The ISBN endpoints accept 13 digits, with optional hyphens. Search returns
book details without saving them. Import adds the book to the database,
associates its author when available, and saves its cover images. Import
returns `409 Conflict` if a book with that ISBN-13 is already in the
collection; an ISBN that cannot be found returns `404 Not Found`.

### Create an author

`POST /authors/`

```json
{
  "name": "Ursula K. Le Guin"
}
```

### Update an author

`PUT /authors/{id}`

```json
{
  "name": "Ursula K. Le Guin"
}
```

### Create or update a book

`POST /books/` creates a book; `PUT /books/{id}` replaces all its details.
Every book field below is required except `author_ids`, which defaults to an
empty list. Use existing author IDs to associate authors with the book.

```json
{
  "title": "A Wizard of Earthsea",
  "sub_title": "",
  "org_title": "A Wizard of Earthsea",
  "org_sub_title": "",
  "org_publication_year": 1968,
  "print_format": "Paperback",
  "pages": 205,
  "publisher": "Parnassus Press",
  "cover": "",
  "language": "English",
  "language_iso": "en",
  "isbn_13": "9780547773742",
  "isbn_10": "0547773749",
  "description": "A fantasy novel.",
  "author_ids": [1]
}
```

Create requests return `201 Created`; successful updates return `200 OK`.
Looking up or updating an author or book that does not exist returns `404`.
Referencing a missing author ID when creating or updating a book also returns
`404`. Delete endpoints return a message if the item was deleted or not found.
