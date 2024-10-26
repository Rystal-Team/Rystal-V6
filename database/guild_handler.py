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

from termcolor import colored

from config.loader import default_language, lang
from .main_handler import check_exists, db_handler


async def append_guild(guild_id: int):
    """
    Registers a new guild in the database with default settings.

    Args:
        guild_id (int): The ID of the guild to be registered.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        statement = {
            "sqlite": "INSERT INTO guild (guild_id, language, music_silent_mode, music_auto_leave, music_default_loop_mode) VALUES (?, ?, ?, ?, ?)",
            "mysql" : "INSERT INTO guild (guild_id, language, music_silent_mode, music_auto_leave, music_default_loop_mode) VALUES (%s, %s, %s, %s, %s)",
        }
        values = (str(guild_id), default_language, False, True, 1)
        db_handler.execute(statement, values)
        print(colored(f"Registered Guild: {guild_id}", "light_yellow"))
    except Exception:
        print(colored(f"Failed to Register Guild: {guild_id}", "red"))


async def get_jackpot_announcement_channels():
    """
    Retrieves all channel IDs where jackpot announcements are made.

    Returns:
        list: A list of channel IDs.
    """
    statement = {
        "sqlite": "SELECT game_announce_channel FROM guild WHERE game_announce_channel IS NOT NULL",
        "mysql" : "SELECT game_announce_channel FROM guild WHERE game_announce_channel IS NOT NULL",
    }
    db_handler.execute(statement)
    return [row[0] for row in (db_handler.fetchall() or [])]


async def change_guild_language(guild_id: int, language: str):
    """
    Updates the language setting for a specific guild.

    Args:
        guild_id (int): The ID of the guild.
        language (str): The new language setting.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("guild", "guild_id", guild_id):
        await append_guild(guild_id)
    statement = {
        "sqlite": "UPDATE guild SET language = ? WHERE guild_id = ?",
        "mysql" : "UPDATE guild SET language = %s WHERE guild_id = %s",
    }
    db_handler.execute(statement, (language, str(guild_id)))
    print(
        colored(f"Updated Guild {guild_id}'s Language to [{language}]", "light_yellow")
    )


async def get_guild_language(guild_id: int):
    """
    Retrieves the language setting for a specific guild.

    Args:
        guild_id (int): The ID of the guild.

    Returns:
        str: The language setting of the guild.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("guild", "guild_id", guild_id):
        await append_guild(guild_id)
    statement = {
        "sqlite": "SELECT language FROM guild WHERE guild_id = ?",
        "mysql" : "SELECT language FROM guild WHERE guild_id = %s",
    }
    db_handler.execute(statement, (guild_id,))
    guild_language = db_handler.fetchall()[0][0]
    if not guild_language:
        return default_language
    return default_language if guild_language not in lang else guild_language


async def change_guild_settings(guild_id: int | str, key, value):
    """
    Updates a specific setting for a guild.

    Args:
        guild_id (int): The ID of the guild.
        key (str): The setting key to be updated.
        value: The new value for the setting.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("guild", "guild_id", guild_id):
        await append_guild(guild_id)
    statement = {
        "sqlite": f"UPDATE guild SET {key} = ? WHERE guild_id = ?",
        "mysql" : f"UPDATE guild SET {key} = %s WHERE guild_id = %s",
    }
    db_handler.execute(statement, (value, str(guild_id)))
    print(
        colored(
            f"Updated Guild {guild_id}'s setting: {key} to [{value}]", "light_yellow"
        )
    )


async def get_guild_settings(guild_id: int | str, key):
    """
    Retrieves a specific setting for a guild.

    Args:
        guild_id (int): The ID of the guild.
        key (str): The setting key to be retrieved.

    Returns:
        The value of the specified setting.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("guild", "guild_id", guild_id):
        await append_guild(guild_id)
    statement = {
        "sqlite": f"SELECT {key} FROM guild WHERE guild_id = ?",
        "mysql" : f"SELECT {key} FROM guild WHERE guild_id = %s",
    }
    db_handler.execute(statement, (guild_id,))
    return db_handler.fetchall()[0][0]
