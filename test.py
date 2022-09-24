from stardb import StarSchema

with StarSchema() as db:
    db.insert_dimension("dimension_jira", [0])
