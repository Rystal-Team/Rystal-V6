"""
This module defines a Database class for managing user secrets stored in an SQLite database. It includes methods for 
connecting to the database, creating tables, registering users, and retrieving user secrets.

Classes:
    Database: Manages database connections and operations for user secrets.

Methods:
    __init__(db_path): Initializes the Database instance with the specified database path.
    connect(): Connects to the SQLite database and creates the required table.
    close(): Closes the database connection.
    create_table(): Creates the 'secrets' table if it does not exist.
    register(user_id): Registers a user by generating and storing a secret.
    get_user_secret(user_id): Retrieves the secret for a specified user.

Modules:
    asyncio: Provides support for asynchronous programming.
    sqlite3: Manages SQLite database connections.
    .utils: Contains utility functions such as generate_secret.
    .LogHandler: Manages logging functionalities.
"""

import sqlite3
import asyncio
from .utils import generate_secret
from . import LogHandler

class Database:
    """
    Manages database connections and operations for user secrets.

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
        """
        Connects to the SQLite database and creates the required table.
        """
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.create_table()

    def close(self):
        """
        Closes the database connection.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def create_table(self):
        """
        Creates the 'secrets' table if it does not exist.
        """
        query = """
        CREATE TABLE IF NOT EXISTS secrets (
            user_id TEXT PRIMARY KEY,
            secret TEXT
        );
        """
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

    async def get_user_secret(self, user_id: str) -> str:
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
            else:
                return None
        except sqlite3.Error as e:
            LogHandler.error(f"Error fetching user secret: {e}")
            raise e
