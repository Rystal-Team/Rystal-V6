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
from yaml.error import YAMLError

from . import LogHandler
from .database.base import DatabaseHandler
from .database_create import create_statement
from .event_manager import EventManager
from .loader import get_default_permission, load_permission
from .permission import GeneralPermission


class AuthGuard:
    """
    A class to handle authorization and permissions for commands in a Nextcord bot.

    Attributes:
        db (DatabaseHandler): The database handler for managing permissions.
        command_id_list (list): A list of command IDs to manage permissions.
        default_perm (dict): The default permissions loaded from the configuration.
    """

    def __init__(
        self,
        db_type="sqlite",
        db_path="./sqlite/authguard.sqlite",
        mysql_host="localhost",
        mysql_port=3306,
        mysql_user="root",
        mysql_password="password",
        mysql_database="authguard",
        perm_config: str = None,
    ):
        """
        Initializes the AuthGuard class with database and permission configurations.

        Args:
            db_type (str): The type of database to use ('sqlite' or 'mysql').
            db_path (str): The path to the SQLite database file.
            mysql_host (str): The MySQL database host.
            mysql_port (int): The MySQL database port.
            mysql_user (str): The MySQL database user.
            mysql_password (str): The MySQL database password.
            mysql_database (str): The MySQL database name.
            perm_config (str): The permission configuration path.

        Raises:
            ValueError: If perm_config is not provided or if an invalid database type is provided.
            FileNotFoundError: If the permission config file is not found.
            YAMLError: If there is an error in the YAML format of the permission config.
        """
        if not perm_config:
            raise ValueError("A valid permission config is required!")

        try:
            self.default_perm = load_permission(perm_config)
        except (FileNotFoundError, YAMLError) as e:
            raise e

        db_params = {
            "sqlite": {
                "db_type": db_type,
                "create_query": create_statement,
                "db_file": db_path,
            },
            "mysql": {
                "db_type": db_type,
                "create_query": create_statement,
                "host": mysql_host,
                "port": mysql_port,
                "user": mysql_user,
                "password": mysql_password,
                "database": mysql_database,
            },
        }

        if db_type not in db_params:
            raise ValueError("Invalid database type provided!")

        self.db = DatabaseHandler(**db_params[db_type])
        self.db.create_tables()
        self.command_id_list = []

    @staticmethod
    def find_interaction(*args):
        """
        Finds and returns the first instance of nextcord.Interaction in the provided arguments.

        Args:
            *args: Variable length argument list.

        Returns:
            nextcord.Interaction: The first interaction found, or None if not found.
        """
        return next(
            (arg for arg in args if isinstance(arg, nextcord.Interaction)), None
        )

    def cleanup_permissions(self):
        """Cleans up permissions by removing entries not in the command_id_list."""
        placeholders = ", ".join(
            "?" if self.db.db_type == "sqlite" else "%s" for _ in self.command_id_list
        )
        statement = {
            "sqlite": f"DELETE FROM permissions WHERE command_id NOT IN ({placeholders})",
            "mysql": f"DELETE FROM permissions WHERE command_id NOT IN ({placeholders})",
        }
        self.db.execute(statement, tuple(self.command_id_list))
        self.command_id_list.clear()

    def check_permissions(self, command_id):
        """
        Decorator to check permissions for a command.

        Args:
            command_id (str): The ID of the command to check permissions for.

        Returns:
            function: The decorated function with permission checks.
        """
        if command_id in self.command_id_list:
            raise ValueError("Command ID already exists!")
        self.command_id_list.append(command_id)

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cog, interaction = args[0], args[1]
                user, guild = interaction.user, interaction.guild
                user_roles = [role.id for role in user.roles]
                permissions = self.get_command_permissions(command_id, guild.id)
                default_perm = get_default_permission(self.default_perm, command_id)

                if default_perm is None or default_perm == []:
                    LogHandler.warning(
                        "Missing default permission for command: " + command_id
                    )

                if permissions and permissions is not None and len(permissions) > 0:
                    permissions = permissions or []
                    for perm in permissions:
                        if (
                            not perm[3] is None
                            and int(perm[3]) == user.id
                            and perm[5] == 1
                        ):
                            return await func(*args, **kwargs)
                        if (
                            not perm[4] is None
                            and int(perm[4]) in user_roles
                            and perm[5] == 1
                        ):
                            return await func(*args, **kwargs)
                if any(
                    [
                        GeneralPermission.ADMIN in default_perm
                        and user.guild_permissions.administrator,
                        GeneralPermission.OWNER in default_perm
                        and cog.bot.owner_id == user.id,
                        GeneralPermission.MOD in default_perm
                        and user.guild_permissions.manage_guild,
                        GeneralPermission.EVERYONE in default_perm,
                    ]
                ):
                    return await func(*args, **kwargs)

                if GeneralPermission.DISABLED in default_perm:
                    await EventManager.fire(
                        "on_permission_denied",
                        interaction,
                        permissions,
                        default_perm,
                    )
                    return

                await EventManager.fire(
                    "on_permission_denied", interaction, permissions, default_perm
                )

            return wrapper

        return decorator

    def user_exists(self, guild_id, user_id, command_id):
        """
        Checks if a user exists in the permissions table.

        Args:
            guild_id (str): The ID of the guild.
            user_id (str): The ID of the user.
            command_id (str): The ID of the command.

        Returns:
            tuple: The user record if exists, otherwise None.
        """
        statement = {
            "sqlite": "SELECT * FROM permissions WHERE guild_id = ? AND user_id = ? AND command_id = ?",
            "mysql": "SELECT * FROM permissions WHERE guild_id = %s AND user_id = %s AND command_id = %s",
        }
        self.db.execute(statement, (guild_id, user_id, command_id))
        return self.db.fetchone()

    def role_exists(self, guild_id, role_id, command_id):
        """
        Checks if a role exists in the permissions table.

        Args:
            guild_id (str): The ID of the guild.
            role_id (str): The ID of the role.
            command_id (str): The ID of the command.

        Returns:
            tuple: The role record if exists, otherwise None.
        """
        statement = {
            "sqlite": "SELECT * FROM permissions WHERE guild_id = ? AND role_id = ? AND command_id = ?",
            "mysql": "SELECT * FROM permissions WHERE guild_id = %s AND role_id = %s AND command_id = %s",
        }
        self.db.execute(statement, (guild_id, role_id, command_id))
        return self.db.fetchone()

    def get_commands(self):
        """
        Returns the list of command IDs.

        Returns:
            list: The list of command IDs.
        """
        return self.command_id_list

    def get_command_permissions(self, command_id, guild_id):
        """
        Retrieves permissions for a specific command in a guild.

        Args:
            command_id (str): The ID of the command.
            guild_id (int): The ID of the guild.

        Returns:
            list: The list of permissions for the command.
        """
        statement = {
            "sqlite": "SELECT * FROM permissions WHERE command_id = ? AND guild_id = ?",
            "mysql": "SELECT * FROM permissions WHERE command_id = %s AND guild_id = %s",
        }
        self.db.execute(statement, (command_id, guild_id))
        return self.db.fetchall()

    def edit_user(self, command_id, user_id, guild_id, allowed):
        """
        Edits or inserts a user's permission for a command in a guild.

        Args:
            command_id (str): The ID of the command.
            user_id (str): The ID of the user.
            guild_id (str): The ID of the guild.
            allowed (bool): Whether the user is allowed to use the command.
        """
        print(command_id, user_id, guild_id, allowed)
        print(self.user_exists(guild_id, user_id, command_id))
        if not self.user_exists(guild_id, user_id, command_id):
            statement = {
                "sqlite": "INSERT INTO permissions (permission_id, command_id, guild_id, user_id, allowed) VALUES (?, ?, ?, ?, ?)",
                "mysql": "INSERT INTO permissions (permission_id, command_id, guild_id, user_id, allowed) VALUES (%s, %s, %s, %s, %s)",
            }
            self.db.execute(
                statement,
                (str(uuid4()), command_id, guild_id, user_id, allowed),
            )
        else:
            statement = {
                "sqlite": "UPDATE permissions SET allowed = ? WHERE command_id = ? AND guild_id = ? AND user_id = ?",
                "mysql": "UPDATE permissions SET allowed = %s WHERE command_id = %s AND guild_id = %s AND user_id = %s",
            }
            self.db.execute(statement, (allowed, command_id, guild_id, user_id))

    def edit_role(self, command_id, role_id, guild_id, allowed):
        """
        Edits or inserts a role's permission for a command in a guild.

        Args:
            command_id (str): The ID of the command.
            role_id (str): The ID of the role.
            guild_id (str): The ID of the guild.
            allowed (bool): Whether the role is allowed to use the command.
        """
        if not self.role_exists(guild_id, role_id, command_id):
            statement = {
                "sqlite": "INSERT INTO permissions (permission_id, command_id, guild_id, role_id, allowed) VALUES (?, ?, ?, ?, ?)",
                "mysql": "INSERT INTO permissions (permission_id, command_id, guild_id, role_id, allowed) VALUES (%s, %s, %s, %s, %s)",
            }
            self.db.execute(
                statement,
                (str(uuid4()), command_id, guild_id, role_id, allowed),
            )
        else:
            statement = {
                "sqlite": "UPDATE permissions SET allowed = ? WHERE command_id = ? AND guild_id = ? AND role_id = ?",
                "mysql": "UPDATE permissions SET allowed = %s WHERE command_id = %s AND guild_id = %s AND role_id = %s",
            }
            self.db.execute(statement, (allowed, command_id, guild_id, role_id))
