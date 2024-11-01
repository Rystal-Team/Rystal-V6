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

import datetime
import json
import logging

import nextcord
from nextcord.ext import commands

from config.loader import enable_activity_logging, logging_channel_id, type_color


class Logger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.set_debug(True)
        logging.basicConfig(level=logging.DEBUG)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        channel = self.bot.get_channel(logging_channel_id)
        if (
            hasattr(interaction, "application_command")
            and hasattr(interaction.application_command, "qualified_name")
            and isinstance(interaction.application_command.qualified_name, str)
        ):
            identifier = interaction.application_command.qualified_name
        else:
            identifier = "Not Command"

        embed = nextcord.Embed(
            title="Command Execution",
            description=f"Command: **/{identifier}**",
            color=(type_color["info"]),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.add_field(
            name="Channel",
            value=f"```{interaction.channel.name} | {interaction.channel.mention}```",
            inline=False,
        )
        embed.add_field(
            name="Guild",
            value=f"```{interaction.guild.name} | Owner: {interaction.guild.owner} | Humans: {len(interaction.guild.humans)}```",
            inline=False,
        )

        embed.add_field(name="User", value=f"{interaction.user.name}", inline=False)
        if "options" in interaction.data:
            embed.add_field(
                name="Options",
                value=f"```json\n{str(json.dumps(interaction.data['options'], indent=2))}```",
                inline=False,
            )
        await channel.send(embed=embed)


def setup(bot):
    if enable_activity_logging:
        bot.add_cog(Logger(bot))
