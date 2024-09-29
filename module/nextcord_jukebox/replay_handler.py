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

from datetime import datetime

from . import LogHandler
from .event_manager import EventManager
from .exceptions import NothingPlaying
from .utils import get_video_id


class ReplayHandler(EventManager):
    """
    ReplayHandler class to handle replay events and log them to a database.

    Attributes:
        manager (EventManager): The event manager instance.
        database: The database instance from the manager.
    """

    def __init__(self, manager):
        """
        Initializes the ReplayHandler with the given manager.

        Args:
            manager (EventManager): The event manager instance.
        """
        self.manager = manager
        self.database = manager.database

    @EventManager.listener
    async def track_start(self, player, interaction, before, after):
        """
        Event listener for when a track starts playing.

        Args:
            player: The player instance.
            interaction: The interaction instance.
            before: The state before the track started.
            after: The state after the track started.
        """
        for member in player.members:
            if member == player.bot or member is None:
                continue
            now_playing = await player.now_playing()
            video_id = await get_video_id(now_playing.url)
            LogHandler.info(f"Adding replay entry for {member.global_name}")
            await self.database.add_replay_entry(
                str(member.id), (datetime.now().isoformat()), video_id
            )

    @EventManager.listener
    async def member_joined_voice(self, player, member):
        """
        Event listener for when a member joins a voice channel.

        Args:
            player: The player instance.
            member: The member who joined the voice channel.
        """
        if member == player.bot or member is None:
            return
        try:
            now_playing = await player.now_playing()
        except NothingPlaying:
            return
        video_id = await get_video_id(now_playing.url)
        LogHandler.info(f"Adding replay entry for {member.global_name}")
        await self.database.add_replay_entry(
            str(member.id), (datetime.now().isoformat()), video_id
        )


def attach(manager):
    """
    Attaches the ReplayHandler to the EventManager.

    Args:
        manager: EventManager to attach manager.

    Returns:
        ReplayHandler: The attached handler instance.
    """
    handler = ReplayHandler(manager)
    EventManager.attach(handler)
    return handler
