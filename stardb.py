from datetime import datetime
from os import environ
from textwrap import dedent
from zoneinfo import ZoneInfo

from mysql.connector import connect
from mysql.connector.connection import MySQLConnection

_DEBUG = False


def _print(*args, **kwargs):
    if _DEBUG:
        print(*args, **kwargs)


class StarSchemaError(Exception):
    pass


class StarSchema:
    def __init__(self) -> None:
        ENDPOINT = environ["RDS_ENDPOINT"]
        USER = environ["RDS_USER"]
        PASSWORD = environ["RDS_PASSWORD"]
        environ["LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN"] = "1"
        self.conn = connect(
            host=ENDPOINT,
            user=USER,
            passwd=PASSWORD,
            port="3306",
            database="metrics",
        )

    def __enter__(self) -> MySQLConnection:
        return self.conn

    def _close(self) -> None:
        self.conn.close()

    def __exit__(self) -> None:
        self._close()

    def query(self, query: str, data):  # TODO return type
        cur = self.conn.cursor()
        cur.execute(query, data)
        ans = cur.fetchall()
        cur.close()
        if len(ans) == 1:
            ans = ans[0]
        _print(ans)
        return ans

    def _insert_auto_increment(self, query: str, data) -> int:
        """Insert into dimension table.
        Args:
            Upsert query.
        Returns:
            The AUTO_INCREMENT id generated for the dimension table row.
        """

        cur = self.conn.cursor()
        cur.execute(query, data)
        ans = cur.lastrowid
        cur.close()
        assert ans is not None
        return ans

    @staticmethod
    def _today():
        return datetime.now(ZoneInfo("US/Eastern")).strftime("%Y-%m-%d")

    def _upsert_fact_foreign_key(self, data: list[int | None]) -> None:
        """Insert id's of dimension foreign keys into fact table."""
        today = self._today()
        ...

    def _get_current_id_for_dimension(self, dimension: str) -> int:
        today = self._today()
        return self.query(
            f"""
        SELECT id_{dimension}
        FROM fact_tabe
        WHERE date = %s
        """,
            (today),
        )

    def insert_dimension(self, dimension: str, data) -> None:
        """Insert data into dimension table. The class manages insertions/updates
        of fact_table foreign keys.
        Args:
            dimension: name of the dimension, for 'dimension_jira' use 'jira'.
            data: Data to insert into dimension. NOTE Don't put None for the id
            field, just give the data you want to insert into the dimension.
        """

        for x in data:
            assert x is not None

        match dimension:
            case "dimension_jira":
                assert len(data) == 1
                id_jira = self._get_current_id_for_dimension("jira")
                foreign_key_jira = self._insert_auto_increment(
                    f"""
                INSERT INTO dimension_jira (id, issues_done)
                VALUES (%(id)s, %(issues_done)s)
                ON DUPLICATE KEY UPDATE issues_done = %(issues_done)s
                """,
                    {"id": id_jira, "issues_done": id[0]},
                )
            case "dimension_leetcode":
                assert len(data) == 4
                id = self._insert_auto_increment(
                    f"""
                INSERT INTO dimension_leetcode (id, python3_problems, mysql_problems, rank_, streak)
                VALUES (%s, %s, %s, %s, %s)
                """,
                    (),
                )
            case "dimension_strava":
                assert len(data) == 1
                id = self._insert_auto_increment(
                    f"""
                INSERT INTO dimension_strava (id, distance_km)
                VALUES (%s, %s)
                """,
                    (),
                )
            case _:
                raise StarSchemaError(
                    dedent(
                        f"""Dimension table name `{dimension}` not found. \
                    Did you forget to implement the upsert logic for this dimension?"""
                    )
                )
