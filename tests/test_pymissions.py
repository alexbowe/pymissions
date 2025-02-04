import pytest

from pymissions import *

# TODO: Use an OS provided temporary file, this string doesn't actually work
# ":memory:" works but can't create multiple connections.
TEST_DB_PATH = "test_db.sqlite"


def load_db_in_memory(path):
    """Load a database from disk to an in-memory database so we can test it without modifying the original."""
    in_memory_db = sqlite3.connect(TEST_DB_PATH)
    with sqlite3.connect(path) as file_db:
        file_db.backup(in_memory_db)
    return in_memory_db


def dallas_officer_incident_db():
    db_path = "test_data/dallas_ois_records.sqlite"
    return load_db_in_memory(db_path)


def is_authorization_error(error):
    return "not authorized" in str(error) or "prohibited" in str(error)


# Fixture to have a shared db if we need it - probably not.
@pytest.fixture(scope="function")
def dallas_officer_incident_db_fixture():
    with auto_close(dallas_officer_incident_db()) as db:
        yield db


def test_sqlite_callback_strategy(dallas_officer_incident_db_fixture):
    db = PermissionedSqliteDb(strategy=SqliteCallbackStrategy())

    with auto_close(db.connect(TEST_DB_PATH)) as conn:
        with get_cursor(conn) as c:
            c.execute("SELECT * FROM officers")

    try:
        with auto_close(db.connect(TEST_DB_PATH, user="123")) as user_conn:
            with get_cursor(user_conn) as c:
                c.execute("SELECT * FROM officers")
    except sqlite3.DatabaseError as e:
        assert is_authorization_error(e), "Raised a non-authorization error"
    else:
        assert False, "Did not raise an authorization error"

    # fmt: off
    db.permissions().grant(
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="case_number")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="race")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="gender")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="first_name")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="last_name")),
        ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="full_name")),
    )
    # fmt: on

    with auto_close(db.connect(TEST_DB_PATH, user="123")) as user_conn:
        with get_cursor(user_conn) as c:
            c.execute("SELECT * FROM officers")
            # print(c.fetchall())

    # UPDATE query
    test_case_number = "44523A"
    try:
        with auto_close(db.connect(TEST_DB_PATH, user="123")) as user_conn:
            with get_cursor(user_conn) as c:
                c.execute(
                    f"UPDATE officers SET first_name = 'John' WHERE case_number = '{test_case_number}'"
                )

    except sqlite3.DatabaseError as e:
        assert is_authorization_error(e), "Raised a non-authorization error"
    else:
        assert False, "Did not raise an authorization error"

    db.permissions().grant(
        (
            "123",
            SqlPermission.TABLE_UPDATE,
            SqlResource(table="officers", column="first_name"),
        ),
    )

    with auto_close(db.connect(TEST_DB_PATH, user="123")) as user_conn:
        with get_cursor(user_conn) as c:
            c.execute(
                f"SELECT first_name FROM officers WHERE case_number = '{test_case_number}'"
            )
            assert c.fetchone()[0] != "John", "First name should not be John"
            c.execute(
                f"UPDATE officers SET first_name = 'John' WHERE case_number = '{test_case_number}'"
            )
            c.execute(
                f"SELECT first_name FROM officers WHERE case_number = '{test_case_number}'"
            )
            result = c.fetchone()
            assert result[0] == "John", "UPDATE query did not work as expected"

def test_sql_parsing_strategy(dallas_officer_incident_db_fixture):
    db = PermissionedSqliteDb(strategy=SqlParsingStrategy(dialect="sqlite"))

    # with auto_close(db.connect(TEST_DB_PATH)) as conn:
    #     with get_cursor(conn) as c:
    #         c.execute("SELECT * FROM officers")
    with auto_close(db.connect(TEST_DB_PATH, user="123")) as conn:
        with get_cursor(conn) as c:
            #c.execute("SELECT * FROM officers")
            c.execute("SELECT first_name,* FROM officers,incidents")
    assert False

    # try:
    #     with auto_close(db.connect(TEST_DB_PATH, user="123")) as user_conn:
    #         with get_cursor(user_conn) as c:
    #             c.execute("SELECT * FROM officers")
    # except sqlite3.DatabaseError as e:
    #     assert is_authorization_error(e), "Raised a non-authorization error"
    # else:
    #     assert False, "Did not raise an authorization error"

    # # fmt: off
    # db.permissions().grant(
    #     ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="case_number")),
    #     ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="race")),
    #     ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="gender")),
    #     ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="first_name")),
    #     ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="last_name")),
    #     ("123", SqlPermission.TABLE_SELECT, SqlResource(table="officers", column="full_name")),
    # )
    # # fmt: on

    # with auto_close(db.connect(TEST_DB_PATH, user="123")) as user_conn:
    #     with get_cursor(user_conn) as c:
    #         c.execute("SELECT * FROM officers")
    #         # print(c.fetchall())
    
    # assert False


"""
TODO:
- Try an update query
- Try a transaction

- Write a parser proof of concept.

- Write the outline of the doc
-- Include sections
--- Assumptions
---- What are the salient points in this project
---- What is out of scope
---- What are the assumptions
--- Design
---- Goals
----- Personal Philosophies
----- Modularity
----- Existing DB

---
Other:
- Joins
- Insert
- Delete
- Subqueries
- Views
"""
