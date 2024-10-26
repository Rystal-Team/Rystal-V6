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
import random
import string

from termcolor import colored

from .main_handler import check_exists, db_handler

default_user_data = {}


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
            "sqlite": "INSERT INTO note (user_id, notes) VALUES (?, ?)",
            "mysql" : "INSERT INTO note (user_id, notes) VALUES (%s, %s)",
        }
        db_handler.execute(statement, (str(user_id), json.dumps(default_user_data)))
        print(colored(f"[NOTE DATABASE] Registered User: {user_id}", "light_yellow"))
    except Exception as e:
        print(
            colored(f"[NOTE DATABASE] Failed to Register User: {user_id} - {e}", "red")
        )


async def add_note(user_id: int, note_content: str):
    """
    Adds a note for a user in the database.

    Args:
        user_id (int): The ID of the user.
        note_content (str): The content of the note to be added.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    note_id = random.choice(string.ascii_letters) + "".join(
        random.choices("0123456789", k=7)
    )
    try:
        if not check_exists("note", "user_id", user_id):
            await register_user(user_id)
        fetch_statement = {
            "sqlite": "SELECT notes FROM note WHERE user_id = ?",
            "mysql" : "SELECT notes FROM note WHERE user_id = %s",
        }
        db_handler.execute(fetch_statement, (str(user_id),))
        notes = json.loads(db_handler.fetchone()[0] or "{}")
        notes[note_id] = note_content
        update_statement = {
            "sqlite": "UPDATE note SET notes = ? WHERE user_id = ?",
            "mysql" : "UPDATE note SET notes = %s WHERE user_id = %s",
        }
        db_handler.execute(update_statement, (json.dumps(notes), str(user_id)))
        print(
            colored(f"[NOTE DATABASE] Note added for User: {user_id}", "light_yellow")
        )
    except Exception as e:
        print(
            colored(
                f"[NOTE DATABASE] Failed to add note for User: {user_id} - {e}", "red"
            )
        )


async def get_notes(user_id: int):
    """
    Retrieves all notes for a user from the database.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict: A dictionary of notes for the user, or an empty dictionary if no notes are found.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        if not check_exists("note", "user_id", user_id):
            await register_user(user_id)
        statement = {
            "sqlite": "SELECT notes FROM note WHERE user_id = ?",
            "mysql" : "SELECT notes FROM note WHERE user_id = %s",
        }
        db_handler.execute(statement, (str(user_id),))
        result = db_handler.fetchone()
        if result:
            return json.loads(result[0])
        print(colored(f"[NOTE DATABASE] No notes found for User: {user_id}", "yellow"))
        return {}
    except Exception as e:
        print(
            colored(
                f"[NOTE DATABASE] Failed to retrieve notes for User: {user_id} - {e}",
                "red",
            )
        )
        return {}


async def fetch_note(user_id: int, note_id: str) -> str | None:
    """
    Fetches a specific note for a user from the database.

    Args:
        user_id (int): The ID of the user.
        note_id (str): The ID of the note to be fetched.

    Returns:
        dict: The content of the note if found, otherwise an appropriate message.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        if not check_exists("note", "user_id", user_id):
            await register_user(user_id)

        statement = {
            "sqlite": "SELECT notes FROM note WHERE user_id = ?",
            "mysql" : "SELECT notes FROM note WHERE user_id = %s",
        }
        db_handler.execute(statement, (str(user_id),))
        result = db_handler.fetchone()
        if result:
            notes = json.loads(result[0])
            if note_id in notes:
                return notes[note_id]
            return None
        return None
    except Exception as e:
        print(
            colored(
                f"[NOTE DATABASE] Failed to fetch note for User: {user_id} - {e}",
                "red",
            )
        )
        raise e


async def update_note_state(user_id: int, note_id: str, new_state: int):
    """
    Updates the state of a specific note for a user in the database.

    Args:
        user_id (int): The ID of the user.
        note_id (str): The ID of the note to be updated.
        new_state (int): The new state of the note.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        if not check_exists("note", "user_id", user_id):
            await register_user(user_id)

        statement = {
            "sqlite": "SELECT notes FROM note WHERE user_id = ?",
            "mysql" : "SELECT notes FROM note WHERE user_id = %s",
        }
        db_handler.execute(statement, (str(user_id),))
        result = db_handler.fetchone()
        if result:
            notes = json.loads(result[0])
            if note_id in notes:
                note_content = json.loads(notes[note_id])
                note_content["state"] = new_state
                notes[note_id] = json.dumps(note_content)
                update_statement = {
                    "sqlite": "UPDATE note SET notes = ? WHERE user_id = ?",
                    "mysql" : "UPDATE note SET notes = %s WHERE user_id = %s",
                }
                db_handler.execute(update_statement, (json.dumps(notes), str(user_id)))
    except Exception as e:
        print(
            colored(
                f"[NOTE DATABASE] Failed to update note state for User: {user_id} - {e}",
                "red",
            )
        )
        raise e


async def remove_note(user_id: int, note_id: str) -> bool:
    """
    Removes a specific note for a user from the database.

    Args:
        user_id (int): The ID of the user.
        note_id (str): The ID of the note to be removed.

    Returns:
        bool: True if the note was removed, False if the note was not found.
    """
    if db_handler.db_type == "mysql":
        db_handler.connection.ping(reconnect=True, attempts=3)
    try:
        if not check_exists("note", "user_id", user_id):
            await register_user(user_id)

        statement = {
            "sqlite": "SELECT notes FROM note WHERE user_id = ?",
            "mysql" : "SELECT notes FROM note WHERE user_id = %s",
        }
        db_handler.execute(statement, (str(user_id),))
        result = db_handler.fetchone()
        if result:
            notes = json.loads(result[0])
            if note_id in notes:
                del notes[note_id]
                update_statement = {
                    "sqlite": "UPDATE note SET notes = ? WHERE user_id = ?",
                    "mysql" : "UPDATE note SET notes = %s WHERE user_id = %s",
                }
                db_handler.execute(update_statement, (json.dumps(notes), str(user_id)))
                return True
        return False
    except Exception as e:
        print(
            colored(
                f"[NOTE DATABASE] Failed to remove note for User: {user_id} - {e}",
                "red",
            )
        )
        raise e
