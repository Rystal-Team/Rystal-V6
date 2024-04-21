import nextcord, psutil, platform, datetime, time, sys
from module.embed import Embeds
from nextcord.ext import commands
from nextcord import Interaction
from termcolor import colored
from config.config import lang

emcolor = 0x8042A9
start_time = time.time()


class system(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(
            activity=nextcord.Activity(
                type=nextcord.ActivityType.playing, name="🌟 Music Module Update!"
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

    @nextcord.slash_command(description="🤖 | Pong!")
    async def ping(self, interaction: Interaction):
        ping = round((self.bot.latency) * 1000)

        await interaction.send(
            embed=Embeds.message(
                title=lang["system_class_title"], message=lang["ping"].format(ping=ping), message_type="info"
            )
        )

    @nextcord.slash_command(description="🤖 | Get the system info of the bot!")
    async def info(self, interaction: Interaction):
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

        cpu_str = lang["cpu"].format(cpu=cpu)
        ram_str = lang["ram"].format(ram_used=ram_used, ram_total=ram_total)
        os_str = lang["os"].format(platform=os_platform)
        version_str = lang["version"].format(os_version=os_version)
        release_str = lang["release"].format(os_release=os_release)
        uptime_str = lang["uptime"].format(uptime=uptime_time_str)

        message_str = f"{cpu_str}\n{ram_str}\n{os_str}\n{version_str}\n{release_str}\n{uptime_str}"

        await interaction.send(
            embed=Embeds.message(
                title=lang["system_class_title"],
                message=message_str,
                message_type="info",
            )
        )


async def setup(bot):

    bot.add_cog(system(bot))
