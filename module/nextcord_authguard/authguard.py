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

from functools import wraps
from uuid import uuid4
import nextcord
from yaml import YAMLError

from .database.base import DatabaseHandler
from .database_create import create_statement
from .loader import load_permission
from . import LogHandler


class AuthGuard:
    """
    Initializes the AuthGuard with the given permission config.

    Args:
        db_type (str): The type of the database ('sqlite' or 'mysql').
        db_path (str): The path to the SQLite database file.
        mysql_host (str): The hostname of the MySQL server.
        mysql_port (int): The port of the MySQL server.
        mysql_user (str): The username of the MySQL server.
        mysql_password (str): The password of the MySQL server.
        mysql_database (str): The name of the MySQL database.
        perm_config (dict): The permission config to be used.

    Raises:
        ValueError: If a valid permission config is not provided.
        FileNotFoundError: If the permission config is not found.
        YAMLError: If the permission config has an invalid YAML format.
    """

    def __init__(
        self,
        db_type: str = "sqlite",
        db_path: str = "./sqlite/authguard.sqlite",
        mysql_host: str = "localhost",
        mysql_port: int = 3306,
        mysql_user: str = "root",
        mysql_password: str = "password",
        mysql_database: str = "authguard",
        perm_config: str = None,
    ):
        """
        Initializes the AuthGuard with the given permission config.

        Args:
            db_type (str): The type of the database ('sqlite' or 'mysql').
            db_path (str): The path to the SQLite database file.
            mysql_host (str): The hostname of the MySQL server.
            mysql_port (int): The port of the MySQL server.
            mysql_user (str): The username of the MySQL server.
            mysql_password (str): The password of the MySQL server.
            mysql_database (str): The name of the MySQL database.
            perm_config (str): The permission config to be used.

        Raises:
            ValueError: If a valid permission config is not provided.
            FileNotFoundError: If the permission config is not found.
            YAMLError: If the permission config has an invalid YAML format.
        """
        if not perm_config:
            raise ValueError("A valid permission config is required!")

        try:
            self.default_perm = load_permission(perm_config)
        except FileNotFoundError:
            raise FileNotFoundError("Permission config not found!")
        except YAMLError:
            raise YAMLError(
                "Invalid YAML format, recheck if the config YAML format is correct!"
            )

        if db_type == "sqlite":
            self.db = DatabaseHandler(
                db_type=db_type,
                create_query=create_statement,
                db_file=db_path,
            )
        elif db_type == "mysql":
            self.db = DatabaseHandler(
                db_type=db_type,
                create_query=create_statement,
                host=mysql_host,
                port=mysql_port,
                user=mysql_user,
                password=mysql_password,
                database=mysql_database,
            )
        else:
            raise ValueError("Invalid database type provided!")

        self.db.create_tables()
        self.command_id_list = []

        return

    @staticmethod
    def find_interaction(*args):
        for arg in args:
            if isinstance(arg, nextcord.Interaction):
                return arg
        return None

    def cleanup_permissions(self):
        """
        Deletes all permissions that are not registered anymore.
        """
        statement = {
            "sqlite": "DELETE FROM permissions WHERE command_id NOT IN ({})".format(
                ", ".join("?" * len(self.command_id_list))
            ),
            "mysql": "DELETE FROM permissions WHERE command_id NOT IN ({})".format(
                ", ".join("%s" * len(self.command_id_list))
            ),
        }
        self.db.execute(statement, tuple(self.command_id_list))
        self.command_id_list.clear()

    def check_permissions(self, command_id: str):
        """
        A decorator to check if the user has the required permissions to use the command.

        Args:
            command_id (str): The command ID to be checked.

        Returns:
            The decorator function.
        """
        self.command_id_list.append(command_id)

        def decorator(func):

            @wraps(func)
            async def wrapper(*args, **kwargs):
                """
                A wrapper to check if the user has the required permissions to use the command.

                Args:
                    *args: The arguments passed to the function.
                    **kwargs: The keyword arguments passed to the function.

                Returns:
                    The function if the user has the required permissions, else sends an ephemeral message
                    to the user.
                """
                event_name = func.__name__
                LogHandler.info(
                    f"Started Listening `check_permission` on function {event_name}"
                )
                interaction = AuthGuard.find_interaction(*args)
                user = interaction.user
                guild = interaction.guild
                allowed_roles = kwargs.get("allowed_roles")
                allowed_permissions = kwargs.get("allowed_permissions")

                print(guild.name)
                print(user.name)

                if not interaction.guild:
                    await interaction.response.send_message(
                        "権限なし",
                        ephemeral=True,
                    )
                    return

                return await func(*args, **kwargs)

            return wrapper

        return decorator

    def user_exists(self, guild_id: str, user_id: str):
        statement = {
            "sqlite": "SELECT * FROM permissions WHERE guild_id = ? AND user_id = ?",
            "mysql": "SELECT * FROM permissions WHERE guild_id = %s AND user_id = %s",
        }
        self.db.execute(statement, (guild_id, user_id))
        return self.db.fetchone()

    def edit_user(self, command_id: str, guild_id: str, user_id: str, allowed: bool):
        if not self.user_exists(guild_id, user_id):
            statement = {
                "sqlite": "INSERT INTO permissions (permission_id, command_id, guild_id, user_id, allowed) VALUES (?, ?, ?, ?, ?)",
                "mysql": "INSERT INTO permissions (permission_id, command_id, guild_id, user_id, allowed) VALUES (%s, %s, %s, %s, %s)",
            }
            self.db.execute(
                statement,
                (
                    str(uuid4()),
                    command_id,
                    guild_id,
                    user_id,
                    allowed,
                ),
            )
        else:
            statement = {
                "sqlite": "UPDATE permissions SET allowed = ? WHERE command_id = ? AND guild_id = ? AND user_id = ?",
                "mysql": "UPDATE permissions SET allowed = %s WHERE command_id = %s AND guild_id = %s AND user_id = %s",
            }
            self.db.execute(statement, (allowed, command_id, guild_id, user_id))
