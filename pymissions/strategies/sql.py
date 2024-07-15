from pymissions import PermissionStrategy

from sqlglot import parse_one, exp
from sqlglot.optimizer.scope import build_scope
from sqlglot.optimizer.scope import find_all_in_scope
from sqlglot.optimizer.qualify import qualify

class SqlParsingStrategy(PermissionStrategy):
    def __init__(self, dialect, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dialect = dialect

    def wrap_execute(self, cursor, query):
        #columns = cursor._connection.get_columns_of_table("officers")
        #print("columns:", columns)
        
        ast = parse_one(query, dialect=self._dialect)
    
        read_columns = set()

        selects = list(ast.find_all(exp.Select))
        print(selects)
        print()
        for select in selects:
            print(repr(select))
            print()
            # for expression in select.expressions:
            #     if isinstance(expression, exp.Star):
            #         #read_columns.update(cursor._connection.get_columns_of_table(expression.table))
            #         print("STAR")
            #     #print(expression)
            #     else:
            #         print(repr(expression))
        
        # for column in ast.find_all(exp.Column):
        #     if isinstance(column, exp.Star):
        #         if column.table:
        #             table_name = column.table
        #             columns = cursor._connection.get_columns_of_table(table_name)
        #             print(f"Columns for table {table_name}: {columns}")
        #         else:
        #             # If there's no specific table for the star, we might need to check all tables in the query
        #             for table in ast.find_all(exp.Table):
        #                 table_name = table.name
        #                 columns = cursor._connection.get_columns_of_table(table_name)
        #                 print(f"Columns for table {table_name}: {columns}")
        #     else:
        #         print(f"Column: {column.name}, Table: {column.table}")

        # root = build_scope(ast)        
        # for scope in root.traverse():
        #     print(scope)
        #     scope.
        #     for alias, (node, source) in scope.selected_sources.items():
        #         print("source:", source)

        # # tables = set()
        # # columns = set()
        # # operations = set()

        # # # Find all tables
        # # for table in ast.find_all(exp.Table):
        # #     if table.db:
        # #         tables.add(f"{table.db}.{table.name}")
        # #     else:
        # #         tables.add(table.name)

        # # Find all columns and their associated tables
        # for column in ast.find_all(exp.Column):
        #     print(column.table)

        # # Determine operations
        # if isinstance(ast, exp.Select):
        #     operations.add("SELECT")
        # elif isinstance(ast, exp.Update):
        #     operations.add("UPDATE")
        # elif isinstance(ast, exp.Insert):
        #     operations.add("INSERT")
        # elif isinstance(ast, exp.Delete):
        #     operations.add("DELETE")

        # # Handle subqueries
        # for subquery in ast.find_all(exp.Subquery):
        #     subquery_ast = subquery.this
        #     if isinstance(subquery_ast, exp.Select):
        #         operations.add("SELECT")
        #     for table in subquery_ast.find_all(exp.Table):
        #         if table.db:
        #             tables.add(f"{table.db}.{table.name}")
        #         else:
        #             tables.add(table.name)
        #     for column in subquery_ast.find_all(exp.Column):
        #         if column.table:
        #             columns.add(f"{column.table}.{column.name}")
        #         else:
        #             columns.add(column.name)

        # print("Tables:", tables)
        # print("Columns:", columns)
        # print("Operations:", operations)
        
        # for table in parsed_query.find_all(exp.Table):
        #     print("table:", table.name)
        
        # # find operations on each table
        # for select in parsed_query.find_all(exp.Select):
        #     print("select:", select.expressions)
            
        # for column in parsed_query.find_all(
        #     exp.Column
        # ):
        #     print(column.alias_or_name)
        print()
        return cursor._native_execute(query)
