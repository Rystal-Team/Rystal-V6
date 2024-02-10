import nextcord, psutil, platform, os, datetime
from module.embed import Embeds
from nextcord.ext import commands
from nextcord import Interaction

emcolor = 0x8042A9


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
        print("Processing.....")
        print("|||||||||||||||")
        print("Bot has Successfully logged onto nextcord...")
        print("Successfully logged in as {0.user}...".format(self.bot))

    @nextcord.slash_command(description="🤖 | Pong!")
    async def ping(self, interaction: Interaction):
        ping = round((self.bot.latency) * 1000)

        await interaction.send(
            embed=Embeds.message(
                title="🏓 | Pong!", message=f"{ping}ms", message_type="info"
            )
        )

    @nextcord.slash_command(description="🤖 | Pong!")
    async def info(self, interaction: Interaction):
        cpu = psutil.cpu_percent()
        ram_used, ram_total = psutil.virtual_memory()[3], psutil.virtual_memory()[0]
        os_platform, os_version, os_time = platform.system(), platform.version()

        await interaction.send()


async def setup(bot):
    bot.add_cog(system(bot))
