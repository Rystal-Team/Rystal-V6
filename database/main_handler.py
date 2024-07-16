import os

import mysql.connector

database = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
)

database_tables = ["guild", "rank", "note"]
create_statements = {
    "guild": "CREATE TABLE guild (guild_id VARCHAR(24) PRIMARY KEY, language VARCHAR(255), settings JSON)",
    "rank" : "CREATE TABLE rank (user_id VARCHAR(24) PRIMARY KEY, data JSON, total_xp INT(255))",
    "note" : "CREATE TABLE note (user_id VARCHAR(24) PRIMARY KEY, notes JSON)",
}
existing_tables = []

cursor = database.cursor(buffered=True)


def startup():
    database.ping(reconnect=True, attempts=3)

    cursor.execute("SHOW TABLES")

    for (x,) in cursor:
        existing_tables.append(x)

    for table_name in database_tables:
        if not table_name in existing_tables:
            cursor.execute(create_statements[table_name])

    return


def check_exists(table, key, value):
    statement = f"SELECT {key} FROM {table} WHERE {key} = %s"
    values = (value,)
    cursor.execute(statement, values)
    result = cursor.fetchall()

    return not (len(result) == 0)
