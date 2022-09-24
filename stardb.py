from datetime import datetime
from functools import wraps
from os import environ
from textwrap import dedent
from typing import Callable
from zoneinfo import ZoneInfo

from mysql.connector import connect
from mysql.connector.connection import MySQLConnection

_DEBUG = False


def _print(*args, **kwargs):
    if _DEBUG:
        print(*args, **kwargs)


def _debug_func(func) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        _print("QUALNAME", func.__qualname__)
        _print(args, kwargs)
        ans = func(*args, **kwargs)
        _print("OUTPUT", ans)
        return ans

    return wrapper


def _debug(cls) -> type:
    for key, value in vars(cls).items():
        if callable(value):
            setattr(cls, key, _debug_func(value))
            continue
    return cls


class StarSchemaError(Exception):
    pass


@_debug
class StarSchema:
    def __init__(self) -> None:
        self._today = datetime.now(ZoneInfo("US/Eastern"))
        if _DEBUG:
            self.conn = connect(
                host="localhost",
                user="root",
                passwd="root",
                port="3306",
                database="metrics",
            )
        else:
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
        return self

    def _close(self):
        self.conn.commit()
        self.conn.close()

    def __exit__(self, *_, **__) -> None:
        self._close()

    def query(self, query: str, data=tuple()):  # TODO return type
        """Query star schema.

        Args:
            Query and data for paramaterization.

        Returns:
            List of rows, or unwrapped list if only one row.
        """
        cur = self.conn.cursor()
        cur.execute(query, data)
        ans = cur.fetchall()
        cur.close()
        return ans

    def _insert(self, query: str, data) -> None:
        cur = self.conn.cursor()
        cur.execute(query, data)
        cur.close()

    def _get_current_id_for_dimension(self, dimension: str) -> int:
        try:
            ans = self.query(
                f"""
            SELECT id_{dimension}
            FROM fact_table
            WHERE date = %s
            """,
                (self._today.strftime("%Y-%m-%d"),),
            )
            return ans[0][0]
        except:
            return None

    def insert_dimension(self, dimension: str, data) -> None:
        """Insert data into dimension table.

        The class manages insertions/updates of fact_table foreign keys.

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
                fact_id = self._get_current_id_for_dimension("jira")
                self._insert(
                    f"""
                INSERT INTO dimension_jira (id, issues_done)
                VALUES (%(id)s, %(issues_done)s)
                ON DUPLICATE KEY UPDATE issues_done = %(issues_done)s
                """,
                    {"id": fact_id, "issues_done": data[0]},
                )
                dimension_id = self.query("SELECT MAX(id) FROM dimension_jira")[0][0]
                if fact_id != dimension_id:
                    self._insert(
                        """
                    INSERT INTO fact_table (date, id_jira, id_leetcode, id_strava)
                    VALUES (%(date)s, %(id_jira)s, NULL, NULL)
                    ON DUPLICATE KEY UPDATE id_jira = %(id_jira)s
                    """,
                        {"date": self._today, "id_jira": dimension_id},
                    )
            case "dimension_leetcode":
                assert len(data) == 4
                fact_id = self._get_current_id_for_dimension("leetcode")
                self._insert(
                    f"""
                INSERT INTO dimension_leetcode (id, python3_problems, mysql_problems, rank_, streak)
                VALUES (%(id)s, %(python3_problems)s, %(mysql_problems)s, %(rank_)s, %(streak)s)
                ON DUPLICATE KEY UPDATE
                    python3_problems = %(python3_problems)s
                    , mysql_problems = %(mysql_problems)s
                    , rank_ = %(rank_)s
                    , streak = %(streak)s
                """,
                    {
                        "id": fact_id,
                        "python3_problems": data[0],
                        "mysql_problems": data[1],
                        "rank_": data[2],
                        "streak": data[3],
                    },
                )
                dimension_id = self.query("SELECT MAX(id) FROM dimension_leetcode")[0][
                    0
                ]
                if fact_id != dimension_id:
                    self._insert(
                        """
                    INSERT INTO fact_table (date, id_jira, id_leetcode, id_strava)
                    VALUES (%(date)s, NULL, %(id_leetcode)s, NULL)
                    ON DUPLICATE KEY UPDATE id_leetcode = %(id_leetcode)s
                    """,
                        {"date": self._today, "id_leetcode": dimension_id},
                    )
            case "dimension_strava":
                assert len(data) == 1
                fact_id = self._get_current_id_for_dimension("strava")
                self._insert(
                    f"""
                INSERT INTO dimension_strava (id, distance_km)
                VALUES (%(id)s, %(distance_km)s)
                ON DUPLICATE KEY UPDATE distance_km = %(distance_km)s
                """,
                    {"id": fact_id, "distance_km": data[0]},
                )
                dimension_id = self.query("SELECT MAX(id) FROM dimension_jira")[0][0]
                if fact_id != dimension_id:
                    self._insert(
                        """
                    INSERT INTO fact_table (date, id_jira, id_leetcode, id_strava)
                    VALUES (%(date)s, NULL, NULL, %(id_strava)s)
                    ON DUPLICATE KEY UPDATE id_strava = %(id_strava)s
                    """,
                        {"date": self._today, "id_strava": dimension_id},
                    )
            case _:
                raise StarSchemaError(
                    dedent(
                        f"""Dimension table name `{dimension}` not found. \
                    Did you forget to implement the upsert logic for this dimension?"""
                    )
                )


if __name__ == "__main__":
    if _DEBUG:
        with StarSchema() as db:
            db.insert_dimension("dimension_jira", [0])
            db.insert_dimension("dimension_leetcode", [5, 0, 95000, 11])
            db.insert_dimension("dimension_strava", [4.13])
            db.insert_dimension(
                "dimension_leetcode", [x + 1 for x in [5, 0, 95000, 11]]
            )
