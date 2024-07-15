import sqlite3
import logging

from pymissions.pymissions import *
from .sqlite_codes import SQLITE_CODE_TO_STRING


LOGGER = logging.getLogger(__name__)


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
    universally_allowed_actions = {
        # SQLITE_SELECT is whether users have the right to select at all. Can be inferred.
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_TRANSACTION,
    }

    def __init__(self, permissions, user):
        self._permissions = permissions
        self._user = user

    @log_inputs_and_outputs(
        LOGGER,
        format_function=lambda func: "SqliteCallbackAuthorizor",
        format_input= lambda *args, **kwargs: f"{SQLITE_CODE_TO_STRING[args[1]]}, {', '.join(map(str, args[2:]))}",
        format_output=SQLITE_CODE_TO_STRING.get,
    )
    def __call__(self, action, arg1, arg2, db_name, trigger_name):
        if self._user == SYSTEM_USER:
            return sqlite3.SQLITE_OK
        if action in self.universally_allowed_actions:
            return sqlite3.SQLITE_OK

        if action not in SQLITE_ACTION_TO_PERMISSION_MAP:
            LOGGER.warning(f"Unsupported action: {action}")
            return sqlite3.SQLITE_DENY

        permission = SQLITE_ACTION_TO_PERMISSION_MAP.get(action)
        table_name, column_name = arg1, arg2
        status = self._permissions.check(
            self._user, permission, SqlResource(table_name, column_name)
        )
        return SQLITE_STATUS_MAP[status]


class PermissionedSqliteDb(PermissionedSqlDb):
    def __init__(self, strategy=None):
        strategy = strategy or SqliteCallbackStrategy()
        super().__init__(strategy)
    
    def _get_columns_of_table(self, connection, table_name):
        with get_cursor(connection._native_connection) as c:
            c.execute(f"PRAGMA table_info({table_name})")
            columns = {row[1] for row in c.fetchall()}
            return columns

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
