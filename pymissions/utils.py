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

def _format_function_location(func, log_location):
    if not log_location:
        return ""
    
    file_name = func.__code__.co_filename
    line_number = func.__code__.co_firstlineno
    return f"{file_name}:{line_number}: "

def _format_function_name(func):
    func_name = func.__name__
    module_name = func.__module__
    class_name = (
        func.__qualname__.split(".")[0] if "." in func.__qualname__ else None
    )
    location = format_location(func, True)  # Always include location for default formatter
    return f"{location}{module_name}.{class_name + '.' if class_name else ''}{func_name}"

def log_inputs_and_outputs(
    logger,
    log_location=True,
    format_function=None,
    format_input=None,
    format_output=None,
):
    format_input = format_input or (
        lambda *args, **kwargs: f"*args={args}, **kwargs={kwargs}"
    )
    format_output = format_output or (lambda result: result)
    format_function = format_function or _format_function_name
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_location = _format_function_location(func, log_location)
            func_info = format_function(func)
            inputs = format_input(*args, **kwargs)

            try:
                result = func(*args, **kwargs)
                output = format_output(result)
                logger.debug(f"{func_location}{func_info}({inputs}) -> {output}")
            except Exception:
                logger.debug(f"{func_location}{func_info}({inputs}) -> EXCEPTION")
                raise

            return result

        return wrapper

    return decorator
