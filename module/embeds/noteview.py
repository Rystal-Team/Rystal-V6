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
from enum import Enum, unique

import nextcord

from config.loader import lang, type_color
from database.guild_handler import get_guild_language
from database.note_handler import fetch_note, remove_note, update_note_state

class_namespace = "note_class_title"


@unique
class NoteState(Enum):
    """Enum representing the state of a note."""

    UNBEGUN = 30
    STALLED = 31
    ONGOING = 32
    FINISHED = 33


def map_state_to_text(guild_lang, state):
    """
    Map the state value to the corresponding text.

    Args:
        guild_lang (str): The language of the guild.
        state (int): The state value.

    Returns:
        str: The corresponding text for the state.
    """
    state_mapping = {
        NoteState.UNBEGUN.value : lang[guild_lang]["note_state_unbegun"],
        NoteState.STALLED.value : lang[guild_lang]["note_state_stalled"],
        NoteState.ONGOING.value : lang[guild_lang]["note_state_ongoing"],
        NoteState.FINISHED.value: lang[guild_lang]["note_state_finished"],
    }
    return state_mapping.get(state, "Unknown")


def map_state_to_emoji(state):
    """
    Map the state value to the corresponding emoji.

    Args:
        state (int): The state value.

    Returns:
        str: The corresponding emoji for the state.
    """
    state_mapping = {
        NoteState.UNBEGUN.value : "❔",
        NoteState.STALLED.value : "🛑",
        NoteState.ONGOING.value : "🕰️",
        NoteState.FINISHED.value: "✅",
    }
    return state_mapping.get(state, "❔")


class Note:
    """
    A class representing a note.

    Attributes:
        id (int): The ID of the note.
        title (str): The title of the note.
        message (str): The message content of the note.
        state (int): The state of the note.
    """

    def __init__(self, note_id: int, title: str, message: str, state: int):
        """
        Initialize a Note instance.

        Args:
            note_id (int): The ID of the note.
            title (str): The title of the note.
            message (str): The message content of the note.
            state (int): The state of the note.
        """
        self.id = note_id
        self.title = title
        self.message = message
        self.state = state


class NotesEmbed:
    """A class for creating embeds for notes."""

    @staticmethod
    def create_embed(notes, page, total_pages, guild_lang):
        """
        Create an embed for a list of notes.

        Args:
            notes (list): The list of notes.
            page (int): The current page number.
            total_pages (int): The total number of pages.
            guild_lang (str): The language of the guild.

        Returns:
            nextcord.Embed: The created embed.
        """
        embed = nextcord.Embed(
            title=lang[guild_lang]["note_list_title"],
            description=lang[guild_lang]["note_list_footer"].format(
                page=page, total_pages=total_pages
            ),
            color=type_color["list"],
        )

        for note in notes:
            embed.add_field(
                name=f"{note.title}【{map_state_to_emoji(note.state)}】",
                value=f"ID: {note.id}",
                inline=False,
            )
        return embed


