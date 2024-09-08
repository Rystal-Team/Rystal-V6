"""
EXPERIMENTS
Might not be implemented as a feature
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

from typing import Callable

import nextcord
from module.embeds.generic import Embeds
from module.games.roulette import Roulette, RouletteResult
from module.split_str import split_string
from nextcord import SelectOption
from nextcord.ui import Select, View


class DropdownSelector(Select):
    """
    A dropdown menu selector for Nextcord interactions.

    Attributes:
        options (list): List of options to display in the dropdown.
        placeholder (str): Placeholder text displayed when no option is selected.
        callback_func (Callable, optional): Callback function for synchronous operations.
        async_callback_func (Callable, optional): Callback function for asynchronous operations.
    """

    def __init__(
        self,
        options: list,
        placeholder: str = "Select a language",
        callback: Callable = None,
        async_callback: Callable = None,
    ):
        """
        Initialize the dropdown selector.

        Args:
            options (list): List of options to display in the dropdown.
            placeholder (str, optional): Placeholder text displayed when no option is selected.
            callback (Callable, optional): Callback function for synchronous operations.
            async_callback (Callable, optional): Callback function for asynchronous operations.
        """
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=[SelectOption(label=option, value=option) for option in options],
        )
        self.callback_func = callback
        self.async_callback_func = async_callback

    async def callback(self, interaction: nextcord.Interaction):
        """
        Callback function triggered when an option is selected.

        Args:
            interaction (nextcord.Interaction): The interaction that triggered the callback.
        """
        await interaction.response.defer(with_message=True)
        selected_option = self.values[0]
        if self.async_callback_func:
            await self.async_callback_func(self, selected_option)
        if self.callback_func:
            self.callback_func(self, selected_option)


class LyricsSelectorView(View):
    """
    A view for selecting lyrics language and displaying them.

    Attributes:
        options (list): List of language options for lyrics.
        placeholder (str): Placeholder text displayed in the dropdown selector.
        captions (dict): Dictionary mapping languages to their captions/transcripts.
        class_namespace (str): Namespace for the music class title.
    """

    def __init__(
        self,
        options: list,
        placeholder: str,
        captions: dict = None,
    ):
        """
        Initialize the lyrics selector view.

        Args:
            options (list): List of language options for lyrics.
            placeholder (str): Placeholder text displayed in the dropdown selector.
            captions (dict, optional): Dictionary mapping languages to their captions/transcripts.
        """
        if captions is None:
            captions = {}
        super().__init__()
        self.options = options
        self.placeholder = placeholder
        self.captions = captions
        self.class_namespace = "music_class_title"

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        """
        Check if the interaction is allowed based on the user.

        Args:
            interaction (nextcord.Interaction): The interaction to check.

        Returns:
            bool: True if the interaction is allowed, False otherwise.
        """
        return interaction.user == self.author

    async def on_selected(self, _, lang):
        """
        Handle the selection of a language option and display lyrics.

        Args:
            _ (DropdownSelector): The dropdown selector instance.
            lang (str): The selected language option.
        """
        lyrics_string = ""
        for line in self.captions[lang].transcript:
            line_text = line.get("text", "")
            lyrics_string = f"{lyrics_string}\n{line_text}"

        lyrics_chunks = split_string(lyrics_string, max_length=4096)
        for chunk in lyrics_chunks:
            await self.channel.send(
                embed=Embeds.message(
                    title="Lyrics",
                    message=chunk,
                    message_type="info",
                )
            )

    async def start(self, interaction: nextcord.Interaction):
        """
        Start the lyrics selector view.

        Args:
            interaction (nextcord.Interaction): The interaction that triggered the view.
        """
        self.author = interaction.user
        self.channel = interaction.channel
        self.interaction = interaction
        dropdown = DropdownSelector(
            options=self.options,
            placeholder=self.placeholder,
            async_callback=self.on_selected,
        )
        self.add_item(dropdown)
        await interaction.followup.send("Selector", view=self)
