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

import sqlite3

import mysql.connector
from mysql.connector import Error


class DatabaseHandler:
    """
    A class to handle database operations for SQLite and MySQL databases.

    Attributes:
        db_type (str): The type of the database ('sqlite' or 'mysql').
        connection (object): The database connection object.
        cursor (object): The database cursor object.
        create_query (dict): A dictionary containing create table queries for both SQLite and MySQL.
    """

    def __init__(self, db_type, create_query, **kwargs):
        """
        Initializes the DatabaseHandler with the specified database type and connection parameters.

        Args:
            db_type (str): The type of the database ('sqlite' or 'mysql').
            create_query (dict): A dictionary containing create table queries for both SQLite and MySQL.
            **kwargs: Additional arguments for database connection.
        """
        self.db_type = db_type
        self.connection = None
        self.cursor = None
        self.create_query = create_query or {
            "sqlite": [],
            "mysql": [],
        }

        if db_type == "sqlite":
            self._connect_sqlite(**kwargs)
        elif db_type == "mysql":
            self._connect_mysql(**kwargs)
        else:
            raise ValueError("Unsupported database type. Use 'sqlite' or 'mysql'.")

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

    def execute(self, query_dict, params=None):
        """
        Executes a query on the connected database.

        Args:
            query_dict (dict): A dictionary containing the query for both SQLite and MySQL.
            params (tuple, optional): Parameters to be passed with the query. Defaults to None.

        Raises:
            ValueError: If query_dict is not a dictionary with 'sqlite' and 'mysql' keys.
        """
        if (
            not isinstance(query_dict, dict)
            or "sqlite" not in query_dict
            or "mysql" not in query_dict
        ):
            raise ValueError(
                "query_dict must be a dictionary with 'sqlite' and 'mysql' keys"
            )

        query = (
            query_dict["sqlite"] if self.db_type == "sqlite" else query_dict["mysql"]
        )

        try:
            if self.cursor:
                self.cursor.execute(query, params or ())
                self.connection.commit()
        except (sqlite3.Error, Error) as e:
            print(f"Database error: {e}")

    def create_tables(self):
        """Creates necessary tables in the database."""
        for query in self.create_query[self.db_type]:
            print(query)
            self.cursor.execute(query)
        self.connection.commit()

    def fetchall(self):
        """
        Fetches all rows from the last executed query.

        Returns:
            list: A list of all rows from the last executed query, or None if an error occurs.
        """
        try:
            return self.cursor.fetchall() if self.cursor else None
        except (sqlite3.Error, Error) as e:
            print(f"Database error: {e}")
            return None

    def fetchone(self):
        """
        Fetches one row from the last executed query.

        Returns:
            tuple: A single row from the last executed query, or None if an error occurs.
        """
        try:
            return self.cursor.fetchone() if self.cursor else None
        except (sqlite3.Error, Error) as e:
            print(f"Database error: {e}")
            return None

    def close(self):
        """Closes the database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
