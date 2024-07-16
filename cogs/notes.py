import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from config.config import lang
from database.guild_handler import get_guild_language
from module.embed import Embeds

class_namespace = "music_class_title"


class NoteSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        description="📒 | Note"
    )
    async def note(
        self,
        interaction: Interaction,
    ):
        return

    @note.subcommand(
        description="📒 | Create a new note!"
    )
    async def create(
        self,
        interaction: Interaction,
        title: str = SlashOption(name="title", description="Title of the note!"),
        description: str = SlashOption(
            name="description", description="Description of the note!"
        ),
    ):
        await interaction.response.send_message(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "not_implemented"
                ],
                message_type="warn",
            ),
            ephemeral=True,
        )
        return title, description

    @note.subcommand(
        description="📒 | Create a new note!"
    )
    async def list(
        self,
        interaction: Interaction,
    ):
        await interaction.response.send_message(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "not_implemented"
                ],
                message_type="warn",
            ),
            ephemeral=True,
        )
        return

    @note.subcommand(
        description="📒 | Create a new note!"
    )
    async def view(
        self,
        interaction: Interaction,
        title: str = SlashOption(name="title", description="Title of the note!"),
        description: str = SlashOption(
            name="description", description="Description of the note!"
        ),
    ):
        await interaction.response.send_message(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "not_implemented"
                ],
                message_type="warn",
            ),
            ephemeral=True,
        )
        return title, description


async def setup(bot):
    bot.add_cog(NoteSystem(bot))
