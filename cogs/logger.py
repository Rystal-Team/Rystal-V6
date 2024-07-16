import datetime
import logging

import nextcord
from nextcord.ext import commands

from config.config import (enable_activity_logging, logging_channe_id,
                           type_color)


class Logger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.set_debug(True)
        logging.basicConfig(level=logging.DEBUG)

    """@commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog Ready!")"""

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        channel = self.bot.get_channel(logging_channe_id)
        if (hasattr(interaction, 'application_command') and
            hasattr(interaction.application_command, 'qualified_name') and
            isinstance(interaction.application_command.qualified_name, str)):
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
            value=f"{interaction.channel.name} | {interaction.channel.mention}",
            inline=False,
        )
        embed.add_field(
            name="Guild",
            value=f"{interaction.guild.name} | Owner: {interaction.guild.owner} | Humans: {len(interaction.guild.humans)}",
            inline=False,
        )

        embed.add_field(name="User", value=f"{interaction.user.name}", inline=False)
        if "options" in interaction.data:
            embed.add_field(
                name="Options",
                value=f"{str(interaction.data['options'])}",
                inline=False,
            )
        await channel.send(embed=embed)


def setup(bot):
    if enable_activity_logging:
        bot.add_cog(Logger(bot))
