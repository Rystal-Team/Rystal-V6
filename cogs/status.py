import datetime
import platform
import time

import nextcord
import psutil
from nextcord import Interaction
from nextcord.ext import commands
from termcolor import colored

from config.config import lang, status_text, use_ytdlp
from database.guild_handler import get_guild_language
from module.embed import Embeds

start_time = time.time()
class_namespace = "system_class_title"


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            activity=nextcord.Activity(
                type=nextcord.ActivityType.playing, name=status_text
            ),
            status=nextcord.Status.online,
        )
        print(
            colored(
                text="|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||",
                color="white",
            )
        )
        print(
            colored(
                text="Successfully logged in as {0.user}...".format(self.bot),
                color="green",
            )
        )

        for guild in self.bot.guilds:
            print(
                colored(
                    text=f"Guild: {guild.name} | Member: {guild.member_count}",
                    color="white",
                )
            )

        if use_ytdlp:
            print(colored(text=f"Using YTDLP to extract video data", color="dark_grey"))
        else:
            print(colored(text=f"Using Meta-YT to extract video data", color="dark_grey"))

    @nextcord.slash_command(description="🤖 | Pong!")
    async def ping(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)
        ping = round((self.bot.latency) * 1000)

        await interaction.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "ping"
                ].format(ping=ping),
                message_type="info",
            )
        )

    @nextcord.slash_command(description="🤖 | Get the System info of the bot!")
    async def info(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        cpu = psutil.cpu_percent(0.5)
        ram_used = round(psutil.virtual_memory()[3] / 1000000000, 1)
        ram_total = round(psutil.virtual_memory()[0] / 1000000000, 1)
        os_platform = platform.system()
        os_version = platform.version()
        os_release = platform.release()
        os_time = datetime.datetime.now()
        os_time = os_time.strftime("%H:%M:%S %d/%m/%y")

        uptime_time_str = str(datetime.timedelta(seconds=(round(time.time() - start_time))))

        cpu_str = lang[await get_guild_language(interaction.guild.id)]["cpu"].format(cpu=cpu)
        ram_str = lang[await get_guild_language(interaction.guild.id)]["ram"].format(ram_used=ram_used,
                                                                                     ram_total=ram_total)
        os_str = lang[await get_guild_language(interaction.guild.id)]["os"].format(platform=os_platform)
        version_str = lang[await get_guild_language(interaction.guild.id)]["version"].format(os_version=os_version)
        release_str = lang[await get_guild_language(interaction.guild.id)]["release"].format(os_release=os_release)
        uptime_str = lang[await get_guild_language(interaction.guild.id)]["uptime"].format(uptime=uptime_time_str)

        message_str = f"{cpu_str}\n{ram_str}\n{os_str}\n{version_str}\n{release_str}\n{uptime_str}"

        await interaction.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=message_str,
                message_type="info",
            )
        )


async def setup(bot):
    bot.add_cog(System(bot))
