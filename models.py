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


class Book(SQLModel, table=True):
    __tablename__ = "books"
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    sub_title: str = Field()
    org_title: str = Field()
    org_sub_title: str = Field()
    org_publication_year: str = Field()
    print_format: str = Field()
    pages: str = Field()
    publisher: str = Field()
    cover: str = Field()
    language: str = Field()
    language_iso: str = Field()
    isbn_13: str = Field()
    isbn_10: str = Field()
    description: str = Field()
    authors: list[Author] = Relationship(link_model=BookAuthorLink, back_populates="books")
