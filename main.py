import sqlite3


if __name__ == "__main__":
    #parsed_query = sqlglot.parse("SELECT * FROM users")
    #self._conn = sqlite3.connect(db_path)
    get_tables("data/dallas_ois_records.sqlite")
    
    from sqlglot import parse_one, exp

    # print all column references (a and b)
    for column in parse_one("SELECT a, b + 1 AS c FROM d", dialect="sqlite").find_all(exp.Column):
        print(column.alias_or_name)

    # find all projections in select statements (a and c)
    for select in parse_one("SELECT a, b + 1 AS c FROM d").find_all(exp.Select):
        for projection in select.expressions:
            print(projection.alias_or_name)

    # find all tables (x, y, z)
    for table in parse_one("SELECT * FROM x JOIN y JOIN z").find_all(exp.Table):
        print(table.name)