class NotesPagination(nextcord.ui.View):
    """
    A view for paginating through notes.

    Attributes:
        notes (list): The list of notes.
        interaction (nextcord.Interaction): The interaction that triggered the view.
        index (int): The current page index.
        notes_per_page (int): The number of notes per page.
        total_pages (int): The total number of pages.
    """

    def __init__(self, notes, interaction: nextcord.Interaction):
        """
        Initialize a NotesPagination instance.

        Args:
            notes (list): The list of notes.
            interaction (nextcord.Interaction): The interaction that triggered the view.
        """
        super().__init__(timeout=180)
        self.notes = list(notes)
        self.interaction = interaction
        self.index = 0
        self.notes_per_page = 10
        self.total_pages = (len(self.notes) - 1) // self.notes_per_page + 1
        self.author_id = interaction.user.id

    async def send_initial_message(self):
        """Send the initial message with the first page of notes."""
        self.guild_lang = await get_guild_language(self.interaction.guild.id)
        embed = self.create_embed()
        self.update_buttons()
        self.message = await self.interaction.followup.send(embed=embed, view=self)

    def create_embed(self):
        """
        Create an embed for the current page of notes.

        Returns:
            nextcord.Embed: The created embed.
        """
        start = self.index * self.notes_per_page
        end = start + self.notes_per_page
        notes_slice = self.notes[start:end]
        return NotesEmbed.create_embed(
            notes_slice,
            self.index + 1,
            self.total_pages,
            self.guild_lang,
        )

    @nextcord.ui.button(label="◀️", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        """
        Handle the previous page button click.

        Args:
            button (nextcord.ui.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        if interaction.user.id == self.author_id:
            if self.index > 0:
                self.index -= 1
                await self.update_message()
        else:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title=lang[self.guild_lang][class_namespace],
                    description=lang[self.guild_lang]["interaction_author_only"],
                    color=type_color["warn"],
                ),
                ephemeral=True,
            )

    @nextcord.ui.button(label="▶️", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handle the next page button click.

        Args:
            button (nextcord.ui.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        if interaction.user.id == self.author_id:
            if self.index < self.total_pages - 1:
                self.index += 1
                await self.update_message()
        else:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title=lang[self.guild_lang][class_namespace],
                    description=lang[self.guild_lang]["interaction_author_only"],
                    color=type_color["warn"],
                ),
                ephemeral=True,
            )

    async def update_message(self):
        """Update the message with the current page of notes."""
        embed = self.create_embed()
        self.update_buttons()
        await self.message.edit(embed=embed, view=self)

    def update_buttons(self):
        """Update the state of the pagination buttons."""
        self.children[0].disabled = self.index == 0
        self.children[1].disabled = self.index == self.total_pages - 1

    async def on_timeout(self):
        """Handle the timeout event for the view."""
        await self.message.edit(view=None)


class NoteStateView(nextcord.ui.View):
    """
    A view for handling note state interactions.

    Attributes:
        note_id (int): The ID of the note.
        user_id (int): The ID of the user.
        guild_lang (str): The language of the guild.
        message (nextcord.Message): The message to edit.
    """

    def __init__(self, note_id, user_id, guild_lang):
        """
        Initialize a NoteStateView instance.

        Args:
            note_id (int): The ID of the note.
            user_id (int): The ID of the user.
            guild_lang (str): The language of the guild.
        """
        super().__init__(timeout=180)
        self.note_id = note_id
        self.user_id = user_id
        self.guild_lang = guild_lang
        self.message = None

    async def update_state(self, interaction: nextcord.Interaction, new_state: int):
        """
        Update the state of the note.

        Args:
            interaction (nextcord.Interaction): The interaction that triggered the state update.
            new_state (int): The new state of the note.
        """
        await update_note_state(self.user_id, self.note_id, new_state)
        note_data = await fetch_note(self.user_id, self.note_id)
        note_data = json.loads(note_data)

        embed = nextcord.Embed(
            title=lang[self.guild_lang][class_namespace],
            description=lang[self.guild_lang]["note_view_details"].format(
                title=note_data["title"], message=note_data["description"]
            ),
            color=type_color["info"],
        )
        embed.add_field(
            name=lang[self.guild_lang]["note_state_title"],
            value=f"{map_state_to_text(self.guild_lang, note_data['state'])} 【{map_state_to_emoji(note_data['state'])}】",
            inline=False,
        )
        await self.message.edit(embed=embed, view=self)
        return new_state

    @nextcord.ui.button(label="🛑", style=nextcord.ButtonStyle.red)
    async def stalled(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handle the stalled state button click.

        Args:
            button (nextcord.ui.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        if interaction.user.id == self.user_id:
            await self.update_state(interaction, NoteState.STALLED.value)
        else:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title=lang[self.guild_lang][class_namespace],
                    description=lang[self.guild_lang]["interaction_author_only"],
                    color=type_color["warn"],
                ),
                ephemeral=True,
            )

    @nextcord.ui.button(label="🕰️", style=nextcord.ButtonStyle.blurple)
    async def ongoing(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handle the ongoing state button click.

        Args:
            button (nextcord.ui.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        if interaction.user.id == self.user_id:
            await self.update_state(interaction, NoteState.ONGOING.value)
        else:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title=lang[self.guild_lang][class_namespace],
                    description=lang[self.guild_lang]["interaction_author_only"],
                    color=type_color["warn"],
                ),
                ephemeral=True,
            )

    @nextcord.ui.button(label="✅", style=nextcord.ButtonStyle.green)
    async def finished(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        """
        Handle the finished state button click.

        Args:
            button (nextcord.ui.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        if interaction.user.id == self.user_id:
            await self.update_state(interaction, NoteState.FINISHED.value)
        else:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title=lang[self.guild_lang][class_namespace],
                    description=lang[self.guild_lang]["interaction_author_only"],
                    color=type_color["warn"],
                ),
                ephemeral=True,
            )

    @nextcord.ui.button(label="🗑️", style=nextcord.ButtonStyle.danger)
    async def remove(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handle the remove note button click.

        Args:
            button (nextcord.ui.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        if interaction.user.id == self.user_id:
            success = await remove_note(self.user_id, str(self.note_id))
            if success:
                await self.message.delete()
                await interaction.response.send_message(
                    lang[self.guild_lang]["note_remove_success"], ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    lang[self.guild_lang]["note_remove_failure"], ephemeral=True
                )
        else:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title=lang[self.guild_lang][class_namespace],
                    description=lang[self.guild_lang]["interaction_author_only"],
                    color=type_color["warn"],
                ),
                ephemeral=True,
            )

    async def on_timeout(self):
        """Handle the timeout event for the view."""
        await self.message.edit(view=None)
