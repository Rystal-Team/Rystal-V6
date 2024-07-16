import json

from termcolor import colored

from .main_handler import cursor, database

default_user_data = {}


async def register_user(user_id: int):
    database.ping(reconnect=True, attempts=3)
    try:
        statement = "INSERT INTO note (user_id, notes) VALUES (%s, %s, %s)"
        values = (str(user_id), json.dumps(default_user_data))
        cursor.execute(statement, values)
        database.commit()
        print(
            colored(
                text=f"[NOTE DATABASE] Registered User: {user_id}", color="light_yellow"
            )
        )
    except Exception:
        print(
            colored(
                text=f"[NOTE DATABASE] Failed to Registered User: {user_id}",
                color="red",
            )
        )


async def add_note():
    uuid = str(uuid.uuid4())

    return
