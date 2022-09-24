with open("./schema.sql", "r") as f:
    content = f.read()

queries = content.split(";")[1:-2]  # NOTE im skipping the transaction stuff in the file

from stardb import StarSchema

with StarSchema() as db:
    for query in queries:
        print(query)
        db.query(query)
