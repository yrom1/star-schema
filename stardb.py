from datetime import datetime
from functools import wraps
from os import environ
from textwrap import dedent
from typing import Callable
from zoneinfo import ZoneInfo

from mysql.connector import connect
from mysql.connector.connection import MySQLConnection

_DEBUG = True


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
        if len(ans) == 1:
            ans = ans[0]
        _print(ans)
        return ans

    def _insert(self, query: str, data) -> None:
        cur = self.conn.cursor()
        cur.execute(query, data)
        cur.close()

    def _insert_auto_increment(self, query: str, data) -> int:
        """
        Returns:
            The AUTO_INCREMENT id generated for the dimension table row.
        """

        cur = self.conn.cursor()
        cur.execute(query, data)
        ans = cur.lastrowid
        cur.close()
        assert ans is not None
        return ans

    def _get_current_id_for_dimension(self, dimension: str) -> int:
        return self.query(
            f"""
        SELECT id_{dimension}
        FROM fact_table
        WHERE date = %s
        """,
            (self._today,),
        )

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
                dimension_id = self._insert_auto_increment(
                    f"""
                INSERT INTO dimension_jira (id, issues_done)
                VALUES (%(id)s, %(issues_done)s)
                ON DUPLICATE KEY UPDATE issues_done = %(issues_done)s
                """,
                    {"id": fact_id if fact_id else None, "issues_done": data[0]},
                )
                _print(self.query("select * from dimension_jira"))
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
                # id = self._insert_auto_increment(
                #     f"""
                # INSERT INTO dimension_leetcode (id, python3_problems, mysql_problems, rank_, streak)
                # VALUES (%s, %s, %s, %s, %s)
                # """,
                #     (),
                # )
            case "dimension_strava":
                assert len(data) == 1
                # id = self._insert_auto_increment(
                #     f"""
                # INSERT INTO dimension_strava (id, distance_km)
                # VALUES (%s, %s)
                # """,
                #     (),
                # )
            case _:
                raise StarSchemaError(
                    dedent(
                        f"""Dimension table name `{dimension}` not found. \
                    Did you forget to implement the upsert logic for this dimension?"""
                    )
                )
