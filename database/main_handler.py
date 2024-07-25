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

from config.config import SQLITE_PATH, USE_SQLITE
from .base import DatabaseHandler

create_statements = {
    "sqlite": [
        "CREATE TABLE IF NOT EXISTS note (user_id TEXT PRIMARY KEY, notes TEXT)",
        "CREATE TABLE IF NOT EXISTS rank (user_id TEXT PRIMARY KEY, data TEXT, total_xp INTEGER)",
        "CREATE TABLE IF NOT EXISTS guild (guild_id TEXT PRIMARY KEY, language TEXT, settings TEXT)",
    ],
    "mysql": [
        "CREATE TABLE IF NOT EXISTS note (user_id VARCHAR(255) PRIMARY KEY, notes JSON)",
        "CREATE TABLE IF NOT EXISTS rank (user_id VARCHAR(255) PRIMARY KEY, data JSON, total_xp INT)",
        "CREATE TABLE IF NOT EXISTS guild (guild_id VARCHAR(255) PRIMARY KEY, language VARCHAR(255), settings JSON)",
    ],
}

if USE_SQLITE:
    db_handler = DatabaseHandler(
        db_type="sqlite", create_query=create_statements, db_file=SQLITE_PATH
    )
else:
    db_handler = DatabaseHandler(
        db_type="mysql",
        create_query=create_statements,
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def check_exists(table, key, value):
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    statement = {
        "sqlite": f"SELECT {key} FROM {table} WHERE {key} = ?",
        "mysql": f"SELECT {key} FROM {table} WHERE {key} = %s",
    }
    db_handler.execute(statement, (value,))
    return bool(db_handler.fetchall())
