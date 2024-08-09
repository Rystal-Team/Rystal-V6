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

from config.loader import default_language, lang, type_color
from database.guild_handler import get_guild_language
from database.note_handler import add_note, remove_note
from database.note_handler import fetch_note, get_notes
from module.embeds.generic import Embeds
from module.embeds.noteview import Note, NotesPagination, NoteState, NoteStateView

class_namespace = "note_class_title"


class NoteSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=lang[default_language][class_namespace])
    async def note(
        self,
        interaction: Interaction,
    ):
        return

    @note.subcommand(description=lang[default_language]["note_create_description"])
    async def create(
        self,
        interaction: Interaction,
        title: str = SlashOption(
            name="title",
            description=lang[default_language]["note_create_title_description"],
        ),
        description: str = SlashOption(
            name="description",
            description=lang[default_language]["note_create_description_description"],
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
                message=lang[await get_guild_language(interaction.guild.id)][
                    "note_create_success"
                ],
                message_type="success",
            ),
            ephemeral=True,
        )

    @note.subcommand(description=lang[default_language]["note_list_description"])
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
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "note_not_found"
                    ],
                    message_type="error",
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

    @note.subcommand(description=lang[default_language]["note_view_description"])
    async def view(
        self,
        interaction: Interaction,
        note_id: str = SlashOption(
            name="id",
            description=lang[default_language]["note_view_id_description"],
            required=True,
        ),
    ):
        await interaction.response.defer()
        note_data = await fetch_note(interaction.user.id, note_id)

        if note_data is None:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "note_not_found"
                    ],
                    message_type="error",
                ),
                ephemeral=True,
            )
            return

        note_data = json.loads(note_data)
        guild_lang = await get_guild_language(interaction.guild.id)

        def map_state_to_text(state):
            state_mapping = {
                NoteState.UNBEGUN.value: lang[guild_lang]["note_state_unbegun"],
                NoteState.STALLED.value: lang[guild_lang]["note_state_stalled"],
                NoteState.ONGOING.value: lang[guild_lang]["note_state_ongoing"],
                NoteState.FINISHED.value: lang[guild_lang]["note_state_finished"],
            }
            return state_mapping.get(state, "Unknown")

        embed = nextcord.Embed(
            title=lang[guild_lang][class_namespace],
            description=lang[guild_lang]["note_view_details"].format(
                title=note_data["title"], message=note_data["description"]
            ),
            color=type_color["info"],
        )
        embed.add_field(
            name=lang[guild_lang]["note_state_title"],
            value=map_state_to_text(note_data["state"]),
            inline=False,
        )
        view = NoteStateView(note_id, interaction.user.id, guild_lang)
        message = await interaction.followup.send(
            embed=embed, view=view, ephemeral=False
        )
        view.message = message

    @note.subcommand(description=lang[default_language]["note_remove_description"])
    async def remove(
        self,
        interaction: Interaction,
        note_id: str = SlashOption(
            name="id",
            description=lang[default_language]["note_remove_id_description"],
            required=True,
        ),
    ):
        await interaction.response.defer()
        success = await remove_note(interaction.user.id, note_id)
        if success:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "note_remove_success"
                    ],
                    message_type="success",
                ),
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "note_not_found"
                    ],
                    message_type="error",
                ),
                ephemeral=True,
            )


async def setup(bot):
    bot.add_cog(NoteSystem(bot))
