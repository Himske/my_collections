from sqlmodel import SQLModel, Field, Relationship


class BookAuthorLink(SQLModel, table=True):
    __tablename__ = "books_authors"
    book_id: int | None = Field(default=None, foreign_key="books.id", primary_key=True)
    author_id: int | None = Field(default=None, foreign_key="authors.id", primary_key=True)


class Author(SQLModel, table=True):
    __tablename__ = "authors"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    books: list["Book"] = Relationship(link_model=BookAuthorLink, back_populates="authors")


class AuthorWithBooks(SQLModel):
    id: int | None
    name: str
    books: list["Book"]


class AuthorCreate(SQLModel):
    name: str


class AuthorUpdate(SQLModel):
    name: str


class AuthorRead(SQLModel):
    id: int
    name: str


class BookCreate(SQLModel):
    title: str
    sub_title: str
    org_title: str
    org_sub_title: str
    org_publication_year: int
    print_format: str
    pages: int
    publisher: str
    cover: str
    language: str
    language_iso: str
    isbn_13: str
    isbn_10: str
    description: str
    author_ids: list[int] = Field(default_factory=list)


class BookUpdate(SQLModel):
    title: str
    sub_title: str | None
    org_title: str | None
    org_sub_title: str | None
    org_publication_year: int | None
    print_format: str | None
    pages: int | None
    publisher: str | None
    cover: str | None
    language: str | None
    language_iso: str | None
    isbn_13: str | None
    isbn_10: str | None
    description: str | None
    author_ids: list[int] = Field(default_factory=list)


class BookRead(SQLModel):
    id: int
    title: str
    sub_title: str | None
    org_title: str | None
    org_sub_title: str | None
    org_publication_year: int | None
    print_format: str | None
    pages: int | None
    publisher: str | None
    cover: str | None
    language: str | None
    language_iso: str | None
    isbn_13: str | None
    isbn_10: str | None
    description: str | None
    authors: list[AuthorRead]


class BookScrapeResult(SQLModel):
    author: str | None
    title: str | None
    sub_title: str | None
    publisher: str | None
    publication_date: str | None
    language: str | None
    language_iso: str | None
    nof_pages: str | None
    format: str | None
    image_url: str | None
    isbn_13: str | None
    isbn_10: str | None
    description: str | None


class Book(SQLModel, table=True):
    __tablename__ = "books"
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    sub_title: str = Field()
    org_title: str = Field()
    org_sub_title: str = Field()
    org_publication_year: int = Field()
    print_format: str = Field()
    pages: int = Field()
    publisher: str = Field()
    cover: str = Field()
    language: str = Field()
    language_iso: str = Field()
    isbn_13: str = Field()
    isbn_10: str = Field()
    description: str = Field()
    authors: list[Author] = Relationship(link_model=BookAuthorLink, back_populates="books")
