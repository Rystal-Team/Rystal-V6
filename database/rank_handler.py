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

from .main_handler import check_exists, cursor, database

default_user_data = {
    "xp"     : 0,
    "totalxp": 0,
    "level"  : 0,
}


async def register_user(user_id: int):
    database.ping(reconnect=True, attempts=3)
    try:
        statement = "INSERT INTO rank (user_id, data, total_xp) VALUES (%s, %s, %s)"
        values = (str(user_id), json.dumps(default_user_data), 0)
        cursor.execute(statement, values)
        database.commit()
        print(
            colored(text=f"[RANK DATABASE] Registered User: {user_id}", color="light_yellow")
        )
    except Exception as e:
        print(
            colored(
                text=f"[RANK DATABASE] Failed to Registered User: {user_id}", color="red"
            )
        )


async def update_total_xp(user_id, total_xp):
    database.ping(reconnect=True, attempts=3)
    statement = "UPDATE rank SET total_xp = %s WHERE user_id = %s"
    values = (total_xp, str(user_id))
    cursor.execute(statement, values)
    database.commit()


async def update_user_data(user_id: int, data):
    database.ping(reconnect=True, attempts=3)
    if not check_exists("rank", "user_id", user_id):
        await register_user(user_id)
    statement = "UPDATE rank SET data = %s WHERE user_id = %s"
    values = (json.dumps(data), str(user_id))
    cursor.execute(statement, values)
    database.commit()
    await update_total_xp(user_id, data["totalxp"])
    return


async def get_user_data(user_id: int):
    database.ping(reconnect=True, attempts=3)
    if not check_exists("rank", "user_id", user_id):
        await register_user(user_id)
    statement = "SELECT data FROM rank WHERE user_id = %s"
    values = (user_id,)
    cursor.execute(statement, values)
    result = cursor.fetchall()
    data = json.loads(result[0][0])
    return data


async def get_leaderboard(limit):
    statement = "SELECT * FROM rank ORDER BY total_xp DESC LIMIT %s"
    values = (limit,)
    cursor.execute(statement, values)
    result = cursor.fetchall()

    return result
