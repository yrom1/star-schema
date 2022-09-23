from os import environ

from mysql.connector import connect

ENDPOINT = environ["RDS_ENDPOINT"]
USER = environ["RDS_USER"]
PASSWORD = environ["RDS_PASSWORD"]

environ["LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN"] = "1"

conn = connect(
    host=ENDPOINT,
    user=USER,
    passwd=PASSWORD,
    port="3306",
    database="metrics",
)
cur = conn.cursor()
cur.execute("""SELECT now()""")
query_results = cur.fetchall()
print(query_results)
