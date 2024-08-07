import json

from termcolor import colored

from config.config import default_language, multi_lang
from .main_handler import check_exists, cursor, database

default_guild_settings = {
    "music_silent_mode": False,
    "music_auto_leave" : True,
}


async def append_guild(guild_id: int):
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
                text=f"[GUILD DATABASE] Registered Guild: {guild_id}", color="light_yellow"
            )
        )
    except Exception as e:
        print(
            colored(
                text=f"[GUILD DATABASE] Failed to Registered Guild: {guild_id}", color="red"
            )
        )


async def change_guild_language(guild_id: int, language):
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

    return


async def get_guild_language(guild_id: int):
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
    else:
        return default_language


async def change_guild_settings(guild_id: int, key, value):
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

    return


async def get_guild_settings(guild_id: int, key):
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
