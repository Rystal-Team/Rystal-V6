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

import nextcord


class Note:
    def __init__(self, note_id: int, title: str, message: str, state: int):
        self.id = note_id
        self.title = title
        self.message = message
        self.state = 30


class NotesEmbed:
    @staticmethod
    def create_embed(notes, page, total_pages):
        embed = nextcord.Embed(
            title="Notes List", description=f"Page {page} of {total_pages}"
        )
        for note in notes:
            embed.add_field(name=f"ID: {note.id}", value=note.title, inline=False)
        return embed


class NotesPagination(nextcord.ui.View):
    def __init__(self, notes, interaction: nextcord.Interaction):
        super().__init__(timeout=180)
        self.notes = list(notes)
        self.interaction = interaction
        self.index = 0
        self.notes_per_page = 10
        self.total_pages = (len(self.notes) - 1) // self.notes_per_page + 1

    async def send_initial_message(self):
        embed = self.create_embed()
        self.message = await self.interaction.followup.send(embed=embed, view=self)

    def create_embed(self):
        start = self.index * self.notes_per_page
        end = start + self.notes_per_page
        notes_slice = self.notes[start:end]
        return NotesEmbed.create_embed(notes_slice, self.index + 1, self.total_pages)

    @nextcord.ui.button(label="◀️", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        if self.index > 0:
            self.index -= 1
            await self.update_message()

    @nextcord.ui.button(label="▶️", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.Button, interaction: nextcord.Interaction):
        if self.index < self.total_pages - 1:
            self.index += 1
            await self.update_message()

    async def update_message(self):
        embed = self.create_embed()
        await self.message.edit(embed=embed, view=self)

    async def on_timeout(self):
        await self.message.edit(view=None)
