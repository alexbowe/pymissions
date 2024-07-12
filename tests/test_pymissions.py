import sqlite3
import pytest

from pymissions import *

# def get_tables(db_path):
#     conn = sqlite3.connect('data/dallas_ois_records.sqlite')
#     cursor = conn.cursor()

#     # Print a message to confirm connection
#     print("Successfully connected to the database.")

#     # Optionally, you can list the tables in the database
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cursor.fetchall()

#     if tables:
#         print("Tables in the database:")
#         for table in tables:
#             print(f"- {table[0]}")
#     else:
#         print("No tables found in the database.")

#     # Don't forget to close the connection when you're done
#     conn.close()


def load_db_in_memory(path):
    """Load a database from disk to an in-memory database. This allows
    multiple instances of a database to be used for testing.
    """
    in_memory_db = sqlite3.connect(":memory:")
    with sqlite3.connect(path) as file_db:
        file_db.backup(in_memory_db)
    return in_memory_db


def dallas_db():
    db_path = "test_data/dallas_ois_records.sqlite"
    return load_db_in_memory(db_path)


# Fixture to have a shared db if we need it - probably not.
@pytest.fixture(scope="function")
def dallas_db_fixture():
    with auto_close(dallas_db()) as db:
        yield db


def test_dallas_db():
    db = dallas_db()
    pdb = PermissionedSqliteConnection(db)
    pdb.permissions().grant("123", SqlPermission.TABLE_INSERT, SqlResource(table="*", columns="*"))
    
    # pm_conn.permissions().grant("123", SqlPermission.TABLE_INSERT, SqlResource(table="*", columns="*"))
    #with get_cursor(dallas_db) as c:
    #    c.execute("SELECT * FROM officers")
    #    print(c.fetchall())
