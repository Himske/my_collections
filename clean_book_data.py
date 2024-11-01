import polars as pl

books = pl.scan_csv("book_export_df2.csv").collect().with_row_index("id")

books_authors = (
    books.select(pl.col("id"), pl.col("author"))
    .with_columns(pl.col("author").str.split("; ").alias("split_author"))
    .explode("split_author")
).select(pl.col("id").alias("book_id"), pl.col("split_author").alias("author"))

authors = books_authors.select(pl.col("author")).unique().sort(by="author").with_row_index("id")

books_authors = books_authors.join(authors, on="author", how="inner").select(
    pl.col("book_id"), pl.col("id").alias("author_id")
)

print(books.head(5))
print(authors.head(10))
print(books_authors.head(5))

books.write_csv("books.csv")
authors.write_csv("authors.csv")
books_authors.write_csv("books_authors.csv")
