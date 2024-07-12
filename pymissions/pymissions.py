import sqlite3
from enum import Enum

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


class SqlResource:
    def __init__(self, table, rows=None, columns=None):
        pass


# Object/document stores won't necessarily have a concept of rows/columns
# so they might need a different kind of permission set
class SqlPermissionSet:
    def grant(self, auth_key, permission, resource):
        # store this in a dictionary and pickle it
        pass
    
    @classmethod
    def load(cls, io):
        raise NotImplementedError("Out of scope for MVP")

    # How to handle revoking subsets?
    # Maybe a permission can be revoked?
    def revoke(auth_key, permission, resource):
        raise NotImplementedError("Out of scope for MVP")

class PermissionedSqliteConnection:
    # from_dialect = "sqlite"
    # to_dialect = "sqlite"

    def __init__(self, db, permissions=None):
        self._db = db
        self._permissions = permissions or SqlPermissionSet()
        # TODO: update permissions in database if the database supports it natively (in other Permissioned db)

    # def cursor(self):
    #     return self._db_connection.cursor()

    def permissions(self):
        return self._permissions

    # TODO: implement this if we go with the view option
    def _create_user_view_of_table(self, auth_key: str, table_name: str):
        pass

    def execute(self, auth_key: str, query: str):
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
