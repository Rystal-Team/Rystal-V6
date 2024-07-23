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

import mysql.connector
from mysql.connector import Error

from . import LogHandler
from .utils import generate_secret


class Database:
    """
    A class to handle database operations for the jukebox application.

    Attributes:
        db_type (str): The type of database ('sqlite' or 'mysql').
        connection: The database connection object.
        cursor: The database cursor object.
    """

    def __init__(self, db_type, **kwargs):
        """
        Initializes the Database instance and connects to the specified database.

        Args:
            db_type (str): The type of database ('sqlite' or 'mysql').
            **kwargs: Additional arguments for database connection.
        """
        self.db_type = db_type
        self.connection = None
        self.cursor = None
        if db_type == "sqlite":
            self._connect_sqlite(**kwargs)
        elif db_type == "mysql":
            self._connect_mysql(**kwargs)
        else:
            raise ValueError("Unsupported database type. Choose 'sqlite' or 'mysql'.")

    def _connect_sqlite(self, db_file):
        """
        Connects to a SQLite database and creates necessary tables.

        Args:
            db_file (str): The SQLite database file path.
        """
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite: {e}")

    def _connect_mysql(self, host, user, password, database, port=3306):
        """
        Connects to a MySQL database and creates necessary tables.

        Args:
            host (str): The MySQL server host.
            user (str): The MySQL user.
            password (str): The MySQL user's password.
            database (str): The MySQL database name.
            port (int, optional): The MySQL server port. Defaults to 3306.
        """
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database, port=port
            )
            self.cursor = self.connection.cursor()
            self.create_tables()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def create_tables(self):
        """Creates necessary tables in the database."""
        queries = {
            "sqlite": [
                "CREATE TABLE IF NOT EXISTS jukebox_secrets (user_id TEXT PRIMARY KEY, secret TEXT);",
                "CREATE TABLE IF NOT EXISTS jukebox_ytcache (video_id TEXT PRIMARY KEY, metadata TEXT, registered_date TEXT);",
                "CREATE TABLE IF NOT EXISTS jukebox_replay_history (user_id TEXT, played_at TEXT, song TEXT, FOREIGN KEY (user_id) REFERENCES jukebox_secrets (user_id));",
            ],
            "mysql": [
                "CREATE TABLE IF NOT EXISTS jukebox_secrets (user_id VARCHAR(255) PRIMARY KEY, secret TEXT);",
                "CREATE TABLE IF NOT EXISTS jukebox_ytcache (video_id VARCHAR(255) PRIMARY KEY, metadata TEXT, registered_date VARCHAR(255));",
                "CREATE TABLE IF NOT EXISTS jukebox_replay_history (user_id VARCHAR(255), played_at VARCHAR(255), song TEXT, FOREIGN KEY (user_id) REFERENCES jukebox_secrets (user_id));",
            ],
        }
        for query in queries[self.db_type]:
            self.cursor.execute(query)
        self.connection.commit()

    async def register(self, user_id: str) -> str:
        """
        Registers a user by generating a secret and storing it in the database.

        Args:
            user_id (str): The user ID.

        Returns:
            str: The generated secret.
        """
        secret = await generate_secret()
        try:
            user_id = str(user_id)
            query = {
                "sqlite": "INSERT INTO jukebox_secrets (user_id, secret) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET secret=excluded.secret;",
                "mysql": "INSERT INTO jukebox_secrets (user_id, secret) VALUES (%s, %s) ON DUPLICATE KEY UPDATE secret=VALUES(secret);",
            }
            self.cursor.execute(query[self.db_type], (user_id, secret))
            self.connection.commit()
            LogHandler.info(f"Registered user: {user_id}")
        except Exception as e:
            LogHandler.error(f"Error registering user: {e}")
            raise e
        return secret

    async def user_exists(self, user_id: str) -> bool:
        """
        Checks if a user exists in the database.

        Args:
            user_id (str): The user ID.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        try:
            query = {
                "sqlite": "SELECT EXISTS(SELECT 1 FROM jukebox_secrets WHERE user_id = ?)",
                "mysql": "SELECT EXISTS(SELECT 1 FROM jukebox_secrets WHERE user_id = %s)",
            }
            self.cursor.execute(query[self.db_type], (user_id,))
            return self.cursor.fetchone()[0] == 1
        except Exception as e:
            LogHandler.error(f"Error checking if user exists: {e}")
            return False

    async def get_user_secret(self, user_id: str) -> str | None:
        """
        Retrieves the secret for a given user ID.

        Args:
            user_id (str): The user ID.

        Returns:
            str | None: The user's secret if found, None otherwise.
        """
        try:
            query = {
                "sqlite": "SELECT secret FROM jukebox_secrets WHERE user_id = ?",
                "mysql": "SELECT secret FROM jukebox_secrets WHERE user_id = %s",
            }
            self.cursor.execute(query[self.db_type], (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            LogHandler.error(f"Error fetching user secret: {e}")
            raise e

    def cache_video_metadata(self, video_id: str, metadata: dict):
        """
        Caches video metadata in the database.

        Args:
            video_id (str): The video ID.
            metadata (dict): The metadata to cache.
        """
        try:
            metadata_json = json.dumps(metadata)
            registered_date = datetime.now().isoformat()
            query = {
                "sqlite": "INSERT INTO jukebox_ytcache (video_id, metadata, registered_date) VALUES (?, ?, ?) ON CONFLICT(video_id) DO UPDATE SET metadata=excluded.metadata, registered_date=excluded.registered_date;",
                "mysql": "INSERT INTO jukebox_ytcache (video_id, metadata, registered_date) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE metadata=VALUES(metadata), registered_date=VALUES(registered_date);",
            }
            self.cursor.execute(
                query[self.db_type], (video_id, metadata_json, registered_date)
            )
            self.connection.commit()
            LogHandler.info(f"Cached video metadata for {video_id}")
        except Exception as e:
            LogHandler.error(f"Error caching video metadata: {e}")
            raise e

    def get_cached_video_metadata(self, video_id: str) -> None | dict:
        """
        Retrieves cached video metadata from the database.

        Args:
            video_id (str): The video ID.

        Returns:
            None | dict: The cached metadata if found, None otherwise.
        """
        try:
            query = {
                "sqlite": "SELECT metadata FROM jukebox_ytcache WHERE video_id = ?",
                "mysql": "SELECT metadata FROM jukebox_ytcache WHERE video_id = %s",
            }
            self.cursor.execute(query[self.db_type], (video_id,))
            result = self.cursor.fetchone()
            if result:
                LogHandler.info(f"Using cached video metadata for {video_id}")
                return json.loads(result[0])
            return None
        except Exception as e:
            LogHandler.error(f"Error fetching cached video metadata: {e}")
            raise e

    def get_bulk_video_metadata(self, video_ids: list) -> dict:
        """
        Retrieves metadata for multiple videos from the cache.

        Args:
            video_ids (list): A list of video IDs.

        Returns:
            dict: A dictionary with video IDs as keys and metadata as values.
        """
        video_ids_tuple = tuple(video_ids)
        metadata_dict = {}
        try:
            placeholders = ",".join(
                ["?" if self.db_type == "sqlite" else "%s"] * len(video_ids)
            )
            query = f"SELECT video_id, metadata FROM jukebox_ytcache WHERE video_id IN ({placeholders})"
            self.cursor.execute(query, video_ids_tuple)
            results = self.cursor.fetchall()
            for video_id, metadata_json in results:
                metadata_dict[video_id] = json.loads(metadata_json)
        except Exception as e:
            LogHandler.error(f"Error fetching bulk video metadata: {e}")
            raise e
        return metadata_dict

    async def add_replay_entry(self, user_id: str, played_at: str, song: str):
        """
        Adds a replay entry to the database.

        Args:
            user_id (str): The user ID.
            played_at (str): The timestamp when the song was played.
            song (str): The song that was played.
        """
        if not await self.user_exists(user_id):
            await self.register(user_id)
        try:
            query = {
                "sqlite": "INSERT INTO jukebox_replay_history (user_id, played_at, song) VALUES (?, ?, ?)",
                "mysql": "INSERT INTO jukebox_replay_history (user_id, played_at, song) VALUES (%s, %s, %s)",
            }
            self.cursor.execute(query[self.db_type], (user_id, played_at, song))
            self.connection.commit()
            LogHandler.info(f"Added replay entry for {user_id}")
        except Exception as e:
            LogHandler.error(f"Error adding replay entry: {e}")
            raise e

    async def get_replay_history(self, user_id: str, cutoff: int = 30) -> list:
        """
        Retrieves the replay history for a user within a specified cutoff period.

        Args:
            user_id (str): The user ID.
            cutoff (int, optional): The number of days to look back. Defaults to 30.

        Returns:
            list: A list of dictionaries containing replay history.
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=cutoff)).isoformat()
            query = {
                "sqlite": "SELECT played_at, song FROM jukebox_replay_history WHERE user_id = ? and played_at >= ? ORDER BY played_at DESC",
                "mysql": "SELECT played_at, song FROM jukebox_replay_history WHERE user_id = %s and played_at >= %s ORDER BY played_at DESC",
            }
            self.cursor.execute(query[self.db_type], (user_id, cutoff_date))
            results = self.cursor.fetchall()
            return [{"played_at": result[0], "song": result[1]} for result in results]
        except Exception as e:
            LogHandler.error(f"Error fetching replay history: {e}")
            raise e

    def clear_old_cache(self):
        """Clears old cached video metadata from the database."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=28)).isoformat()
            query = {
                "sqlite": "DELETE FROM jukebox_ytcache WHERE registered_date < ?",
                "mysql": "DELETE FROM jukebox_ytcache WHERE registered_date < %s",
            }
            self.cursor.execute(query[self.db_type], (cutoff_date,))
            self.connection.commit()
        except Exception as e:
            LogHandler.error(f"Error clearing old cache: {e}")
            raise e

    def run_cleanup(self):
        """Clears old cached video metadata from the database and logs the action."""
        self.clear_old_cache()
        LogHandler.info("Old cache entries cleared.")

    def close(self):
        """Closes the database cursor and connection if they are open."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
