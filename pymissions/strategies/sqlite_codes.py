# https://charlesleifer.com/blog/sqlite-database-authorization-and-access-control-with-python/
import sqlite3

# fmt: off
# Return values
SQLITE_OK     = 0
SQLITE_DENY   = 1
SQLITE_IGNORE = 2

# Actions and args
SQLITE_CREATE_INDEX        = 1   # Index Name      Table Name
SQLITE_CREATE_TABLE        = 2   # Table Name      NULL
SQLITE_CREATE_TEMP_INDEX   = 3   # Index Name      Table Name
SQLITE_CREATE_TEMP_TABLE   = 4   # Table Name      NULL
SQLITE_CREATE_TEMP_TRIGGER = 5   # Trigger Name    Table Name
SQLITE_CREATE_TEMP_VIEW    = 6   # View Name       NULL
SQLITE_CREATE_TRIGGER      = 7   # Trigger Name    Table Name
SQLITE_CREATE_VIEW         = 8   # View Name       NULL
SQLITE_DELETE              = 9   # Table Name      NULL
SQLITE_DROP_INDEX          = 10  # Index Name      Table Name
SQLITE_DROP_TABLE          = 11  # Table Name      NULL
SQLITE_DROP_TEMP_INDEX     = 12  # Index Name      Table Name
SQLITE_DROP_TEMP_TABLE     = 13  # Table Name      NULL
SQLITE_DROP_TEMP_TRIGGER   = 14  # Trigger Name    Table Name
SQLITE_DROP_TEMP_VIEW      = 15  # View Name       NULL
SQLITE_DROP_TRIGGER        = 16  # Trigger Name    Table Name
SQLITE_DROP_VIEW           = 17  # View Name       NULL
SQLITE_INSERT              = 18  # Table Name      NULL
SQLITE_PRAGMA              = 19  # Pragma Name     1st arg or NULL
SQLITE_READ                = 20  # Table Name      Column Name
SQLITE_SELECT              = 21  # NULL            NULL
SQLITE_TRANSACTION         = 22  # Operation       NULL
SQLITE_UPDATE              = 23  # Table Name      Column Name
SQLITE_ATTACH              = 24  # Filename        NULL
SQLITE_DETACH              = 25  # Database Name   NULL
SQLITE_ALTER_TABLE         = 26  # Database Name   Table Name
SQLITE_REINDEX             = 27  # Index Name      NULL
SQLITE_ANALYZE             = 28  # Table Name      NULL
SQLITE_CREATE_VTABLE       = 29  # Table Name      Module Name
SQLITE_DROP_VTABLE         = 30  # Table Name      Module Name
SQLITE_FUNCTION            = 31  # NULL            Function Name
SQLITE_SAVEPOINT           = 32  # Operation       Savepoint Name
SQLITE_RECURSIVE           = 33  # NULL            NULL

SQLITE_CODE_TO_STRING = {
    sqlite3.SQLITE_OK:                 "SQLITE_OK",
    sqlite3.SQLITE_DENY:               "SQLITE_DENY",
    sqlite3.SQLITE_IGNORE:             "SQLITE_IGNORE",
    sqlite3.SQLITE_CREATE_INDEX:       "SQLITE_CREATE_INDEX",
    sqlite3.SQLITE_CREATE_TABLE:       "SQLITE_CREATE_TABLE",
    sqlite3.SQLITE_CREATE_TEMP_INDEX:  "SQLITE_CREATE_TEMP_INDEX",
    sqlite3.SQLITE_CREATE_TEMP_TABLE:  "SQLITE_CREATE_TEMP_TABLE",
    sqlite3.SQLITE_CREATE_TEMP_TRIGGER:"SQLITE_CREATE_TEMP_TRIGGER",
    sqlite3.SQLITE_CREATE_TEMP_VIEW:   "SQLITE_CREATE_TEMP_VIEW",
    sqlite3.SQLITE_CREATE_TRIGGER:     "SQLITE_CREATE_TRIGGER",
    sqlite3.SQLITE_CREATE_VIEW:        "SQLITE_CREATE_VIEW",
    sqlite3.SQLITE_DELETE:             "SQLITE_DELETE",
    sqlite3.SQLITE_DROP_INDEX:         "SQLITE_DROP_INDEX",
    sqlite3.SQLITE_DROP_TABLE:         "SQLITE_DROP_TABLE",
    sqlite3.SQLITE_DROP_TEMP_INDEX:    "SQLITE_DROP_TEMP_INDEX",
    sqlite3.SQLITE_DROP_TEMP_TABLE:    "SQLITE_DROP_TEMP_TABLE",
    sqlite3.SQLITE_DROP_TEMP_TRIGGER:  "SQLITE_DROP_TEMP_TRIGGER",
    sqlite3.SQLITE_DROP_TEMP_VIEW:     "SQLITE_DROP_TEMP_VIEW",
    sqlite3.SQLITE_DROP_TRIGGER:       "SQLITE_DROP_TRIGGER",
    sqlite3.SQLITE_DROP_VIEW:          "SQLITE_DROP_VIEW",
    sqlite3.SQLITE_INSERT:             "SQLITE_INSERT",
    sqlite3.SQLITE_PRAGMA:             "SQLITE_PRAGMA",
    sqlite3.SQLITE_READ:               "SQLITE_READ",
    sqlite3.SQLITE_SELECT:             "SQLITE_SELECT",
    sqlite3.SQLITE_TRANSACTION:        "SQLITE_TRANSACTION",
    sqlite3.SQLITE_UPDATE:             "SQLITE_UPDATE",
    sqlite3.SQLITE_ATTACH:             "SQLITE_ATTACH",
    sqlite3.SQLITE_DETACH:             "SQLITE_DETACH",
    sqlite3.SQLITE_ALTER_TABLE:        "SQLITE_ALTER_TABLE",
    sqlite3.SQLITE_REINDEX:            "SQLITE_REINDEX",
    sqlite3.SQLITE_ANALYZE:            "SQLITE_ANALYZE",
    sqlite3.SQLITE_CREATE_VTABLE:      "SQLITE_CREATE_VTABLE",
    sqlite3.SQLITE_DROP_VTABLE:        "SQLITE_DROP_VTABLE",
    sqlite3.SQLITE_FUNCTION:           "SQLITE_FUNCTION",
    sqlite3.SQLITE_SAVEPOINT:          "SQLITE_SAVEPOINT",
    sqlite3.SQLITE_RECURSIVE:          "SQLITE_RECURSIVE",
}

# fmt: on
