import polars as pl

q = pl.scan_csv("book_export_df2.csv")

df = q.collect()

authors = df.select(pl.col("author")).unique()

authors = authors.with_columns(pl.col("author").str.split("; ").alias("split_author")).explode("split_author")

authors = authors.select(pl.col("split_author").alias("author")).unique().sort(by="author").with_row_index("id")

print(authors.head(10))

authors.write_csv("authors.csv")
