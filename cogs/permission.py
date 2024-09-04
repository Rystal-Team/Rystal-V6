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


class PermissionSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Set the permission for a role.")
    async def permission(self, interaction: nextcord.Interaction):
        return

    @permission.subcommand(description="Set the permission for user.")
    async def user(
        self,
        interaction: nextcord.Interaction,
        command_id: str,
        user: nextcord.Member,
        allow: bool,
    ):
        auth_guard.edit_user(command_id, user.id, interaction.guild.id, allow)

        await interaction.response.send_message(
            f"Permission for {user.mention} to use {command_id} has been set to {allow}.",
            ephemeral=True,
        )

        return


async def setup(bot):
    cog = PermissionSystem(bot)
    bot.add_cog(cog)
