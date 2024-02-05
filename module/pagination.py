import nextcord
from typing import Callable, Optional


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
        self, interaction: nextcord.Interaction, button: nextcord.Button
    ):
        self.index -= 1
        await self.edit_page(interaction)

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.blurple)
    async def next(self, interaction: nextcord.Interaction, button: nextcord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @nextcord.ui.button(emoji="⏭️", style=nextcord.ButtonStyle.blurple)
    async def end(self, interaction: nextcord.Interaction, button: nextcord.Button):
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
