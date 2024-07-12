import sqlite3
from enum import Enum
from dataclasses import dataclass

from typing import Optional, Set

from .utils import *
from sqlglot import parse_one, exp


# Define our own exception base class for easier filtering
class PermissionError(Exception):
    pass


class SqlPermission(Enum):
    TABLE_SELECT = "table::select"
    TABLE_INSERT = "table::insert"
    TABLE_UPDATE = "table::update"
    TABLE_DELETE = "table::delete"


@dataclass
class SqlResource:
    table: str
    rows: Optional[set] = None
    columns: Optional[set] = None


# Object/document stores won't necessarily have a concept of rows/columns
# so they might need a different kind of permission set
class SqlPermissionSet:
    def grant(self, auth_key, permission, resource):
        # store this in a dictionary and pickle it
        return self

    @classmethod
    def load(cls, io):
        raise NotImplementedError("Out of scope for MVP")

    # How to handle revoking subsets?
    # Maybe a permission can be revoked?
    def revoke(auth_key, permission, resource):
        raise NotImplementedError("Out of scope for MVP")

    def check(self, auth_key, permission, resource):
        # if "*" in their tables then thats fine
        # else
        raise NotImplementedError("Out of scope for MVP")


class PermissionedSqliteCursor:
    def __init__(self, parent_db, cursor):
        self._parent_db = parent_db
        self._cursor = cursor

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def execute(self, query, *args, **kwargs):
        """
        Execute a query with the given auth key.

        This method should be implemented by subclasses to:
        1. Parse the query
        2. Check the permissions
        3. Execute the query
        4. Return the result
        """
        # get tables from query
        # create views for each table
        # execute query on view
        return self._cursor.execute(query, *args, **kwargs)


class PermissionedSqliteConnection:
    # from_dialect = "sqlite"
    # to_dialect = "sqlite"

    def __init__(self, db, permissions=None):
        self._db = db
        self._permissions = permissions or SqlPermissionSet()
        # TODO: update permissions in database if the database supports it natively (in other Permissioned db)

    def __getattr__(self, name):
        return getattr(self._db, name)

    def cursor(self):
        # Wrap this with something that points back to this
        # and filters the query
        return PermissionedSqliteCursor(self, self._db.cursor())

    def permissions(self):
        return self._permissions

    # TODO: implement this if we go with the view option
    def _create_user_view_of_table(self, auth_key: str, table_name: str):
        pass
