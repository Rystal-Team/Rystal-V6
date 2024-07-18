

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
import sqlite3
from datetime import datetime, timedelta

from . import LogHandler
from .utils import generate_secret


class Database:
    """
    Manages database connections and operations for user secrets and video metadata caching.

    Attributes:
        db_path (str): The path to the SQLite database file.
        connection (sqlite3.Connection): The SQLite database connection.
        cursor (sqlite3.Cursor): The SQLite database cursor.
    """

    def __init__(self, db_path: str = "./database/user.db"):
        """
        Initializes the Database instance with the specified database path.

        Args:
            db_path (str): The path to the SQLite database file. Defaults to "./database/user.db".
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connects to the SQLite database and creates the required tables."""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def close(self):
        """Closes the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def create_tables(self):
        """
        Creates the 'secrets', 'ytcache', and 'replay_history' tables if they do not exist.
        """
        queries = [
            """
            CREATE TABLE IF NOT EXISTS secrets (
                user_id TEXT PRIMARY KEY,
                secret TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS ytcache (
                video_id TEXT PRIMARY KEY,
                metadata TEXT,
                registered_date TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS replay_history (
                user_id TEXT,
                played_at TEXT,
                song TEXT,
                FOREIGN KEY (user_id) REFERENCES secrets (user_id)
            );
            """
        ]
        for query in queries:
            self.cursor.execute(query)
        self.connection.commit()

    async def register(self, user_id: str) -> str:
        """
        Registers a user by generating and storing a secret.

        Args:
            user_id (str): The ID of the user to register.

        Returns:
            str: The generated secret for the user.
        """
        secret = await generate_secret()
        try:
            user_id = str(user_id)
            query = """
            INSERT INTO secrets (user_id, secret)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET secret=excluded.secret;
            """
            self.cursor.execute(query, (user_id, secret))
            self.connection.commit()
        except sqlite3.Error as e:
            LogHandler.error(f"Error registering user: {e}")
            raise e
        return secret

    async def get_user_secret(self, user_id: str) -> str | None:
        """
        Retrieves the secret for a specified user.

        Args:
            user_id (str): The ID of the user whose secret is to be retrieved.

        Returns:
            str: The secret of the user, or None if the user is not found.
        """
        try:
            query = "SELECT secret FROM secrets WHERE user_id = ?"
            self.cursor.execute(query, (user_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return None
        except sqlite3.Error as e:
            LogHandler.error(f"Error fetching user secret: {e}")
            raise e

    def cache_video_metadata(self, video_id: str, metadata: dict):
        """
        Caches metadata for a specified video.

        Args:
            video_id (str): The ID of the video.
            metadata (dict): The metadata to be cached.
        """
        try:
            metadata_json = json.dumps(metadata)
            registered_date = datetime.now().isoformat()
            query = """
            INSERT INTO ytcache (video_id, metadata, registered_date)
            VALUES (?, ?, ?)
            ON CONFLICT(video_id) DO UPDATE SET metadata=excluded.metadata, registered_date=excluded.registered_date;
            """
            self.cursor.execute(query, (video_id, metadata_json, registered_date))
            self.connection.commit()
            LogHandler.info(f"Cached video metadata for {video_id}")
        except sqlite3.Error as e:
            LogHandler.error(f"Error caching video metadata: {e}")
            raise e

    def get_cached_video_metadata(self, video_id: str) -> None | dict:
        """
        Retrieves cached metadata for a specified video.

        Args:
            video_id (str): The ID of the video.

        Returns:
            dict: The cached metadata, or None if the video is not found.
        """
        try:
            query = "SELECT metadata FROM ytcache WHERE video_id = ?"
            self.cursor.execute(query, (video_id,))
            result = self.cursor.fetchone()
            if result:
                LogHandler.info(f"Using cached video metadata for {video_id}")
                return json.loads(result[0])
            return None
        except sqlite3.Error as e:
            LogHandler.error(f"Error fetching cached video metadata: {e}")
            raise e

    async def add_replay_entry(self, user_id: str, played_at: str, song: str):
        """
        Adds an entry to the replay history for a user.

        Args:
            user_id (str): The ID of the user.
            played_at (str): The timestamp when the song was played.
            song (str): The name of the song.
        """
        try:
            query = """
            INSERT INTO replay_history (user_id, played_at, song)
            VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (user_id, played_at, song))
            self.connection.commit()
            LogHandler.info(f"Added replay entry for {user_id}")
        except sqlite3.Error as e:
            LogHandler.error(f"Error adding replay entry: {e}")
            raise e

    async def get_replay_history(self, user_id: str, cutoff: int = 30) -> list:
        """
        Retrieves the replay history for a specified user.

        Args:
            user_id (str): The ID of the user whose replay history is to be retrieved.

        Returns:
            list: A list of dictionaries representing replay entries [{played_at: str, song: str}, ...].
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=cutoff)).isoformat()
            query = "SELECT played_at, song FROM replay_history WHERE user_id = ? and played_at >= ? ORDER BY played_at DESC"
            self.cursor.execute(query, (user_id, cutoff_date,))
            results = self.cursor.fetchall()
            history = []
            for result in results:
                history.append({
                    'played_at': result[0],
                    'song'     : result[1]
                })
            return history
        except sqlite3.Error as e:
            LogHandler.error(f"Error fetching replay history: {e}")
            raise e

    def clear_old_cache(self):
        """Clears cached entries older than 28 days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=28)).isoformat()
            query = "DELETE FROM ytcache WHERE registered_date < ?"
            self.cursor.execute(query, (cutoff_date,))
            self.connection.commit()
        except sqlite3.Error as e:
            LogHandler.error(f"Error clearing old ytcache: {e}")
            raise e

    # TODO: この関数をスケジューラにフックしてください！！
    def run_cleanup(self):
        """Runs the cleanup process to clear old ytcache entries."""
        self.clear_old_cache()
        LogHandler.info("Old ytcache entries cleared.")
