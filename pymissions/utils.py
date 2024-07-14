from contextlib import contextmanager


@contextmanager
def auto_close(resource):
    try:
        yield resource
    finally:
        resource.close()


@contextmanager
def get_cursor(connection):
    with auto_close(connection.cursor()) as cursor:
        yield cursor
