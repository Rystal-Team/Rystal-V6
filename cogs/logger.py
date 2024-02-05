import nextcord
from nextcord.ext import commands
import datetime
from config.config import type_color, logging_channe_id, enable_activity_logging


class logger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog Ready!")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Integration):
        channel = self.bot.get_channel(logging_channe_id)
        try:
            identifier = interaction.application_command.qualified_name
        except Exception:
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
        bot.add_cog(logger(bot))
