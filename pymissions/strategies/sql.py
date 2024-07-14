# def _execute_parse(self, query, *args, **kwargs):
#     Execute a query with the given auth key.
#     This method should be implemented by subclasses to:
#     1. Parse the query
#     2. Check the permissions
#     3. Execute the query
#     4. Return the result
#     # get tables from query
#     # create views for each table
#     # execute query on view
#     # do this as a transaction
#     # so we can easily roll back something if needed
#     return self._cursor.execute(query, *args, **kwargs)


class SqlParsingStrategy:
    pass
