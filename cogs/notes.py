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

from config.loader import default_lang, lang
from database.guild_handler import get_guild_language
from database.note_handler import add_note
from database.note_handler import get_notes
from module.embeds.generic import Embeds
from module.embeds.noteview import Note, NotesPagination

class_namespace = "note_class_title"


class NoteSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=lang[default_lang][class_namespace])
    async def note(
        self,
        interaction: Interaction,
    ):
        return

    @note.subcommand(description=lang[default_lang]["note_create_description"])
    async def create(
        self,
        interaction: Interaction,
        title: str = SlashOption(
            name="title",
            description=lang[default_lang]["note_create_title_description"],
        ),
        description: str = SlashOption(
            name="description",
            description=lang[default_lang]["note_create_description_description"],
        ),
    ):
        note_content = {
            "title": title,
            "description": description,
            "state": 30,
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

    @note.subcommand(description=lang[default_lang]["note_list_description"])
    async def list(
        self,
        interaction: Interaction,
    ):
        await interaction.response.defer()
        notes_data = await get_notes(interaction.user.id)
        if not notes_data:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message="No notes found.",
                    message_type="warn",
                ),
                ephemeral=True,
            )
            return

        notes = [
            Note(
                note_id,
                parsed_data["title"],
                parsed_data["description"],
                parsed_data["state"],
            )
            for note_id, data in notes_data.items()
            for parsed_data in [json.loads(data)]
        ]

        pagination = NotesPagination(notes, interaction)
        await pagination.send_initial_message()

    @note.subcommand(description=lang[default_lang]["note_view_description"])
    async def view(
        self,
        interaction: Interaction,
        note_id: str = SlashOption(
            name="id",
            description=lang[default_lang]["note_view_id_description"],
            required=True,
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
        return note_id


async def setup(bot):
    bot.add_cog(NoteSystem(bot))
