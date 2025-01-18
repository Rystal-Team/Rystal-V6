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
        create_query (dict): A dictionary containing table creation queries for both SQLite and MySQL.
    """

    def __init__(self, db_type, create_query, **kwargs):
        """
        Initializes the DatabaseHandler with the specified database type and connection parameters.

        Args:
            db_type (str): The type of the database ('sqlite' or 'mysql').
            create_query (dict): A dictionary containing table creation queries for both SQLite and MySQL.
            **kwargs: Additional arguments for database connection.
        """
        self.db_type = db_type
        self.connection = None
        self.cursor = None
        self.create_query = create_query or {
            "sqlite": {},
            "mysql": {},
        }

        if db_type == "sqlite":
            self._connect_sqlite(**kwargs)
        elif db_type == "mysql":
            self._connect_mysql(**kwargs)
        else:
            raise ValueError("Unsupported database type. Use 'sqlite' or 'mysql'.")

    def _connect_sqlite(self, db_file):
        """
        Connects to an SQLite database.

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
        Connects to a MySQL database.

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
            query_dict (dict): A dictionary containing SQL queries for both SQLite and MySQL.
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
            else:
                print("No database connection.")
        except (sqlite3.Error, Error) as e:
            print(f"Database error: {e}")

    def create_tables(self):
        """
        Creates tables in the connected database based on the create_query attribute.
        """
        for table, queries in self.create_query[self.db_type].items():
            self._create_or_update_table(table, queries)

    def _create_or_update_table(self, table_name, queries):
        """
        Creates or updates a table in the connected database.

        Args:
            table_name (str): The name of the table.
            queries (dict): A dictionary containing 'create' and 'columns' queries.
        """
        if not self._table_exists(table_name):
            self._create_table(table_name, queries["create"])
        else:
            self._update_table(table_name, queries["columns"])

    def _create_table(self, table_name, create_query):
        """
        Creates a table in the connected database.

        Args:
            table_name (str): The name of the table.
            create_query (str): The SQL query to create the table.
        """
        self.cursor.execute(create_query)
        self.connection.commit()

    def _update_table(self, table_name, columns):
        """
        Updates a table in the connected database by adding new columns.

        Args:
            table_name (str): The name of the table.
            columns (dict): A dictionary containing column names and their definitions.
        """
        existing_columns = self._get_existing_columns(table_name)
        for column, column_def in columns.items():
            if column not in existing_columns:
                alter_query = (
                    f"ALTER TABLE {table_name} ADD COLUMN {column} {column_def}"
                )
                self.cursor.execute(alter_query)
                self.connection.commit()

    def _table_exists(self, table_name):
        """
        Checks if a table exists in the connected database.

        Args:
            table_name (str): The name of the table.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        if self.db_type == "sqlite":
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
            )
        elif self.db_type == "mysql":
            self.cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        return bool(self.cursor.fetchone())

    def _get_existing_columns(self, table_name):
        """
        Gets the existing columns of a table in the connected database.

        Args:
            table_name (str): The name of the table.

        Returns:
            set: A set of existing column names.
        """
        if self.db_type == "sqlite":
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            return {col[1] for col in self.cursor.fetchall()}
        if self.db_type == "mysql":
            self.cursor.execute(f"DESCRIBE {table_name}")
            return {col[0] for col in self.cursor.fetchall()}

    def fetchall(self):
        """
        Fetches all rows from the last executed query.

        Returns:
            list: A list of all rows, or None if an error occurs.
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
            tuple: A single row, or None if an error occurs.
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
