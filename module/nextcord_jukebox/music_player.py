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
from typing import Callable, Optional, Union

import yt_dlp
from nextcord import Interaction

from .enums import LOOPMODE
from .song import Song

yt_dlp.utils.bug_reports_message = lambda: ""
ytdlp = yt_dlp.YoutubeDL(
    {
        "format": "bestaudio/best",
        "noplaylist": True,
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
        "source_address": "0.0.0.0",
        "forceip": "4",
        "skip_download": True,
        "extract_flat": True,
        "default_search": "auto",
    }
)


class MusicPlayer:
    """
    A class to handle music playback within a voice channel for a Discord bot.

    This class provides functionalities to manage and control music playback, including queuing songs, managing playback state, and handling voice channel connections.

    Attributes:
        loop (Optional[asyncio.BaseEventLoop]): The event loop used for async operations.
        voice (Optional[nextcord.VoiceClient]): The voice client connected to the voice channel.
        interaction (Interaction): The interaction object associated with the user request.
        bot: The bot instance to which this player is attached.
        loop_mode (LOOPMODE): The current loop mode for the player.
        _now_playing (Optional[Song]): The currently playing song.
        paused (bool): Whether the playback is currently paused.
        removed (bool): Whether the player has been removed.
        leave_when_empty (bool): Whether to leave the voice channel when the queue is empty.
        manager: The player manager instance managing this player.
        database: The database instance used for caching video metadata.
        music_queue (list[Song]): The queue of songs to be played.
        _fetching_stream (bool): Whether a stream is currently being fetched.
        _appending (bool): Whether songs are currently being appended to the queue.
        _asyncio_lock (asyncio.Lock): A lock to prevent concurrent access issues.
        _members (list): The list of members currently in the voice channel.
        ffmpeg_opts (dict): Options for FFmpeg processing.

    Methods:
        _attempt_reconnect(max_retries=5, delay=1):
            Attempts to reconnect to the voice channel if disconnected.
        _on_voice_state_update(member, before, after):
            Handles voice state updates to manage member join/leave events and bot reconnection.
        _play_func(last: Union[Song, None], new: Song):
            Plays a new song and updates the now playing state.
        _pop_queue(index: int = 1, append: bool = False):
            Removes a specified number of songs from the queue.
        _next_func(index: int = 1):
            Moves to the next song in the queue.
        _after_func(error: Union[None, Exception] = None):
            Callback function for after a song finishes playing.
        _pre_check(check_playing: bool = False, check_nowplaying: bool = False,
                   check_fetching_stream: bool = False, check_queue: bool = False,
                   check_connection: bool = True) -> Optional[bool]:
            Performs pre-checks before executing certain methods.
        pre_check(*d_args, **d_kwargs) -> Callable:
            A decorator for methods that require pre-checks before execution.
        cleanup():
            Cleans up the player by clearing the queue and disconnecting from the voice channel.
        _queue_single(video_url: str) -> Song:
            Queues a single song from a video URL.
        queue(interaction: Interaction, query: str):
            Queues a song or playlist based on a search query.
        connect(interaction: Interaction) -> Optional[bool]:
            Connects the bot to a voice channel if not already connected.
        change_loop_mode(mode: LOOPMODE) -> LOOPMODE:
            Changes the loop mode for the player.
        resume(forced=False):
            Resumes playback of the currently paused song.
        pause(forced=False):
            Pauses playback of the currently playing song.
        skip(index: int = 1):
            Skips the current song and optionally advances in the queue.
        previous(index: int = 1):
            Moves to the previous song in the queue.
        shuffle():
            Shuffles the order of songs in the queue.
        now_playing() -> Song:
            Returns the currently playing song.
        current_queue() -> list:
            Returns the current queue of songs.
        stop(disconnect=True) -> bool:
            Stops playback and optionally disconnects from the voice channel.
        remove(index=0) -> Optional[Song]:
            Removes a song from the queue based on its index.
    """

    def __init__(
        self, manager, interaction: Interaction, bot, ffmpeg_opts=None
    ) -> None:
        """
        Initializes the MusicPlayer with the given interaction and bot instances.

        Args:
            manager (PlayerManager): The player manager instance managing this player.
            interaction (Interaction): The interaction object containing information about the user and the guild.
            bot: The bot instance to which this player is attached.
            ffmpeg_opts (dict, optional): Options for FFmpeg. Defaults to None.
        """
        # Initialization code...

    async def _attempt_reconnect(self, max_retries=5, delay=1):
        """
        Attempts to reconnect to the voice channel if disconnected.

        Args:
            max_retries (int, optional): The maximum number of reconnection attempts. Defaults to 5.
            delay (int, optional): The delay between reconnection attempts in seconds. Defaults to 1.

        Returns:
            bool: True if reconnection was successful, False otherwise.
        """
        # Reconnection logic...

    async def _on_voice_state_update(self, member, before, after):
        """
        Handles voice state updates to manage member join/leave events and bot reconnection.

        Args:
            member (nextcord.Member): The member whose voice state has changed.
            before (nextcord.VoiceState): The voice state before the update.
            after (nextcord.VoiceState): The voice state after the update.
        """
        # Voice state update handling logic...

    async def _play_func(self, last: Union[Song, None], new: Song):
        """
        Plays a new song and updates the now playing state.

        Args:
            last (Optional[Song]): The last song that was playing.
            new (Song): The new song to be played.

        Raises:
            Exception: If playback fails.
        """
        # Playback logic...

    async def _pop_queue(self, index: int = 1, append: bool = False):
        """
        Removes a specified number of songs from the queue.

        Args:
            index (int, optional): The number of songs to remove. Defaults to 1.
            append (bool, optional): Whether to append the removed songs to the end of the queue. Defaults to False.
        """
        # Queue removal logic...

    async def _next_func(self, index: int = 1):
        """
        Moves to the next song in the queue.

        Args:
            index (int, optional): The number of songs to skip. Defaults to 1.

        Returns:
            tuple: The last song played and the new song to be played.
        """
        # Move to next song logic...

    async def _after_func(self, error: Union[None, Exception] = None):
        """
        Callback function for after a song finishes playing.

        Args:
            error (Union[None, Exception], optional): An exception if one occurred. Defaults to None.
        """
        # After function logic...

    async def _pre_check(
        self,
        check_playing: bool = False,
        check_nowplaying: bool = False,
        check_fetching_stream: bool = False,
        check_queue: bool = False,
        check_connection: bool = True,
    ) -> Optional[bool]:
        """
        Performs various checks before executing certain methods.

        Args:
            check_playing (bool, optional): Check if a song is currently playing. Defaults to False.
            check_nowplaying (bool, optional): Check if there is a song currently playing. Defaults to False.
            check_fetching_stream (bool, optional): Check if a stream is being fetched. Defaults to False.
            check_queue (bool, optional): Check if the queue is empty. Defaults to False.
            check_connection (bool, optional): Check if connected to a voice channel. Defaults to True.

        Returns:
            Optional[bool]: True if all checks pass, otherwise raises an exception.
        """
        # Pre-check logic...

    def pre_check(*d_args, **d_kwargs) -> Callable:
        """
        A decorator for methods requiring pre-checks.

        Args:
            *d_args: Arguments for the pre-check.
            **d_kwargs: Keyword arguments for the pre-check.

        Returns:
            Callable: The decorated function.
        """
        # Pre-check decorator logic...

    async def cleanup(self):
        """
        Cleans up the music player by clearing the queue and disconnecting from the voice channel.
        """
        # Cleanup logic...

    @pre_check()
    async def _queue_single(self, video_url: str) -> Song:
        """
        Queues a single song from a video URL.

        Args:
            video_url (str): The URL of the video to be queued.

        Returns:
            Song: The queued song.
        """
        # Queue single song logic...

    @pre_check(check_fetching_stream=True)
    async def queue(self, interaction: Interaction, query: str):
        """
        Queues a song or playlist based on a search query.

        Args:
            interaction (Interaction): The interaction object.
            query (str): The query string.

        Returns:
            Playlist or Song: The queued playlist or song.

        Raises:
            NoQueryResult: If no results are found for the query.
        """
        # Queue logic...

    @pre_check(check_connection=False)
    async def connect(self, interaction: Interaction) -> Optional[bool]:
        """
        Connects the bot to a voice channel if not already connected.

        Args:
            interaction (Interaction): The interaction object.

        Returns:
            Optional[bool]: True if connected successfully, False otherwise.
        """
        # Connect logic...

    @pre_check()
    async def change_loop_mode(self, mode: LOOPMODE) -> LOOPMODE:
        """
        Changes the loop mode for the player.

        Args:
            mode (LOOPMODE): The new loop mode.

        Returns:
            LOOPMODE: The updated loop mode.
        """
        # Change loop mode logic...

    @pre_check(check_nowplaying=True)
    async def resume(self, forced=False):
        """
        Resumes playback of the currently paused song.

        Args:
            forced (bool, optional): Whether to force resume. Defaults to False.
        """
        # Resume playback logic...

    @pre_check(check_nowplaying=True)
    async def pause(self, forced=False):
        """
        Pauses playback of the currently playing song.

        Args:
            forced (bool, optional): Whether to force pause. Defaults to False.
        """
        # Pause playback logic...

    @pre_check(check_queue=True)
    async def skip(self, index: int = 1):
        """
        Skips the current song and optionally advances in the queue.

        Args:
            index (int, optional): The number of songs to skip. Defaults to 1.
        """
        # Skip logic...

    @pre_check(check_queue=True)
    async def previous(self, index: int = 1):
        """
        Moves to the previous song in the queue.

        Args:
            index (int, optional): The number of songs to go back. Defaults to 1.
        """
        # Previous song logic...

    @pre_check(check_queue=True)
    async def shuffle(self):
        """
        Shuffles the order of songs in the queue.
        """
        # Shuffle logic...

    @pre_check(check_nowplaying=True)
    async def now_playing(self) -> Song:
        """
        Returns the currently playing song.

        Returns:
            Song: The currently playing song.
        """
        # Get currently playing song logic...

    @pre_check(check_queue=True)
    async def current_queue(self) -> list:
        """
        Returns the current queue of songs.

        Returns:
            list: The current queue of songs.
        """
        # Get current queue logic...

    @pre_check(check_nowplaying=True, check_connection=False)
    async def stop(self, disconnect=True) -> bool:
        """
        Stops playback and optionally disconnects from the voice channel.

        Args:
            disconnect (bool, optional): Whether to disconnect from the voice channel. Defaults to True.

        Returns:
            bool: True if stopped successfully, False otherwise.
        """
        # Stop playback logic...

    @pre_check(check_queue=True)
    async def remove(self, index=0) -> Optional[Song]:
        """
        Removes a song from the queue based on its index.

        Args:
            index (int, optional): The index of the song to remove. Defaults to 0.

        Returns:
            Optional[Song]: The removed song, if any.
        """
        # Remove song logic...
