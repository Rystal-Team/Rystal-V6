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
    def __init__(self, db_type, **kwargs):
        """
        Initialize the database manager.

        :param db_type: Type of database ('sqlite' or 'mysql').
        :param kwargs: Additional parameters based on db_type.

        :example:
        >>> database = Database("sqlite", db_file="jukebox.db")
        >>> database = Database("mysql", host="localhost", user="root", password="password", database="jukebox", port=3306)
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
        """Connect to an SQLite database."""
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
            print(f"Connected to SQLite database {db_file}")
            self.create_tables()
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite database: {e}")

    def _connect_mysql(self, host, user, password, database, port=3306):
        """Connect to a MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, password=password, database=database, port=port
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to MySQL database {database} at {host}")
            self.create_tables()
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")

    def create_tables(self):
        """
        Creates the 'secrets', 'ytcache', and 'replay_history' tables if they do not exist.
        """
        queries = []
        if self.db_type == "sqlite":
            queries = [
                """
                CREATE TABLE IF NOT EXISTS jukebox_secrets (
                    user_id TEXT PRIMARY KEY,
                    secret TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS jukebox_ytcache (
                    video_id TEXT PRIMARY KEY,
                    metadata TEXT,
                    registered_date TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS jukebox_replay_history (
                    user_id TEXT,
                    played_at TEXT,
                    song TEXT,
                    FOREIGN KEY (user_id) REFERENCES jukebox_secrets (user_id)
                );
                """,
            ]
        elif self.db_type == "mysql":
            queries = [
                """
                CREATE TABLE IF NOT EXISTS jukebox_secrets (
                    user_id VARCHAR(255) PRIMARY KEY,
                    secret TEXT
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS jukebox_ytcache (
                    video_id VARCHAR(255) PRIMARY KEY,
                    metadata TEXT,
                    registered_date VARCHAR(255)
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS jukebox_replay_history (
                    user_id VARCHAR(255),
                    played_at VARCHAR(255),
                    song TEXT,
                    FOREIGN KEY (user_id) REFERENCES jukebox_secrets (user_id)
                );
                """,
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
            if self.db_type == "sqlite":
                query = """
                INSERT INTO jukebox_secrets (user_id, secret)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET secret=excluded.secret;
                """
                self.cursor.execute(query, (user_id, secret))
            else:
                query = """
                INSERT INTO jukebox_secrets (user_id, secret)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE secret=VALUES(secret);
                """
                self.cursor.execute(query, (user_id, secret))
            self.connection.commit()
            LogHandler.info(f"Registered user: {user_id}")
        except Exception as e:
            LogHandler.error(f"Error registering user: {e}")
            raise e
        return secret

    async def user_exists(self, user_id: str) -> bool:
        """
        Checks if a user exists in the jukebox_secrets table.

        Args:
            user_id (str): The ID of the user to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        try:
            if self.db_type == "sqlite":
                query = "SELECT EXISTS(SELECT 1 FROM jukebox_secrets WHERE user_id = ?)"
                self.cursor.execute(query, (user_id,))
            else:  # Assuming the only other option is 'mysql'
                query = (
                    "SELECT EXISTS(SELECT 1 FROM jukebox_secrets WHERE user_id = %s)"
                )
                self.cursor.execute(query, (user_id,))
            return self.cursor.fetchone()[0] == 1
        except Exception as e:
            LogHandler.error(f"Error checking if user exists: {e}")
            return False

    async def get_user_secret(self, user_id: str) -> str | None:
        """
        Retrieves the secret for a specified user.

        Args:
            user_id (str): The ID of the user whose secret is to be retrieved.

        Returns:
            str: The secret of the user, or None if the user is not found.
        """
        try:
            if self.db_type == "sqlite":
                query = "SELECT secret FROM jukebox_secrets WHERE user_id = ?"
                self.cursor.execute(query, (user_id,))
            else:
                query = "SELECT secret FROM jukebox_secrets WHERE user_id = %s"
                self.cursor.execute(query, (user_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
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
            if self.db_type == "sqlite":
                query = """
                INSERT INTO jukebox_ytcache (video_id, metadata, registered_date)
                VALUES (?, ?, ?)
                ON CONFLICT(video_id) DO UPDATE SET metadata=excluded.metadata, registered_date=excluded.registered_date;
                """
                self.cursor.execute(query, (video_id, metadata_json, registered_date))
            else:
                query = """
                INSERT INTO jukebox_ytcache (video_id, metadata, registered_date)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE metadata=VALUES(metadata), registered_date=VALUES(registered_date);
                """
                self.cursor.execute(query, (video_id, metadata_json, registered_date))
            self.connection.commit()
            LogHandler.info(f"Cached video metadata for {video_id}")
        except Exception as e:
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
            if self.db_type == "sqlite":
                query = "SELECT metadata FROM jukebox_ytcache WHERE video_id = ?"
                self.cursor.execute(query, (video_id,))
            else:
                query = "SELECT metadata FROM jukebox_ytcache WHERE video_id = %s"
                self.cursor.execute(query, (video_id,))
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
        Retrieves cached metadata for a specified list of videos.

        Args:
            video_ids (list): A list of video IDs.

        Returns:
            dict: A dictionary with video IDs as keys and their cached metadata as values.
        """
        video_ids_tuple = tuple(video_ids)
        metadata_dict = {}
        try:
            if self.db_type == "sqlite":
                query = "SELECT video_id, metadata FROM jukebox_ytcache WHERE video_id IN ({})".format(
                    ",".join("?" for _ in video_ids)
                )
                self.cursor.execute(query, video_ids_tuple)
            else:
                query = "SELECT video_id, metadata FROM jukebox_ytcache WHERE video_id IN ({})".format(
                    ",".join("%s" for _ in video_ids)
                )
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
        Adds an entry to the replay history for a user.

        Args:
            user_id (str): The ID of the user.
            played_at (str): The timestamp when the song was played.
            song (str): The name of the song.
        """
        if not await self.user_exists(user_id):
            await self.register(user_id)
        try:
            if self.db_type == "sqlite":
                query = """
                INSERT INTO jukebox_replay_history (user_id, played_at, song)
                VALUES (?, ?, ?)
                """
                self.cursor.execute(query, (user_id, played_at, song))
            else:
                query = """
                INSERT INTO jukebox_replay_history (user_id, played_at, song)
                VALUES (%s, %s, %s)
                """
                self.cursor.execute(query, (user_id, played_at, song))
            self.connection.commit()
            LogHandler.info(f"Added replay entry for {user_id}")
        except Exception as e:
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
            if self.db_type == "sqlite":
                query = "SELECT played_at, song FROM jukebox_replay_history WHERE user_id = ? and played_at >= ? ORDER BY played_at DESC"
                self.cursor.execute(query, (user_id, cutoff_date))
            else:
                query = "SELECT played_at, song FROM jukebox_replay_history WHERE user_id = %s and played_at >= %s ORDER BY played_at DESC"
                self.cursor.execute(query, (user_id, cutoff_date))
            results = self.cursor.fetchall()
            history = [
                {"played_at": result[0], "song": result[1]} for result in results
            ]
            return history
        except Exception as e:
            LogHandler.error(f"Error fetching replay history: {e}")
            raise e

    def clear_old_cache(self):
        """Clears cached entries older than 28 days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=28)).isoformat()
            if self.db_type == "sqlite":
                query = "DELETE FROM jukebox_ytcache WHERE registered_date < ?"
                self.cursor.execute(query, (cutoff_date,))
            else:
                query = "DELETE FROM jukebox_ytcache WHERE registered_date < %s"
                self.cursor.execute(query, (cutoff_date,))
            self.connection.commit()
        except Exception as e:
            LogHandler.error(f"Error clearing old jukebox_ytcache: {e}")
            raise e

    def run_cleanup(self):
        """Runs the cleanup process to clear old jukebox_ytcache entries."""
        self.clear_old_cache()
        LogHandler.info("Old jukebox_ytcache entries cleared.")

    def close(self):
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")
