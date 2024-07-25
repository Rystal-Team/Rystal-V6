import json

from termcolor import colored

from .main_handler import check_exists, db_handler

default_user_data = {"xp": 0, "totalxp": 0, "level": 0}


async def register_user(user_id: int):
    """
    Registers a new user in the database with default data.

    Args:
        user_id (int): The ID of the user to be registered.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        statement = {
            "sqlite": "INSERT INTO rank (user_id, data, total_xp) VALUES (?, ?, ?)",
            "mysql": "INSERT INTO rank (user_id, data, total_xp) VALUES (%s, %s, %s)",
        }
        db_handler.execute(statement, (str(user_id), json.dumps(default_user_data), 0))
        print(colored(f"[RANK DATABASE] Registered User: {user_id}", "light_yellow"))
    except Exception as e:
        print(
            colored(f"[RANK DATABASE] Failed to Register User: {user_id} - {e}", "red")
        )


async def update_total_xp(user_id, total_xp):
    """
    Updates the total XP of a user in the database.

    Args:
        user_id (int): The ID of the user.
        total_xp (int): The new total XP to set for the user.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    statement = {
        "sqlite": "UPDATE rank SET total_xp = ? WHERE user_id = ?",
        "mysql": "UPDATE rank SET total_xp = %s WHERE user_id = %s",
    }
    db_handler.execute(statement, (total_xp, str(user_id)))


async def update_user_data(user_id: int, data):
    """
    Updates the user data in the database.

    Args:
        user_id (int): The ID of the user.
        data (dict): The new data to set for the user.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("rank", "user_id", user_id):
        await register_user(user_id)
    statement = {
        "sqlite": "UPDATE rank SET data = ? WHERE user_id = ?",
        "mysql": "UPDATE rank SET data = %s WHERE user_id = %s",
    }
    db_handler.execute(statement, (json.dumps(data), str(user_id)))
    await update_total_xp(user_id, data["totalxp"])


async def get_user_data(user_id: int):
    """
    Retrieves the user data from the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: The user data.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("rank", "user_id", user_id):
        await register_user(user_id)
    statement = {
        "sqlite": "SELECT data FROM rank WHERE user_id = ?",
        "mysql": "SELECT data FROM rank WHERE user_id = %s",
    }
    db_handler.execute(statement, (user_id,))
    return json.loads(db_handler.fetchall()[0][0])


async def get_leaderboard(limit):
    """
    Retrieves the leaderboard from the database.

    Args:
        limit (int): The number of top users to retrieve.

    Returns:
        list: A list of users sorted by total XP in descending order.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    statement = {
        "sqlite": "SELECT * FROM rank ORDER BY total_xp DESC LIMIT ?",
        "mysql": "SELECT * FROM rank ORDER BY total_xp DESC LIMIT %s",
    }
    db_handler.execute(statement, (limit,))
    return db_handler.fetchall()
