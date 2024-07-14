import sqlite3
from typing import Any

from pymissions.pymissions import *
from .sqlite_codes import SQLITE_CODE_TO_STRING


SQLITE_ACTION_TO_PERMISSION_MAP = {
    sqlite3.SQLITE_READ: SqlPermission.TABLE_SELECT,
    sqlite3.SQLITE_UPDATE: SqlPermission.TABLE_UPDATE,
    # sqlite3.SQLITE_INSERT: SqlPermission.TABLE_INSERT,
    # sqlite3.SQLITE_DELETE: SqlPermission.TABLE_DELETE,
}

SQLITE_STATUS_MAP = {
    PermissionStatus.GRANTED: sqlite3.SQLITE_OK,
    PermissionStatus.DENIED: sqlite3.SQLITE_DENY,
    PermissionStatus.IGNORED: sqlite3.SQLITE_IGNORE,
}


class SqliteCallbackAuthorizor:
    # TODO: Add other universally allowed permissions such as transactions...
    universally_allowed_actions = {
        sqlite3.SQLITE_SELECT,  # SQLITE_SELECT is whether users have the right to select at all. Can be inferred.
        sqlite3.SQLITE_TRANSACTION,
    }

    def __init__(self, permissions, user):
        self._permissions = permissions
        self._user = user

    def __call__(self, action, arg1, arg2, db_name, trigger_name):
        # fmt: off
        print(SQLITE_CODE_TO_STRING[action], arg1, arg2, db_name, trigger_name)

        print("a")
        if self._user == SYSTEM_USER: return sqlite3.SQLITE_OK
        print("b")
        if action in self.universally_allowed_actions: return sqlite3.SQLITE_OK
        print("c")
        if action not in SQLITE_ACTION_TO_PERMISSION_MAP:
            # TODO: Log the unsupported action and user
            print("d")
            return sqlite3.SQLITE_DENY
        # fmt: on

        permission = SQLITE_ACTION_TO_PERMISSION_MAP.get(action)

        table_name, column_name = arg1, arg2

        status = self._permissions.check(
            self._user, permission, SqlResource(table_name, column_name)
        )
        print(status)
        result = SQLITE_STATUS_MAP[status]
        print("response:", SQLITE_CODE_TO_STRING[result])
        return result


class PermissionedSqliteDb(PermissionedSqlDb):
    def __init__(self, strategy=None):
        strategy = strategy or SqliteCallbackStrategy()
        super().__init__(strategy)

    def _base_connect(self, *args, **kwargs):
        return sqlite3.connect(*args, **kwargs)


class SqliteCallbackStrategy(PermissionStrategy):
    """Native SQLite permissioning strategy that uses callback functions."""

    def wrap_execute(self, cursor, query):
        connection = cursor._connection
        db = connection._db

        # TODO: This should be done atomically
        connection._native_connection.set_authorizer(
            SqliteCallbackAuthorizor(db.permissions(), connection.user)
        )
        results = cursor._native_execute(query)
        connection._native_connection.set_authorizer(None)
        return results


# self._authorizor = SqliteCallbackAuthorizor(self._db.permissions(), self._user)
# self._connection.set_authorizer(self._authorizor)
