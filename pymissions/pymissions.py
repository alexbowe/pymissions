from abc import abstractmethod, ABC
import sqlite3

from collections import defaultdict
from enum import Enum
from dataclasses import dataclass
from functools import partial

from typing import Optional, Set, Dict, Tuple, Iterable

from .utils import *
from sqlglot import parse_one, exp

SYSTEM_USER = "system"

tree = lambda: defaultdict(tree)


# Define our own exception base class for easier filtering
class PermissionError(Exception):
    pass


@dataclass
class SqlResource:
    table: str
    column: str


class SqlPermission(Enum):
    TABLE_SELECT = "table::select"
    TABLE_UPDATE = "table::update"
    # TABLE_INSERT = "table::insert"
    # TABLE_DELETE = "table::delete"


SQLITE_ACTION_TO_PERMISSION_MAP = {
    # SQLITE_SELECT seems to be permission to select at all.
    # We can infer hat from the other permissions.
    sqlite3.SQLITE_READ: SqlPermission.TABLE_SELECT,
    sqlite3.SQLITE_UPDATE: SqlPermission.TABLE_UPDATE,
    # sqlite3.SQLITE_INSERT: SqlPermission.TABLE_INSERT,
    # sqlite3.SQLITE_DELETE: SqlPermission.TABLE_DELETE,
}

# Object/document stores won't necessarily have a concept of rows/columns
# so they might need a different kind of permission set

PermissionGrant = Tuple[str, SqlPermission, SqlResource]

class UserPermissions(ABC):
    @abstractmethod
    def grant(self, permission, resource):
        raise NotImplementedError()

    @abstractmethod
    def check(self, permission, resource):
        raise NotImplementedError()
    
class PermissionManager(ABC):
    @abstractmethod
    def grant(self, user, permission, resource):
        raise NotImplementedError()

    @abstractmethod
    def check(self, user, permission, resource):
        raise NotImplementedError()


class BasicUserPermissions(UserPermissions):
    def __init__(self):
        self._tables = tree()

    def grant(self, permission, resource):
        self._tables[resource.table][resource.column] = permission
        return self

    def check(self, permission, resource):
        print(resource.table, resource.column)
        if resource.table not in self._tables:
            return False
        print("a")
        if resource.column not in self._tables[resource.table]:
            return False
        print("a")
        if self._tables[resource.table][resource.column] != permission:
            return False
        print("c")
        return True


class BasicPermissionSet(PermissionManager):
    """This would benefit from being stored in the DB itself, to make it
    easier to change schemas. For the scope of the MVP this is acceptable."""

    def __init__(self):
        self._permissions = defaultdict(BasicUserPermissions)

    def grant(self, *args: Iterable[PermissionGrant]):
        for user, permission, resource in args:
            self._permissions[user].grant(permission, resource)
        return self

    def check(self, user, permission, resource):
        if user == SYSTEM_USER: return True
        return self._permissions[user].check(permission, resource)


class PermissionStrategy(ABC):
    @abstractmethod
    def setup(self, connection):
        raise NotImplementedError()

    def permission_manager_type(self) -> type:
        raise NotImplementedError()
    
    def wrap_connection(self, connection):
        raise NotImplementedError()
    
    

class PermissionedSqliteCursor:
    def __init__(self, connection, cursor, parser=None):
        self._connection = connection
        self._cursor = cursor
        self._parser = parser

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def _execute_parse(self, query, *args, **kwargs):
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
        # do this as a transaction
        # so we can easily roll back something if needed
        return self._cursor.execute(query, *args, **kwargs)

    def _execute_hook(self, query, *args, **kwargs):
        # https://charlesleifer.com/blog/sqlite-database-authorization-and-access-control-with-python/
        def authorizor_callback(action, arg1, arg2, db_name, trigger_name):
            if self._connection.user == SYSTEM_USER: return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_SELECT: return sqlite3.SQLITE_OK
            permission = SQLITE_ACTION_TO_PERMISSION_MAP[action]
            if permission == SqlPermission.TABLE_SELECT:
                table_name, column_name = arg1, arg2
                allowed = self._connection._permissions.check(
                    self._connection.user,
                    permission,
                    SqlResource(table_name, column_name),
                )
                print("allowed:", allowed)
                if allowed:
                    return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        self._connection.set_authorizer(authorizor_callback)
        self._cursor.execute(query, *args, **kwargs)

    def execute(self, query, *args, **kwargs):
        return self._execute_hook(query, *args, **kwargs)


class PermissionedSqliteConnection:
    def __init__(self, connection, permissions=None, user=SYSTEM_USER):
        self._connection = connection
        self._permissions = permissions or BasicPermissionSet()
        self._user = user
        # TODO: update permissions in database if the database supports it natively (in other Permissioned db)

    @property
    def user(self):
        # Read only accessor for user
        return self._user

    def __getattr__(self, name):
        return getattr(self._connection, name)

    def _get_parser(self):
        return partial(parse_one, read="sqlite", into="sqlite")

    def cursor(self):
        # Wrap this with something that points back to this
        # and filters the query
        return PermissionedSqliteCursor(
            self, self._connection.cursor(), self._get_parser()
        )

    def permissions(self):
        if self.user != SYSTEM_USER:
            raise PermissionError(
                "User does not have permissions to manage permissions"
            )
        return self._permissions

    def user_connection(self, auth_key):
        if self.user != SYSTEM_USER:
            raise PermissionError("User does not have permissions to switch users")
        return PermissionedSqliteConnection(
            self._connection, user=auth_key, permissions=self.permissions()
        )


"""
A PermissionSet:
- implements grant, check
- in future: revoke, load, save
- Can be extended to be stored in a db

A PermissionStrategy has a:
- A PermissionSet factory method (returns the class). Defaults to BasicPermissionSet.
-- This allows a strategy to provide its own permissions if needed (e.g. when storing in the same database)
- link to the db
- link to the permissions
- A setup hook (called before a connection) < future work for different strategies.
- sql execution hook

A DbConnector has:
- A strategy (ctor parameter, would default to SQL permission strategy)
- A permission set (it creates)
- load_permissions()
- connect() function

A ConnectionWrapper:
- wraps cursor()

A cursor wrapper:
- wraps execute() to use the permission strategy

We provide an SqliteConnector with a SqliteCallbackStrategy

Stretch goals:
- Provide SqlParserStrategy
"""
