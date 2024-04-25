from typing import Callable, Optional

import nextcord

from config.config import lang
from database.guild_handler import get_guild_language


class Pagination(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.follow_up = None
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1

        super().__init__(timeout=180)

    async def navegate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            follow_up_msg: nextcord.Message = await self.interaction.followup.send(
                embed=emb
            )

            self.follow_up = follow_up_msg
        elif self.total_pages > 1:
            self.update_buttons()
            follow_up_msg: nextcord.Message = await self.interaction.followup.send(
                embed=emb, view=self
            )

            self.follow_up = follow_up_msg

    async def edit_page(self, interaction: nextcord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, embed=emb, view=self
        )

    def update_buttons(self):
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    @nextcord.ui.button(emoji="◀️", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer()
        self.index -= 1
        await self.edit_page(interaction)

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        self.index += 1
        await self.edit_page(interaction)

    @nextcord.ui.button(emoji="⏭️", style=nextcord.ButtonStyle.blurple)
    async def end(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        if self.index <= self.total_pages // 2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        # remove buttons on timeout
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, view=None
        )

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1


class Description_Pagination(nextcord.ui.View):
    def __init__(self, interaction: nextcord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = nextcord.Embed(
                description=lang[await get_guild_language(self.interaction.guild.id)][
                    "author_only_interactions"
                ],
                color=16711680,
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False

    async def navegate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.interaction.response.send_message(embed=emb)
        elif self.total_pages > 1:
            self.update_buttons()
            await self.interaction.response.send_message(embed=emb, view=self)

    async def edit_page(self, interaction: nextcord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(embed=emb, view=self)

    def update_buttons(self):
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    @nextcord.ui.button(emoji="◀️", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer()
        self.index -= 1
        await self.edit_page(interaction)

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        self.index += 1
        await self.edit_page(interaction)

    @nextcord.ui.button(emoji="⏭️", style=nextcord.ButtonStyle.blurple)
    async def end(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        if self.index <= self.total_pages // 2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)
