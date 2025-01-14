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
import platform
import time
from datetime import datetime


import nextcord
import psutil
import requests
import yt_dlp
from nextcord import Interaction
from nextcord.ext import commands
from termcolor import colored

from config.loader import default_language, lang, status_text, use_ytdlp
from config.perm import auth_guard
from database.guild_handler import get_guild_language
from module.embeds.generic import Embeds

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

        print(
            colored(
                "=============================================================",
                color="white",
            )
        )

        yt_dlp_version = yt_dlp.version.__version__
        print(colored(f"Installed yt-dlp version: {yt_dlp_version}", color="dark_grey"))

        r = requests.get("https://pypi.org/pypi/yt-dlp/json")
        latest_yt_dlp_version = r.json()["info"]["version"]

        yt_dlp_version = datetime.strptime(yt_dlp_version, "%Y.%m.%d").strftime(
            "%Y.%m.%d"
        )

        latest_yt_dlp_version = datetime.strptime(
            latest_yt_dlp_version, "%Y.%m.%d"
        ).strftime("%Y.%m.%d")

        print(
            colored(
                f"Latest yt-dlp version: {latest_yt_dlp_version}", color="dark_grey"
            )
        )

        if use_ytdlp:
            print(colored(text="Using YTDLP to extract video data", color="dark_grey"))
        else:
            print(
                colored(text="Using Meta-YT to extract video data", color="dark_grey")
            )
        print(colored(text=f"Default language: {default_language}", color="dark_grey"))

        if yt_dlp_version != latest_yt_dlp_version:
            print(
                colored(
                    "Update yt-dlp to the latest version by running 'pip install -U yt-dlp' to avoid any issues.",
                    color="red",
                )
            )
        else:
            print(
                colored("yt-dlp is up to date with the latest version.", color="green")
            )

    @nextcord.slash_command(
        description=lang[default_language]["system_ping_description"]
    )
    @auth_guard.check_permissions("status/ping")
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

    @nextcord.slash_command(
        description=lang[default_language]["system_info_description"]
    )
    @auth_guard.check_permissions("status/info")
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

        uptime_time_str = str(
            datetime.timedelta(seconds=(round(time.time() - start_time)))
        )

        cpu_str = lang[await get_guild_language(interaction.guild.id)]["cpu"].format(
            cpu=cpu
        )
        ram_str = lang[await get_guild_language(interaction.guild.id)]["ram"].format(
            ram_used=ram_used, ram_total=ram_total
        )
        os_str = lang[await get_guild_language(interaction.guild.id)]["os"].format(
            platform=os_platform
        )
        version_str = lang[await get_guild_language(interaction.guild.id)][
            "version"
        ].format(os_version=os_version)
        release_str = lang[await get_guild_language(interaction.guild.id)][
            "release"
        ].format(os_release=os_release)
        uptime_str = lang[await get_guild_language(interaction.guild.id)][
            "uptime"
        ].format(uptime=uptime_time_str)

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
