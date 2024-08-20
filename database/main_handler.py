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
<<<<<<< Updated upstream
    "guild": "CREATE TABLE guild (guild_id VARCHAR(24) PRIMARY KEY, language VARCHAR(255), settings JSON)",
    "rank" : "CREATE TABLE rank (user_id VARCHAR(24) PRIMARY KEY, data JSON, total_xp INT(255))",
    "note" : "CREATE TABLE note (user_id VARCHAR(24) PRIMARY KEY, notes JSON)",
=======
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
                    jackpot_announce_channel INTEGER
                )
            """,
            "columns": {
                "guild_id": "TEXT PRIMARY KEY",
                "language": "TEXT",
                "music_silent_mode": "BOOLEAN",
                "music_auto_leave": "BOOLEAN",
                "music_default_loop_mode": "INTEGER",
                "jackpot_total": "INTEGER",
                "jackpot_announce_channel": "INTEGER",
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
                    jackpot_announce_channel INT
                )
            """,
            "columns": {
                "guild_id": "TEXT PRIMARY KEY",
                "language": "TEXT",
                "music_silent_mode": "BOOLEAN",
                "music_auto_leave": "BOOLEAN",
                "music_default_loop_mode": "INT",
                "jackpot_total": "INT",
                "jackpot_announce_channel": "INT",
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
>>>>>>> Stashed changes
}
existing_tables = []

<<<<<<< Updated upstream
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
=======

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
>>>>>>> Stashed changes


def check_exists(table, key, value):
    statement = f"SELECT {key} FROM {table} WHERE {key} = %s"
    values = (value,)
    cursor.execute(statement, values)
    result = cursor.fetchall()

    return not (len(result) == 0)
