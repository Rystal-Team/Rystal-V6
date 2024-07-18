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

import json

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from config.config import lang
from database.guild_handler import get_guild_language
from database.note_handler import add_note
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
        note_content = {
            "title"      : title9,
            "description": description,
            "state"      : 30,
        }
        await interaction.response.defer()
        await add_note(interaction.user.id, json.dumps(note_content))
        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message="Note created successfully!",
                message_type="success",
            ),
            ephemeral=True,
        )

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
