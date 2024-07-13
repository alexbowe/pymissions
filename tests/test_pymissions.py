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


def load_db_in_memory(path):
    """Load a database from disk to an in-memory database. This allows
    multiple instances of a database to be used for testing.
    """
    in_memory_db = sqlite3.connect(":memory:")
    with sqlite3.connect(path) as file_db:
        file_db.backup(in_memory_db)
    return in_memory_db


def dallas_officer_incident_db():
    db_path = "test_data/dallas_ois_records.sqlite"
    return load_db_in_memory(db_path)


# Fixture to have a shared db if we need it - probably not.
@pytest.fixture(scope="function")
def dallas_officer_incident_db_fixture():
    with auto_close(dallas_officer_incident_db()) as db:
        yield db


def test_pymissions():
    db = dallas_officer_incident_db()
    pdb = PermissionedSqliteConnection(db)

    with get_cursor(pdb) as c:
        c.execute("SELECT * FROM officers")
        print(c.fetchall())

    pdb.permissions().grant(
        "123", SqlPermission.TABLE_INSERT, SqlResource(table="*", rows="*", columns="*")
    ).grant(
        "123", SqlPermission.TABLE_SELECT, SqlResource(table="*", rows="*", columns="*")
    )

    with get_cursor(pdb) as c:
        c.as_user("123").execute("SELECT * FROM officers")
        print(c.fetchall())

    assert False


"""
Tests to do

"""
