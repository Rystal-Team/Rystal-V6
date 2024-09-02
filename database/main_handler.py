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

from config.loader import SQLITE_PATH, USE_SQLITE
from .base import DatabaseHandler

create_statements = {
    "sqlite": {
        "note": {
            "create": "CREATE TABLE IF NOT EXISTS note (user_id TEXT PRIMARY KEY, notes TEXT)",
            "columns": {"user_id": "TEXT PRIMARY KEY", "notes": "TEXT"},
        },
        "users": {
            "create": "CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, level INTEGER, xp INTEGER, total_xp INTEGER, points INTEGER, last_point_claimed TEXT)",
            "columns": {
                "user_id": "TEXT PRIMARY KEY",
                "level": "INTEGER",
                "xp": "INTEGER",
                "total_xp": "INTEGER",
                "points": "INTEGER",
                "last_point_claimed": "TEXT",
            },
        },
        "guild": {
            "create": """
                CREATE TABLE IF NOT EXISTS guild (
                    guild_id TEXT PRIMARY KEY,
                    language TEXT,
                    music_silent_mode BOOLEAN,
                    music_auto_leave BOOLEAN,
                    music_default_loop_mode INTEGER,
                    jackpot_total INTEGER,
                    game_announce_channel INTEGER
                )
            """,
            "columns": {
                "guild_id": "TEXT PRIMARY KEY",
                "language": "TEXT",
                "music_silent_mode": "BOOLEAN",
                "music_auto_leave": "BOOLEAN",
                "music_default_loop_mode": "INTEGER",
                "jackpot_total": "INTEGER",
                "game_announce_channel": "INTEGER",
            },
        },
        "game_sessions": {
            "create": "CREATE TABLE IF NOT EXISTS game_sessions (thread_id TEXT PRIMARY KEY, game TEXT, data TEXT, players TEXT)",
            "columns": {
                "thread_id": "TEXT PRIMARY KEY",
                "game": "TEXT",
                "data": "TEXT",
                "players": "TEXT",
            },
        },
        "global": {
            "create": """
                CREATE TABLE IF NOT EXISTS global (
                    jackpot_total INTEGER,
                    jackpot_next_invest TEXT
                )
            """,
            "columns": {
                "jackpot_total": "INTEGER",
                "jackpot_next_invest": "TEXT",
            },
        },
    },
    "mysql": {
        "note": {
            "create": "CREATE TABLE IF NOT EXISTS note (user_id VARCHAR(255) PRIMARY KEY, notes JSON)",
            "columns": {"user_id": "VARCHAR(255) PRIMARY KEY", "notes": "JSON"},
        },
        "users": {
            "create": "CREATE TABLE IF NOT EXISTS users (user_id VARCHAR(255) PRIMARY KEY, level INT, xp INT, total_xp INT, points INT, last_point_claimed DATETIME)",
            "columns": {
                "user_id": "VARCHAR(255) PRIMARY KEY",
                "level": "INT",
                "xp": "INT",
                "total_xp": "INT",
                "points": "INT",
                "last_point_claimed": "DATETIME",
            },
        },
        "guild": {
            "create": """
                CREATE TABLE IF NOT EXISTS guild (
                    guild_id TEXT PRIMARY KEY,
                    language TEXT,
                    music_silent_mode BOOLEAN,
                    music_auto_leave BOOLEAN,
                    music_default_loop_mode INT,
                    jackpot_total INT,
                    game_announce_channel INT
                )
            """,
            "columns": {
                "guild_id": "TEXT PRIMARY KEY",
                "language": "TEXT",
                "music_silent_mode": "BOOLEAN",
                "music_auto_leave": "BOOLEAN",
                "music_default_loop_mode": "INT",
                "jackpot_total": "INT",
                "game_announce_channel": "INT",
            },
        },
        "game_sessions": {
            "create": "CREATE TABLE IF NOT EXISTS game_sessions (thread_id TEXT PRIMARY KEY, game TEXT, data TEXT, players TEXT)",
            "columns": {
                "thread_id": "TEXT PRIMARY KEY",
                "game": "TEXT",
                "data": "TEXT",
                "players": "TEXT",
            },
        },
        "global": {
            "create": "CREATE TABLE IF NOT EXISTS global (jackpot_total INT, jackpot_next_invest TEXT)",
            "columns": {
                "jackpot_total": "INT",
                "jackpot_next_invest": "TEXT",
            },
        },
    },
}
existing_tables = []

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
