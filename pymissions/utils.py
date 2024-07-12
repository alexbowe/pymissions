from contextlib import contextmanager

@contextmanager
def auto_close(resource):
    try:
        yield resource
    finally:
        resource.close()

@contextmanager
def get_cursor(db_connection):
    with auto_close(db_connection.cursor()) as cursor:
        yield cursor
