"""
This module defines classes for handling search and pagination in a Nextcord bot.

Classes:
    Search: A modal for inputting search queries.
    QueueViewer: A view for handling pagination of results in a Nextcord bot.

Methods:
    Search.__init__(self, page_view): Initializes the Search modal with a reference to the page view.
    Search.callback(self, interaction: nextcord.Interaction): Handles the search query input and updates the page view.

    QueueViewer.__init__(self, interaction: nextcord.Interaction, get_page: Callable): Initializes the QueueViewer view.
    QueueViewer.navegate(self): Navigates to the initial page and sends the first message.
    QueueViewer.edit_page(self): Edits the current page based on the search query and page index.
    QueueViewer.update_buttons(self): Updates the state of pagination buttons.

    QueueViewer.previous(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the previous button click.
    QueueViewer.next(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the next button click.
    QueueViewer.end(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the end button click.
    QueueViewer.search(self, button: nextcord.Button, interaction: nextcord.Interaction): Handles the search button click.
    QueueViewer.on_timeout(self): Handles the timeout event by removing pagination buttons.
    QueueViewer.compute_total_pages(total_results: int, results_per_page: int) -> int: Computes the total number of pages.
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

from config.loader import lang
from database.guild_handler import get_guild_language
from module.emoji import get_emoji


class Search(nextcord.ui.Modal):
    """
    A modal for inputting search queries.

    Attributes:
        page_view (QueueViewer): The pagination view associated with this search modal.
        search_query (nextcord.ui.TextInput): The text input field for the search query.
    """

    def __init__(self, page_view):
        """
        Initializes the Search modal with a reference to the page view.

        Args:
            page_view (QueueViewer): The pagination view associated with this search modal.
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


class SkipDropdown(nextcord.ui.Select):
    def __init__(self, queue_viewer, guild_language, player):
        super().__init__(
            placeholder=lang[guild_language]["music_skip_dropdown_placeholder"],
            min_values=1,
            max_values=1,
            options=[],
        )
        self.queue_viewer = queue_viewer
        self.player = player

    async def callback(self, interaction: nextcord.Interaction):
        if not self.values[0] == "no_result":
            await self.player.skip(index=int(self.values[0]))
            await self.queue_viewer.edit_page()


class QueueViewer(nextcord.ui.View):
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

    def __init__(self, interaction: nextcord.Interaction, get_page: Callable, player):
        """
        Initializes the QueueViewer view.

        Args:
            interaction (nextcord.Interaction): The interaction that initiated the pagination.
            get_page (Callable): The function to get the page data.
        """
        super().__init__(timeout=180)

        self.interaction = interaction
        self.follow_up = None
        self.get_page = get_page
        self.search_query = ""
        self.total_pages: Optional[int] = None
        self.index = 1
        self.guild_language = asyncio.run(get_guild_language(interaction.guild.id))
        self.player = player
        self.is_timeout = False

        self.dropdown = SkipDropdown(self, self.guild_language, self.player)
        self.add_item(self.dropdown)

    async def navegate(self):
        """Navigates to the initial page and sends the first message."""
        emb, self.total_pages, options = await self.get_page(self.index)
        self.dropdown.options = options
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
        emb, self.total_pages, options = await self.get_page(
            self.index, query=self.search_query
        )
        self.dropdown.options = options

        if self.index == 0 and self.total_pages != 0:
            self.index = 1
            await self.edit_page()
            return

        if self.index > self.total_pages:
            self.index = self.total_pages
            await self.edit_page()
            return

        self.update_buttons()
        print(emb.to_dict())
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, embed=emb, view=self
        )

    def update_buttons(self):
        """Updates the state of pagination buttons."""
        self.children[0].disabled = self.total_pages in (1, 0) or self.index in (1, 0)
        self.children[1].disabled = self.total_pages in (1, 0) or self.index in (1, 0)
        self.children[3].disabled = (
            self.index == self.total_pages or self.total_pages in (1, 0)
        )
        self.children[4].disabled = (
            self.index == self.total_pages or self.total_pages in (1, 0)
        )

    @nextcord.ui.button(
        emoji=get_emoji("double_arrow_left"), style=nextcord.ButtonStyle.secondary
    )
    async def start(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handles the end button click.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        await interaction.response.defer()
        self.index = 1
        await self.edit_page()

    @nextcord.ui.button(
        emoji=get_emoji("arrow_left"), style=nextcord.ButtonStyle.secondary
    )
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

    @nextcord.ui.button(emoji=get_emoji("search"), style=nextcord.ButtonStyle.secondary)
    async def search(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handles the search button click.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        modal = Search(self)
        await interaction.response.send_modal(modal)

    @nextcord.ui.button(
        emoji=get_emoji("arrow_right"), style=nextcord.ButtonStyle.secondary
    )
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

    @nextcord.ui.button(
        emoji=get_emoji("double_arrow_right"), style=nextcord.ButtonStyle.secondary
    )
    async def end(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Handles the end button click.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered the button click.
        """
        await interaction.response.defer()
        self.index = self.total_pages
        await self.edit_page()

    async def on_timeout(self):
        """Handles the timeout event by removing pagination buttons."""
        is_timeout = True

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
