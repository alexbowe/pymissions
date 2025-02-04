from abc import abstractmethod, ABC
from collections import defaultdict
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Iterable

from .utils import *

SYSTEM_USER = "system"


# Define our own exception base class for easier filtering
class PermissionError(Exception):
    pass


@dataclass
class SqlResource:
    table: str
    column: str


class SqlPermission(Enum):
    UNKOWN = "system::unkown"
    TABLE_SELECT = "table::select"
    TABLE_UPDATE = "table::update"
    # TABLE_INSERT = "table::insert"
    # TABLE_DELETE = "table::delete"


class PermissionStatus(Enum):
    GRANTED = "granted"
    DENIED = "denied"
    IGNORED = "ignored"


Entitlement = Tuple[str, SqlPermission, SqlResource]


class UserPermissions(ABC):
    @abstractmethod
    def grant(self, permission, resource):
        raise NotImplementedError()

    @abstractmethod
    def check(self, permission, resource) -> PermissionStatus:
        raise NotImplementedError()


class PermissionSet(ABC):
    @abstractmethod
    def grant(self, user, permission, resource):
        raise NotImplementedError()

    @abstractmethod
    def check(self, user, permission, resource) -> PermissionStatus:
        raise NotImplementedError()


class BasicUserPermissions(UserPermissions):
    def __init__(self):
        self._tables = defaultdict(lambda: defaultdict(set))

    def grant(self, permission, resource):
        self._tables[resource.table][resource.column].add(permission)
        return self

    def check(self, permission, resource):
        # TODO: add way to configure this so we can ignore rather than deny.
        # This would allow people to select * and only get the columns
        # they have access to. For simplicity we do it this way for now.
        if resource.table not in self._tables:
            return PermissionStatus.DENIED

        if resource.column not in self._tables[resource.table]:
            return PermissionStatus.DENIED

        if permission not in self._tables[resource.table][resource.column]:
            return PermissionStatus.DENIED

        return PermissionStatus.GRANTED


class BasicPermissionSet(PermissionSet):
    """This would benefit from being stored in the DB itself, to make it
    easier to change schemas. For the scope of the MVP this is acceptable."""

    def __init__(self):
        self._permissions = defaultdict(BasicUserPermissions)

    def grant(self, *args: Iterable[Entitlement]):
        for user, permission, resource in args:
            self._permissions[user].grant(permission, resource)
        return self

    def check(self, user, permission, resource):
        if user == SYSTEM_USER:
            return PermissionStatus.GRANTED
        return self._permissions[user].check(permission, resource)


class PermissionStrategy(ABC):
    def permissions(self):
        return BasicPermissionSet()

    def wrap_connection(self, db, connection, user):
        return PermissionedSqlConnection(db, connection, user)

    @abstractmethod
    def wrap_execute(self, query, user): ...


class PermissionedSqlCursor:
    def __init__(self, connection, cursor):
        self._connection = connection
        self._native_cursor = cursor

    def __getattr__(self, name):
        return getattr(self._native_cursor, name)

    def _native_execute(self, query):
        return self._native_cursor.execute(query)

    def execute(self, query):
        return self._connection._db._strategy.wrap_execute(self, query)


class PermissionedSqlConnection:
    def __init__(self, db, native_connection, user=SYSTEM_USER):
        self._db = db
        self._native_connection = native_connection
        self._user = user

    @property
    def user(self):
        return self._user

    def cursor(self):
        return PermissionedSqlCursor(self, self._native_connection.cursor())
    
    def get_columns_of_table(self, table_name):
        return self._db._get_columns_of_table(self, table_name)

    def __getattr__(self, name):
        return getattr(self._native_connection, name)


class PermissionedSqlDb(ABC):
    def __init__(self, strategy):
        self._strategy = strategy
        self._permissions = strategy.permissions()

    def permissions(self):
        return self._permissions

    def wrap_native_connection(self, connection, user=None):
        user = user or SYSTEM_USER
        return PermissionedSqlConnection(self, connection, user=user)

    def connect(self, *args, **kwargs):
        user = kwargs.pop("user", SYSTEM_USER)
        base_connection = self._base_connect(*args, **kwargs)
        return self.wrap_native_connection(base_connection, user=user)

    @abstractmethod
    def _base_connect(self, *args, **kwargs): ...

    @abstractmethod
    def _get_columns_of_table(self, connection, table_name): ...


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

A PermissionedConnection:
- wraps cursor()

A cursor wrapper:
- wraps execute() to use the permission strategy

We provide an SqliteConnector with a SqliteCallbackStrategy

Stretch goals:
- Provide SqlParserStrategy


# Out of Scope:
- Support for wildcard specifications
- Support for wildcard queries returning empty columns when they don't have access to the columns
- Operations...


# Philosophy
- Be stricter in the first versions - this avoids people coming to rely on
  behavior that changes. (e.g. IGNORE vs DENY)
"""
