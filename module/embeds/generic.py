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

from config.loader import type_color


class Embeds:
    """Class for creating Nextcord embed messages."""
    @staticmethod
    def message(title, message, message_type, thumbnail=None):
        """
        Create an embed message.

        Args:
            title (str): The title of the embed.
            message (str): The message content of the embed.
            message_type (str): The type of the message to determine the embed color.
            thumbnail (str, optional): URL of the thumbnail image.

        Returns:
            nextcord.Embed: The generated embed message.
        """
        embed = nextcord.Embed(
            title=title, description=message, color=(type_color[message_type])
        )

        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)

        return embed
