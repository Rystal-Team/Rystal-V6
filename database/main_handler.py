#  ------------------------------------------------------------
#  Copyright (c) 2024 Rystal-Team
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#  ------------------------------------------------------------
#

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
    "rank": "CREATE TABLE rank (user_id VARCHAR(24) PRIMARY KEY, data JSON, total_xp INT(255))",
    "note": "CREATE TABLE note (user_id VARCHAR(24) PRIMARY KEY, notes JSON)",
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


def check_exists(table, key, value):
    statement = f"SELECT {key} FROM {table} WHERE {key} = %s"
    values = (value,)
    cursor.execute(statement, values)
    result = cursor.fetchall()

    return not len(result) == 0
