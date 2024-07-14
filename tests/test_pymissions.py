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


def test_sqlite_permissions():
    sqlite_connection = dallas_officer_incident_db()
    system_connection = PermissionedSqliteConnection(sqlite_connection)

    with get_cursor(system_connection) as c:
        c.execute("SELECT * FROM officers")
        #print(c.fetchall())

    user_connection = system_connection.user_connection("123")

    try:
        with get_cursor(user_connection) as c:
            c.execute("SELECT * FROM officers")
    except sqlite3.DatabaseError as e:
        if "not authorized" not in str(e) and "prohibited" not in str(e):
            assert False, "Did not raise an authorization error"
    else:
        assert False, "Did not raise an authorization error"

    system_connection.permissions().grant(
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="case_number")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="race")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="gender")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="first_name")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="last_name")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="full_name")),
    )
    
    # .grant(
    #    "123", SqlPermission.TABLE_INSERT, SqlResource(table="officers", column="*")
    # )

    print(user_connection._permissions._permissions["123"]._tables)
    with get_cursor(user_connection) as c:
        c.execute("SELECT * FROM officers")
        # print(c.fetchall())

    #assert False


"""
Tests to do

"""
