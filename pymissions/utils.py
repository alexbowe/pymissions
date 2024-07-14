from contextlib import contextmanager
from collections import defaultdict


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


Tree = lambda: defaultdict(Tree)
