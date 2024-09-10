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

import nextcord
from nextcord.ext import commands

from config.perm import auth_guard
from module.nextcord_authguard.event_manager import EventManager

# TODO: Add permission decorator for commands
# TODO: Language support


class PermissionSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @EventManager.listener
    async def on_permission_denied(self, interaction, permission, default_permission):
        print(permission, default_permission)
        await interaction.response.send_message(
            "You don't have permission to do this.",
        )

    @nextcord.slash_command(description="Set the permission for a role.")
    async def permission(self, interaction: nextcord.Interaction):
        return

    @permission.subcommand(description="View all commands IDs.")
    async def list(self, interaction: nextcord.Interaction):
        commands_list = auth_guard.get_commands()

        await interaction.response.send_message(
            "\n".join(commands_list),
        )

    @permission.subcommand(description="Set the permission for user.")
    async def user(
        self,
        interaction: nextcord.Interaction,
        command_id: str,
        user: nextcord.Member,
        allow: bool,
    ):
        if command_id not in auth_guard.get_commands():
            await interaction.response.send_message(
                f"Command ID {command_id} is not found.",
            )
            return
        auth_guard.edit_user(command_id, user.id, interaction.guild.id, allow)

        await interaction.response.send_message(
            f"Permission for {user.mention} to use {command_id} has been set to {allow}.",
        )

        return

    @permission.subcommand(description="Set the permission for role.")
    async def role(
        self,
        interaction: nextcord.Interaction,
        command_id: str,
        role: nextcord.Role,
        allow: bool,
    ):
        if command_id not in auth_guard.get_commands():
            await interaction.response.send_message(
                f"Command ID {command_id} is not found.",
            )
            return
        auth_guard.edit_role(command_id, role.id, interaction.guild.id, allow)

        await interaction.response.send_message(
            f"Permission for {role.mention} to use {command_id} has been set to {allow}.",
        )

        return


async def setup(bot):
    cog = PermissionSystem(bot)
    bot.add_cog(cog)
    EventManager.attach(cog)
