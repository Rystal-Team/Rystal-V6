

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
import uuid

from termcolor import colored

from .main_handler import check_exists, cursor, database

default_user_data = {}


async def register_user(user_id: int):
    database.ping(reconnect=True, attempts=3)
    try:
        statement = "INSERT INTO note (user_id, notes) VALUES (%s, %s)"
        values = (str(user_id), json.dumps(default_user_data))
        cursor.execute(statement, values)
        database.commit()
        print(
            colored(
                text=f"[NOTE DATABASE] Registered User: {user_id}", color="light_yellow"
            )
        )
    except Exception as e:
        print(
            colored(
                text=f"[NOTE DATABASE] Failed to Register User: {user_id} - {e}",
                color="red",
            )
        )


async def add_note(user_id: int, note_content: str):
    database.ping(reconnect=True, attempts=3)
    note_id = str(uuid.uuid4())
    try:
        if not check_exists("note", "user_id", user_id):
            await register_user(user_id)

        fetch_statement = "SELECT notes FROM note WHERE user_id = %s"
        cursor.execute(fetch_statement, (str(user_id),))
        result = cursor.fetchone()
        if result:
            notes = json.loads(result[0])
        else:
            notes = {}

        notes[note_id] = note_content

        update_statement = "UPDATE note SET notes = %s WHERE user_id = %s"
        cursor.execute(update_statement, (json.dumps(notes), str(user_id)))
        database.commit()

        print(colored(text=f"[NOTE DATABASE] Note added for User: {user_id}", color="light_yellow"))
    except Exception as e:
        print(colored(text=f"[NOTE DATABASE] Failed to add note for User: {user_id} - {e}", color="red"))


async def get_notes(user_id: int):
    database.ping(reconnect=True, attempts=3)
    try:
        if not check_exists("note", "user_id", user_id):
            await register_user(user_id)

        statement = "SELECT notes FROM note WHERE user_id = %s"
        cursor.execute(statement, (str(user_id),))
        result = cursor.fetchone()
        if result:
            notes = json.loads(result[0])
            return notes
        else:
            print(colored(text=f"[NOTE DATABASE] No notes found for User: {user_id}", color="yellow"))
            return {}
    except Exception as e:
        print(colored(text=f"[NOTE DATABASE] Failed to retrieve notes for User: {user_id} - {e}", color="red"))
        return {}
