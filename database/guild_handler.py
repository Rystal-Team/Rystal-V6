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
from .main_handler import check_exists, cursor, database

# Default settings for a guild
default_guild_settings = {
    "music_silent_mode": False,
    "music_auto_leave": True,
}


async def append_guild(guild_id: int):
    """
    Registers a new guild in the database with default settings.

    Args:
        guild_id (int): The ID of the guild to register.
    """
    database.ping(reconnect=True, attempts=3)

    try:
        statement = (
            "INSERT INTO guild (guild_id, language, settings) VALUES (%s, %s, %s)"
        )
        values = (str(guild_id), default_language, json.dumps(default_guild_settings))

        cursor.execute(statement, values)
        database.commit()

        print(
            colored(
                text=f"[GUILD DATABASE] Registered Guild: {guild_id}",
                color="light_yellow",
            )
        )
    except Exception as e:
        print(
            colored(
                text=f"[GUILD DATABASE] Failed to Registered Guild: {guild_id}",
                color="red",
            )
        )


async def change_guild_language(guild_id: int, language):
    """
    Changes the language setting for a guild.

    Args:
        guild_id (int): The ID of the guild.
        language (str): The new language to set for the guild.
    """
    database.ping(reconnect=True, attempts=3)
    guild_exists = check_exists("guild", "guild_id", guild_id)

    if not guild_exists:
        await append_guild(guild_id)

    statement = "UPDATE guild SET language = %s WHERE guild_id = %s"
    values = (language, str(guild_id))
    cursor.execute(statement, values)
    database.commit()

    print(
        colored(
            text=f"[GUILD DATABASE] Updated Guild {guild_id}'s Language to [{language}]",
            color="light_yellow",
        )
    )


async def get_guild_language(guild_id: int):
    """
    Retrieves the language setting for a guild.

    Args:
        guild_id (int): The ID of the guild.

    Returns:
        str: The language setting of the guild.
    """
    if multi_lang:
        database.ping(reconnect=True, attempts=3)
        guild_exists = check_exists("guild", "guild_id", guild_id)

        if not guild_exists:
            await append_guild(guild_id)

        statement = "SELECT language FROM guild WHERE guild_id = %s"
        values = (guild_id,)
        cursor.execute(statement, values)

        result = cursor.fetchall()

        guild_language = result[0][0]

        return guild_language
    return default_language


async def change_guild_settings(guild_id: int, key, value):
    """
    Changes a specific setting for a guild.

    Args:
        guild_id (int): The ID of the guild.
        key (str): The setting key to change.
        value (any): The new value for the setting.
    """
    database.ping(reconnect=True, attempts=3)
    guild_exists = check_exists("guild", "guild_id", guild_id)

    if not guild_exists:
        await append_guild(guild_id)

    statement = "SELECT settings FROM guild WHERE guild_id = %s"
    values = (guild_id,)
    cursor.execute(statement, values)

    result = cursor.fetchall()

    settings = json.loads(result[0][0])
    settings[key] = value

    statement = "UPDATE guild SET settings = %s WHERE guild_id = %s"
    values = (json.dumps(settings), str(guild_id))
    cursor.execute(statement, values)
    database.commit()

    print(
        colored(
            text=f"[GUILD DATABASE] Updated Guild {guild_id}'s setting: {key} to [{value}]",
            color="light_yellow",
        )
    )


async def get_guild_settings(guild_id: int, key):
    """
    Retrieves a specific setting for a guild.

    Args:
        guild_id (int): The ID of the guild.
        key (str): The setting key to retrieve.

    Returns:
        any: The value of the requested setting.
    """
    database.ping(reconnect=True, attempts=3)
    guild_exists = check_exists("guild", "guild_id", guild_id)

    if not guild_exists:
        await append_guild(guild_id)

    statement = "SELECT settings FROM guild WHERE guild_id = %s"
    values = (guild_id,)
    cursor.execute(statement, values)

    result = cursor.fetchall()

    settings = json.loads(result[0][0])

    return settings[key]
