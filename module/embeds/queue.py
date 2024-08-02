"""
This module defines classes for handling search and pagination in a Nextcord bot.

Classes:
    Search: A modal for inputting search queries.
    Pagination: A view for handling pagination of results in a Nextcord bot.

Methods:
    Search.__init__(self, page_view): Initializes the Search modal with a reference to the page view.
    Search.callback(self, interaction: nextcord.Interaction): Handles the search query input and updates the page view.

    Pagination.__init__(self, interaction: nextcord.Interaction, get_page: Callable): Initializes the Pagination view.
    Pagination.navegate(self): Navigates to the initial page and sends the first message.
    Pagination.edit_page(self): Edits the current page based on the search query and page index.
    Pagination.update_buttons(self): Updates the state of pagination buttons.

    Pagination.previous(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the previous button click.
    Pagination.next(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the next button click.
    Pagination.end(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the end button click.
    Pagination.search(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the search button click.
    Pagination.on_timeout(self): Handles the timeout event by removing pagination buttons.
    Pagination.compute_total_pages(total_results: int, results_per_page: int) -> int: Computes the total number of pages.
"""

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

import asyncio
from typing import Callable, Optional

import nextcord

from config.config import lang
from database.guild_handler import get_guild_language


class Search(nextcord.ui.Modal):
    """
    A modal for inputting search queries.

    Attributes:
        page_view (Pagination): The pagination view associated with this search modal.
        search_query (nextcord.ui.TextInput): The text input field for the search query.
    """

    def __init__(self, page_view):
        """
        Initializes the Search modal with a reference to the page view.

        Args:
            page_view (Pagination): The pagination view associated with this search modal.
        """
        super().__init__(
            lang[page_view.guild_language]["queue_search"],
            timeout=2 * 60,
        )

        self.page_view = page_view

        self.search_query = nextcord.ui.TextInput(
            label=lang[page_view.guild_language]["queue_query"],
            style=nextcord.TextInputStyle.paragraph,
            placeholder=lang[page_view.guild_language]["queue_serach_query"],
            required=False,
            max_length=100,
        )
        self.add_item(self.search_query)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        """
        Handles the search query input and updates the page view.

        Args:
            interaction (nextcord.Interaction): The interaction that triggered the callback.
        """
        await interaction.response.defer()
        self.page_view.search_query = self.search_query.value
        await self.page_view.edit_page()


class Pagination(nextcord.ui.View):
    """
    A view for handling pagination of results in a Nextcord bot.

    Attributes:
        interaction (nextcord.Interaction): The interaction that initiated the pagination.
        follow_up (Optional[nextcord.Message]): The follow-up message for pagination.
        get_page (Callable): The function to get the page data.
        search_query (str): The current search query.
        total_pages (Optional[int]): The total number of pages.
        index (int): The current page index.
        guild_language (str): The language of the guild.
    """

    def __init__(self, interaction: nextcord.Interaction, get_page: Callable):
        """
        Initializes the Pagination view.

        Args:
            interaction (nextcord.Interaction): The interaction that initiated the pagination.
            get_page (Callable): The function to get the page data.
        """
        self.interaction = interaction
        self.follow_up = None
        self.get_page = get_page
        self.search_query = ""
        self.total_pages: Optional[int] = None
        self.index = 1
        self.guild_language = asyncio.run(get_guild_language(interaction.guild.id))

        super().__init__(timeout=180)

    async def navegate(self):
        """Navigates to the initial page and sends the first message."""
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

    async def edit_page(self):
        """Edits the current page based on the search query and page index."""
        emb, self.total_pages = await self.get_page(self.index, query=self.search_query)

        if self.index == 0 and self.total_pages != 0:
            self.index = 1
            await self.edit_page()
            return

        if self.index > self.total_pages:
            self.index = self.total_pages
            await self.edit_page()
            return

        self.update_buttons()
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, embed=emb, view=self
        )

    def update_buttons(self):
        """Updates the state of pagination buttons."""
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index in (1, 0)
        self.children[1].disabled = self.total_pages in (self.index, 0)
        self.children[2].disabled = self.total_pages == 0

    @nextcord.ui.button(emoji="◀️", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        """
        Handles the previous button click.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        await interaction.response.defer()
        self.index -= 1
        await self.edit_page()

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handles the next button click.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        await interaction.response.defer()
        self.index += 1
        await self.edit_page()

    @nextcord.ui.button(emoji="⏭️", style=nextcord.ButtonStyle.blurple)
    async def end(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handles the end button click.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        await interaction.response.defer()
        if self.index <= self.total_pages // 2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page()

    @nextcord.ui.button(emoji="🔎", style=nextcord.ButtonStyle.blurple)
    async def search(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handles the search button click.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        modal = Search(self)
        await interaction.response.send_modal(modal)

    async def on_timeout(self):
        """Handles the timeout event by removing pagination buttons."""
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, view=None
        )

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        """
        Computes the total number of pages.

        Args:
            total_results (int): The total number of results.
            results_per_page (int): The number of results per page.

        Returns:
            int: The total number of pages.
        """
        return ((total_results - 1) // results_per_page) + 1
