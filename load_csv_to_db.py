import pandas as pd
import sqlite3

conn = sqlite3.connect("database.db")

authors = pd.read_csv("authors.csv")
authors.to_sql("authors", con=conn, index=False, if_exists="replace")

books = pd.read_csv(
    "books.csv",
    dtype={
        "id": int,
        "title": str,
        "sub_title": str,
        "org_title": str,
        "org_sub_title": str,
        "org_publication_year": pd.Int64Dtype(),
        "print_format": str,
        "pages": pd.Int64Dtype(),
        "publisher": str,
        "cover": str,
        "language": str,
        "language_iso": str,
        "isbn_13": str,
        "isbn_10": str,
        "description": str,
    },
)

books = books.drop(["author", "volume", "publication_date"], axis=1)
books.to_sql("books", con=conn, index=False, if_exists="replace")

books_author = pd.read_csv("books_authors.csv")
books_author.to_sql("books_authors", con=conn, index=False, if_exists="replace")
