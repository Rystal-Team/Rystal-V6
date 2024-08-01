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

from .main_handler import db_handler


async def save_session(thread_id, game, data, players):
    query = {
        "sqlite": "INSERT INTO game_sessions (thread_id, game, data, players) VALUES (?, ?, ?, ?)",
        "mysql": "INSERT INTO game_sessions (thread_id, game, data, players) VALUES (%s, %s, %s, %s)",
    }
    db_handler.execute(
        query[db_handler.db_type],
        (thread_id, game, json.dumps(data), json.dumps(players)),
    )
    db_handler.commit()
    return


def load_session(thread_id):
    query = {
        "sqlite": "SELECT game, data, players FROM game_sessions WHERE thread_id = ?",
        "mysql": "SELECT game, data, players FROM game_sessions WHERE thread_id = %s",
    }
    db_handler.execute(query[db_handler.db_type], (thread_id,))
    return db_handler.fetchone()


def delete_session(thread_id):
    query = {
        "sqlite": "DELETE FROM game_sessions WHERE thread_id = ?",
        "mysql": "DELETE FROM game_sessions WHERE thread_id = %s",
    }
    db_handler.execute(query[db_handler.db_type], (thread_id,))
    db_handler.connection.commit()
