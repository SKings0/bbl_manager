import sqlite3


DATABASE = "file/bbl.db"
INSERT_QUERY_SEPARATOR = ", "
INSERT_QUERY_PLACEHOLDER = "?"


def drop_table(table):
    sql = "DROP TABLE IF EXISTS {}".format(table)
    
    execute(sql)


def create_table(table, columns):
    # Trim columns tuples to only first two values (name and type)
    formatted_columns = [x[0] + " " + x[1] for x in columns]
    parameters = INSERT_QUERY_SEPARATOR.join(formatted_columns)
    sql = "CREATE TABLE IF NOT EXISTS {} ({})".format(table, parameters)

    execute(sql)


def reset_table(table, columns):
    drop_table(table)
    create_table(table, columns)


def insert(table, values):
    sql_values = INSERT_QUERY_SEPARATOR.join(
            [INSERT_QUERY_PLACEHOLDER] * len(values))
    sql = "INSERT INTO {} VALUES({})".format(table, sql_values)

    execute(sql, values=values)


def get_values(table, columns):
    parameters = INSERT_QUERY_SEPARATOR.join(columns)
    sql = "SELECT {} FROM {}".format(parameters, table)

    return fetchall(sql)


def fetchall(sql):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(sql)

    return c.fetchall()


def execute(sql, values=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if values is None:
        c.execute(sql)
    else:
        c.execute(sql, values)

    conn.commit()
