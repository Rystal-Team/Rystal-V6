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

import json

from termcolor import colored

from config.config import default_language, multi_lang
from .main_handler import check_exists, db_handler

default_guild_settings = {
    "music_silent_mode": False,
    "music_auto_leave": True,
}


async def append_guild(guild_id: int):
    """
    Registers a new guild in the database.

    Args:
        guild_id (int): The ID of the guild to register.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        statement = {
            "sqlite": "INSERT INTO guild (guild_id, language, settings) VALUES (?, ?, ?)",
            "mysql": "INSERT INTO guild (guild_id, language, settings) VALUES (%s, %s, %s)",
        }
        values = (str(guild_id), default_language, json.dumps(default_guild_settings))
        db_handler.execute(statement, values)
        print(colored(f"[GUILD DATABASE] Registered Guild: {guild_id}", "light_yellow"))
    except Exception:
        print(colored(f"[GUILD DATABASE] Failed to Register Guild: {guild_id}", "red"))


async def change_guild_language(guild_id: int, language):
    """
    Changes the language setting of a guild.

    Args:
        guild_id (int): The ID of the guild.
        language (str): The new language to set for the guild.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("guild", "guild_id", guild_id):
        await append_guild(guild_id)
    statement = {
        "sqlite": "UPDATE guild SET language = ? WHERE guild_id = ?",
        "mysql": "UPDATE guild SET language = %s WHERE guild_id = %s",
    }
    db_handler.execute(statement, (language, str(guild_id)))
    print(
        colored(
            f"[GUILD DATABASE] Updated Guild {guild_id}'s Language to [{language}]",
            "light_yellow",
        )
    )


async def get_guild_language(guild_id: int):
    """
    Retrieves the language setting of a guild.

    Args:
        guild_id (int): The ID of the guild.

    Returns:
        str: The language setting of the guild.
    """
    if multi_lang:
        if db_handler.db_type == "mysql":
            db_handler.connection.ping(reconnect=True, attempts=3)
        if not check_exists("guild", "guild_id", guild_id):
            await append_guild(guild_id)
        statement = {
            "sqlite": "SELECT language FROM guild WHERE guild_id = ?",
            "mysql": "SELECT language FROM guild WHERE guild_id = %s",
        }
        db_handler.execute(statement, (guild_id,))
        return db_handler.fetchall()[0][0]
    return default_language


async def change_guild_settings(guild_id: int, key, value):
    """
    Changes a specific setting of a guild.

    Args:
        guild_id (int): The ID of the guild.
        key (str): The setting key to change.
        value (any): The new value for the setting.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("guild", "guild_id", guild_id):
        await append_guild(guild_id)
    statement = {
        "sqlite": "SELECT settings FROM guild WHERE guild_id = ?",
        "mysql": "SELECT settings FROM guild WHERE guild_id = %s",
    }
    db_handler.execute(statement, (guild_id,))
    settings = json.loads(db_handler.fetchall()[0][0])
    settings[key] = value
    statement = {
        "sqlite": "UPDATE guild SET settings = ? WHERE guild_id = ?",
        "mysql": "UPDATE guild SET settings = %s WHERE guild_id = %s",
    }
    db_handler.execute(statement, (json.dumps(settings), str(guild_id)))
    print(
        colored(
            f"[GUILD DATABASE] Updated Guild {guild_id}'s setting: {key} to [{value}]",
            "light_yellow",
        )
    )


async def get_guild_settings(guild_id: int, key):
    """
    Retrieves a specific setting of a guild.

    Args:
        guild_id (int): The ID of the guild.
        key (str): The setting key to retrieve.

    Returns:
        any: The value of the requested setting.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    if not check_exists("guild", "guild_id", guild_id):
        await append_guild(guild_id)
    statement = {
        "sqlite": "SELECT settings FROM guild WHERE guild_id = ?",
        "mysql": "SELECT settings FROM guild WHERE guild_id = %s",
    }
    db_handler.execute(statement, (guild_id,))
    settings = json.loads(db_handler.fetchall()[0][0])
    return settings.get(key)
