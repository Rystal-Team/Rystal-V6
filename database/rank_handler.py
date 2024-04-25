import json

from termcolor import colored

from .main_handler import check_exists, cursor, database

default_user_data = {
    "xp": 0,
    "totalxp": 0,
    "level": 0,
}


def register_user(user_id: int):
    database.ping(reconnect=True, attempts=3)

    try:
        statement = "INSERT INTO rank (user_id, data, total_xp) VALUES (%s, %s, %s)"
        values = (str(user_id), json.dumps(default_user_data), 0)

        cursor.execute(statement, values)
        database.commit()

        print(
            colored(text=f"[DATABASE] Registered User: {user_id}", color="light_yellow")
        )
    except Exception as e:
        print(
            colored(
                text=f"[DATABASE] Failed to Registered User: {user_id}", color="red"
            )
        )


def update_total_xp(user_id, total_xp):
    database.ping(reconnect=True, attempts=3)
    statement = "UPDATE rank SET total_xp = %s WHERE user_id = %s"
    values = (total_xp, str(user_id))
    cursor.execute(statement, values)
    database.commit()


def update_user_data(user_id: int, data):
    database.ping(reconnect=True, attempts=3)
    user_exists = check_exists("rank", "user_id", user_id)

    if not user_exists:
        register_user(user_id)

    statement = "UPDATE rank SET data = %s WHERE user_id = %s"
    values = (json.dumps(data), str(user_id))
    cursor.execute(statement, values)
    database.commit()

    update_total_xp(user_id, data["totalxp"])

    return


def get_user_data(user_id: int):
    database.ping(reconnect=True, attempts=3)
    user_exists = check_exists("rank", "user_id", user_id)

    if not user_exists:
        register_user(user_id)

    statement = "SELECT data FROM rank WHERE user_id = %s"
    values = (user_id,)
    cursor.execute(statement, values)

    result = cursor.fetchall()

    data = json.loads(result[0][0])

    return data


def get_leaderboard(limit):
    statement = "SELECT * FROM rank ORDER BY total_xp DESC LIMIT %s"
    values = (limit,)
    cursor.execute(statement, values)
    result = cursor.fetchall()
    print(result)
