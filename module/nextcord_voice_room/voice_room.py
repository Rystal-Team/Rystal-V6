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


from .database.base import DatabaseHandler
from .database_create import create_statement


class VoiceRoom:
    def __init__(
        self,
        db_type="sqlite",
        db_path="./sqlite/authguard.sqlite",
        mysql_host="localhost",
        mysql_port=3306,
        mysql_user="root",
        mysql_password="password",
        mysql_database="authguard",
    ):
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

    async def create_voiceroom(self, interaction, member_limit=0):
        """
        Creates a new voice room for the user who invoked the command.

        Args:
            interaction (nextcord.Interaction): The interaction object.
            member_limit (int): The member limit for the voice channel. Default is 0.
        """

    async def on_voice_state_update(self, member, before, after):
        """
        Handles the voice state update event.

        Args:
            member (nextcord.Member): The member who triggered the event.
            before (nextcord.VoiceState): The voice state before the event.
            after (nextcord.VoiceState): The voice state after the event.
        """
        if before.channel and not after.channel:
            await self.delete_voiceroom(member)
        elif not before.channel and after.channel:
            await self.register_voiceroom(member, after.channel)

    async def register_voiceroom(self, member, channel):
        """
        Registers the voice room for a user.

        Args:
            member (nextcord.Member): The member who created the voice room.
            channel (nextcord.VoiceChannel): The voice channel created by the member.
        """
        statement = {
            "sqlite": "INSERT INTO voice_rooms (user_id, channel_id) VALUES (?, ?)",
            "mysql": "INSERT INTO voice_rooms (user_id, channel_id) VALUES (%s, %s)",
        }
        self.db.execute(statement, (member.id, channel.id))

    async def get_voiceroom(self, member):
        """
        Gets the settings for the voice room of a user.

        Args:
            member (nextcord.Member): The member whose voice room settings to get.

        Returns:
            dict: The voice room settings.
        """
        statement = {
            "sqlite": "SELECT * FROM voice_rooms WHERE user_id = ?",
            "mysql": "SELECT * FROM voice_rooms WHERE user_id = %s",
        }
        self.db.execute(statement, (member.id,))
        result = self.db.fetchall()
        return result

    async def delete_voiceroom(self, member):
        """
        Deletes the voice room of a user.

        Args:
            member (nextcord.Member): The member whose voice room to delete.
        """
        statement = {
            "sqlite": "DELETE FROM voice_rooms WHERE user_id = ?",
            "mysql": "DELETE FROM voice_rooms WHERE user_id = %s",
        }
        self.db.execute(statement, (member.id,))
