import sqlite3

connection = sqlite3.connect(r"database\database.sqlite")
sqlite_create_table_query = """CREATE TABLE playlist (
userid INTEGER PRIMARY KEY,
list STRING NOT NULL)
"""

cursor = connection.cursor()
print("Successfully Connected to SQLite")
cursor.execute(sqlite_create_table_query)
connection.commit()
print("SQLite table created")

cursor.close()

connection.close()
