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

import datetime

from termcolor import colored

from .main_handler import check_exists, db_handler


async def register_user(user_id: int):
    """
    Registers a new user in the database.

    Args:
        user_id (int): The ID of the user to register.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        statement = {
            "sqlite": "INSERT INTO users (user_id, level, xp, total_xp, points, last_point_claimed) VALUES (?, ?, ?, ?, ?, ?)",
            "mysql": "INSERT INTO users (user_id, level, xp, total_xp, points, last_point_claimed) VALUES (%s, %s, %s, %s, %s, %s)",
        }
        db_handler.execute(statement, (str(user_id), 0, 0, 0, 0, datetime.datetime.min))
        print(colored(f"[USERS DATABASE] Registered User: {user_id}", "light_yellow"))
    except Exception as e:
        print(
            colored(f"[USERS DATABASE] Failed to Register User: {user_id} - {e}", "red")
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
        "sqlite": "UPDATE users SET total_xp = ? WHERE user_id = ?",
        "mysql": "UPDATE users SET total_xp = %s WHERE user_id = %s",
    }
    db_handler.execute(statement, (total_xp, str(user_id)))


async def update_user_data(user_id: int, data):
    """
    Updates the user data in the database.

    Args:
        user_id (int): The ID of the user.
        data (dict): A dictionary containing the user data to update.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("users", "user_id", user_id):
        await register_user(user_id)

    data["points"] = round(data["points"])

    statement = {
        "sqlite": "UPDATE users SET level = ?, xp = ?, total_xp = ?, points = ?, last_point_claimed = ? WHERE user_id = ?",
        "mysql": "UPDATE users SET level = %s, xp = %s, total_xp = %s, points = %s, last_point_claimed = %s WHERE user_id = %s",
    }
    db_handler.execute(
        statement,
        (
            data["level"],
            data["xp"],
            data["totalxp"],
            data["points"],
            data["last_point_claimed"],
            str(user_id),
        ),
    )


async def get_user_data(user_id: int):
    """
    Retrieves the user data from the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: A dictionary containing the user data.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("users", "user_id", user_id):
        await register_user(user_id)
    statement = {
        "sqlite": "SELECT level, xp, total_xp, points, last_point_claimed FROM users WHERE user_id = ?",
        "mysql": "SELECT level, xp, total_xp, points, last_point_claimed FROM users WHERE user_id = %s",
    }
    db_handler.execute(statement, (user_id,))
    result = db_handler.fetchall()[0]
    return {
        "level": result[0],
        "xp": result[1],
        "totalxp": result[2],
        "points": result[3],
        "last_point_claimed": result[4],
    }


async def get_leaderboard(limit, order_by):
    """
    Retrieves the leaderboard from the database.

    Args:
        order_by: The column to order the leaderboard by.
        limit (int): The number of top users to retrieve.

    Returns:
        dict: A dictionary with user_id as key and their level, xp, and total_xp as values.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    statement = {
        "sqlite": f"SELECT user_id, level, xp, total_xp, points FROM users ORDER BY {order_by} DESC LIMIT ?",
        "mysql": f"SELECT user_id, level, xp, total_xp, points FROM users ORDER BY {order_by} DESC LIMIT %s",
    }
    db_handler.execute(
        statement,
        (limit,),
    )
    result = db_handler.fetchall()

    leaderboard = {
        user[0]: {
            "level": user[1],
            "xp": user[2],
            "totalxp": user[3],
            "points": user[4],
        }
        for user in result
    }

    return leaderboard
