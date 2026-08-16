import duckdb


DATABASE_PATH = "data/ecommerce.duckdb"


con = duckdb.connect(DATABASE_PATH)