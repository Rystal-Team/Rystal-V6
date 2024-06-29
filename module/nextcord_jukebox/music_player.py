"""
MusicPlayer is responsible for managing the playback of songs in a voice channel. It handles operations like connecting to a voice channel, playing, pausing, skipping, and managing the music queue. The class uses YouTube-DL to extract audio sources and supports functionalities like looping and shuffling the playlist.

Attributes:
    interaction (Interaction): The interaction object containing information about the user and the guild.
    bot: The bot instance to which the MusicPlayer is attached.
    loop_mode (loop_mode): The current looping mode of the player (off, single, or all).
    _now_playing (Song or None): The currently playing song.
    paused (bool): Indicates if the player is currently paused.
    removed (bool): Indicates if the player has been removed.
    leave_when_empty (bool): Indicates if the player should leave the voice channel when the queue is empty.
    music_queue (list): The queue of songs to be played.
    _fetching_stream (bool): Indicates if the player is currently fetching a stream.
    _appending (bool): Indicates if the player is currently appending to the queue.
    ffmpeg_opts (dict): Options for FFmpeg.

Methods:
    _on_voice_state_update(member, before, after):
        Handles voice state updates, resuming playback if necessary.

    _play_func(last, new):
        Plays the next song in the queue.

    _pop_queue(index=1, append=False):
        Removes songs from the queue.

    _next_func(index=1):
        Moves to the next song in the queue.

    _after_func(error):
        Handles actions after a song finishes playing.

    _pre_check(*d_args, **d_kwargs) -> Optional[bool]:
        Performs various checks before executing certain methods.

    pre_check(*d_args, **d_kwargs) -> Callable:
        A decorator for methods requiring pre-checks.

    cleanup():
        Cleans up the music player by clearing the queue and disconnecting from the voice channel.

    _queue_single(video_url):
        Queues a single song.

    queue(interaction: Interaction, query: str):
        Queues a song or playlist based on a query.

    connect(interaction: Interaction) -> Optional[bool]:
        Connects to the user's voice channel.

    change_loop_mode(mode: loop_mode) -> loop_mode:
        Changes the loop mode of the player.

    resume(forced=False):
        Resumes playback of the current song.

    pause(forced=False):
        Pauses playback of the current song.

    skip(index: int = 1):
        Skips the current song.

    shuffle():
        Shuffles the songs in the queue.

    now_playing():
        Returns the currently playing song.

    current_queue():
        Returns the current queue of songs.

    stop(disconnect=True):
        Stops playback and optionally disconnects from the voice channel.

    remove(index=0):
        Removes a song from the queue.
"""

import asyncio
import datetime
import random
import time
from typing import Callable, Optional
from urllib import parse

import yt_dlp
from nextcord import FFmpegPCMAudio, Interaction, PCMVolumeTransformer
from pytube import Playlist
from termcolor import colored
from meta_yt import Video, YouTube
from .event_manager import EventListener
from . import LogHandler
from .enums import loop_mode
from .exceptions import *
from .song import Song
from .utils import get_video_id

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


class MusicPlayer(object):
    def __init__(self, interaction: Interaction, bot, ffmpeg_opts=None) -> None:
        """
        Initializes the MusicPlayer with the given interaction and bot instances.

        Args:
            interaction (Interaction): The interaction object containing information about the user and the guild.
            bot: The bot instance to which the MusicPlayer is attached.
            ffmpeg_opts (dict, optional): Options for FFmpeg. Defaults to None.
        """
        self.interaction = interaction
        self.bot = bot

        self.loop_mode = loop_mode.off
        self._now_playing = None
        self.paused = False
        self.removed = False
        self.leave_when_empty = False

        self.music_queue = []
        self._fetching_stream = False
        self._appending = False
        self._members = []
        self.ffmpeg_opts = ffmpeg_opts or {
            "options": "-vn",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0",
        }

    async def _attempt_reconnect(self, max_retries=5, delay=1):
        """
        Reconnect to the voice channel.
        """
        for attempt in range(max_retries):
            try:
                await self.voice.connect()
                print(colored("Reconnected to the voice channel.", "green"))
                return
            except Exception as e:
                print(
                    colored(f"Reconnection attempt {attempt + 1} failed: {e}", "yellow")
                )
                await asyncio.sleep(delay)

    async def _on_voice_state_update(self, member, before, after):
        """
        Handles voice state updates, resuming playback if necessary.

        Args:
            member (Member): The member whose voice state has been updated.
            before (VoiceState): The previous voice state.
            after (VoiceState): The new voice state.
        """

        if member == self.bot.user:
            return

        if not self.voice or not self.voice.is_connected():
            print(colored("Bot is disconnected. Attempting to reconnect...", "yellow"))
            await self._attempt_reconnect()

        elif not self.paused:
            try:
                await self.resume(forced=True)
            except Exception as e:
                print(colored(f"Failed to resume playback: {e}", "red"))

        if not self.voice or not self.voice.is_connected():
            print(colored("Failed to reconnect after multiple attempts.", "red"))
        self._members = self.voice.channel.members

    async def _play_func(self, last, new):
        """
        Plays the next song in the queue.

        Args:
            last (Song): The last song that was played.
            new (Song): The new song to be played.
        """
        try:
            if self.interaction.guild.voice_client:
                timer = time.time()
                print(colored(f"Extracting Song... {new.title}", "dark_grey"))

                data = await self.loop.run_in_executor(
                    None,
                    lambda: ytdlp.extract_info(new.url, download=False),
                )
                source_url = data["url"]
                new.source_url = source_url

                audio_source = FFmpegPCMAudio(source_url, **self.ffmpeg_opts)
                self.voice.play(
                    PCMVolumeTransformer(audio_source),
                    after=lambda error: self._after_func(error),
                )

                self._now_playing = new
                await self._now_playing.start()

                print(colored(f"[PLAYING] {new.title}", "light_blue"))

                expire_unix_time = parse.parse_qs(parse.urlparse(source_url).query)[
                    "expire"
                ][0]
                expire_time = datetime.datetime.fromtimestamp(int(expire_unix_time))
                print(
                    colored(
                        f"Queue Source (Expire: {expire_time}):\n{source_url}", "dark_grey"
                    )
                )

                print(colored(f"Time taken: {time.time() - timer}", "dark_grey"))

                await EventListener.fire("track_start", self, self.interaction, last, new)
        except Exception as e:
            LogHandler.error(f"Failed to play track (If this is due to player not in voice because it gets disconnected when queuing, you can ignore this): {e}")

    async def _pop_queue(self, index: int = 1, append: bool = False):
        """
        Removes songs from the queue.

        Args:
            index (int, optional): The number of songs to remove. Defaults to 1.
            append (bool, optional): Whether to append the removed songs to the end of the queue. Defaults to False.
        """
        for _ in range(index):
            last = self.music_queue.pop(0)
            if append:
                self.music_queue.append(last)

    async def _next_func(self, index: int = 1):
        """
        Moves to the next song in the queue.

        Args:
            index (int, optional): The index of the song to move to. Defaults to 1.

        Returns:
            tuple: The last song played and the new song to be played.
        """
        last = self._now_playing

        if self.loop_mode == loop_mode.off:
            await self._pop_queue(index)
        elif self.loop_mode == loop_mode.all:
            await self._pop_queue(index, append=True)

        if len(self.music_queue) > 0:
            new = self.music_queue[0]
            await self._play_func(last, new)
        else:
            self._now_playing = None
            await EventListener.fire("queue_ended", self, self.interaction)

        return last, new

    async def _after_func(self, error):
        """
        Handles actions after a song finishes playing.

        Args:
            error (Exception): The error encountered, if any.
        """
        if error:
            raise error
        else:
            if len(self.music_queue) > 0:
                await self._next_func(index=1)
            else:
                self._now_playing = None
                await EventListener.fire("queue_ended", self, self.interaction)

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
        if check_nowplaying:
            if self._now_playing == None:
                raise NothingPlaying
        if check_connection:
            if (
                not self.interaction.guild.voice_client
                or not self.interaction.guild.voice_client.is_connected()
            ):
                raise NotConnected
        if check_fetching_stream:
            if self._fetching_stream:
                raise LoadingStream
        if check_queue:
            if len(self.music_queue) <= 0:
                raise EmptyQueue
        if check_playing:
            if not self.interaction.guild.voice_client.is_playing():
                raise NotPlaying

        return True

    def pre_check(*d_args, **d_kwargs) -> Callable:
        """
        A decorator for methods requiring pre-checks.

        Args:
            *d_args: Arguments for the pre-check.
            **d_kwargs: Keyword arguments for the pre-check.

        Returns:
            Callable: The decorated function.
        """

        def decorator(function):
            async def wrapper(self, *args, **kwargs):
                if await self._pre_check(*d_args, **d_kwargs):
                    return await function(self, *args, **kwargs)

            return wrapper

        return decorator

    async def cleanup(self):
        """
        Cleans up the music player by clearing the queue and disconnecting from the voice channel.
        """
        self.music_queue = []
        try:
            await self.voice.disconnect()
        except Exception as e:
            LogHandler.warning(
                message=f"Failed to perform cleanup disconnect. {type(e).__name__}: {str(e)}"
            )
            pass
        return

    @pre_check()
    async def _queue_single(self, video_url):
        """
        Queues a single song.

        Args:
            video_url (str): The URL of the video to be queued.

        Returns:
            Song: The queued song.
        """
        timer = time.time()
        video_id = await get_video_id(video_url)
        video = await self.loop.run_in_executor(None, lambda: Video(video_id))
        song = Song(
            video.url,
            video.title,
            video.views,
            video.duration,
            video.thumbnail,
            video.channel,
            video.channel_url,
            video,
        )
        self.music_queue.append(song)
        if not self.paused and len(self.music_queue) > 0 and not self._now_playing:
            await self._play_func(None, self.music_queue[0])

        print(colored(text=f"{video.title} [{video.url}]", color="magenta"))
        print(colored(text=f"Time taken: {time.time() - timer}", color="dark_grey"))
        return song

    @pre_check(check_fetching_stream=True)
    async def queue(self, interaction: Interaction, query: str):
        """
        Queues a song or playlist based on a query.

        Args:
            interaction (Interaction): The interaction object.
            query (str): The query string.

        Returns:
            Playlist or Song: The queued playlist or song.
        """
        is_playlist = False
        self._fetching_stream = True

        try:
            playlist = Playlist(query)
            if playlist and (playlist is not None):
                is_playlist = True
        except Exception:
            pass

        if is_playlist:
            await EventListener.fire("loading_playlist", self, self.interaction, None)
            for _, url in enumerate(playlist.video_urls):
                song = await self._queue_single(url)
                await EventListener.fire(
                    "loading_playlist", self, self.interaction, song
                )
        else:
            yt = YouTube(query)
            if yt.video:
                song = await self._queue_single(yt.video.url)
            else:
                raise NoQueryResult

        self._fetching_stream = False
        return playlist if is_playlist else song

    @pre_check(check_connection=False)
    async def connect(self, interaction: Interaction) -> Optional[bool]:
        """
        Connects to the user's voice channel.

        Args:
            interaction (Interaction): The interaction object.

        Returns:
            Optional[bool]: True if connected successfully, otherwise raises an exception.
        """
        self.interaction = interaction

        if (
            not self.interaction.guild.voice_client
            or not self.interaction.guild.voice_client.is_connected()
        ):
            try:
                await self.interaction.user.voice.channel.connect()
                LogHandler.info(
                    message=f"Connected to voice channel: {self.interaction.user.voice.channel.id}"
                )
                self.voice = interaction.guild.voice_client
                self.loop = interaction.guild.voice_client.loop
                self._members = self.voice.channel.members
                LogHandler.debug(message=f"Defined self.voice and self.loop")
            except Exception as e:
                LogHandler.error(
                    message=f"Failed to connect to voice! {type(e).__name__}: {str(e)}"
                )
                raise FailedConnection

    @pre_check()
    async def change_loop_mode(self, mode: loop_mode) -> loop_mode:
        """
        Changes the loop mode of the player.

        Args:
            mode (loop_mode): The loop mode to set.

        Returns:
            loop_mode: The new loop mode.
        """
        self.loop_mode = (
            loop_mode.off if self.loop_mode == mode and mode != loop_mode.off else mode
        )
        return self.loop_mode

    @pre_check(check_queue=True, check_nowplaying=True)
    async def resume(self, forced=False):
        """
        Resumes playback of the current song.

        Args:
            forced (bool, optional): If True, forces the resume. Defaults to False.

        Returns:
            Song: The currently playing song.
        """
        self.paused = self.voice.is_paused()
        if forced or self.paused:
            self.voice.resume()
            song = self._now_playing
            await song.resume()
            return song
        else:
            raise NotPaused

    @pre_check(check_queue=True, check_nowplaying=True)
    async def pause(self, forced=False):
        """
        Pauses playback of the current song.

        Args:
            forced (bool, optional): If True, forces the pause. Defaults to False.

        Returns:
            Song: The currently paused song.
        """
        self.paused = self.voice.is_paused()
        if forced or not self.paused:
            self.voice.pause()
            song = self._now_playing
            await song.pause()
            return song
        else:
            raise AlreadyPaused

    @pre_check(check_queue=True)
    async def skip(self, index: int = 1):
        """
        Skips the current song.

        Args:
            index (int, optional): The number of songs to skip. Defaults to 1.

        Returns:
            tuple: The last song played and the new song to be played.
        """
        last = self._now_playing
        new = None

        if self.loop_mode in [loop_mode.off, loop_mode.all]:
            await self._pop_queue(index - 1, append=self.loop_mode == loop_mode.all)
            if len(self.music_queue) > 1:
                new = self.music_queue[1]
        elif self.loop_mode == loop_mode.single:
            new = self.music_queue[0]

        if not self.music_queue:
            self._now_playing = None

        self.voice.stop()
        return last, new

    @pre_check(check_queue=True)
    async def previous(self, index: int = 1):
        """
        Skips the current song.

        Args:
            index (int, optional): The number of songs to skip. Defaults to 1.

        Returns:
            tuple: The last song played and the new song to be played.
        """
        first = self.music_queue[: len(self.music_queue) - 2]
        last = self.music_queue[len(self.music_queue) - 2 :]
        last.extend(first)

        self.music_queue = last

        if not len(self.music_queue) > 1:
            self.music_queue.append(self.music_queue[0])

        new = self.music_queue[1]

        self.voice.stop()
        return last, new

    @pre_check(check_queue=True)
    async def shuffle(self):
        """
        Shuffles the songs in the queue.

        Returns:
            list: The shuffled music queue.
        """
        if len(self.music_queue) > 0:
            self.music_queue = [self.music_queue[0]] + random.sample(
                self.music_queue[1:], len(self.music_queue) - 1
            )

        return self.music_queue

    @pre_check(check_nowplaying=True)
    async def now_playing(self):
        """
        Returns the currently playing song.

        Returns:
            Song: The currently playing song.
        """
        return self._now_playing

    @pre_check()
    async def current_queue(self):
        """
        Returns the current queue of songs.

        Returns:
            list: The current music queue.
        """
        return self.music_queue

    @pre_check()
    async def stop(self, disconnect=True):
        """
        Stops playback and optionally disconnects from the voice channel.

        Args:
            disconnect (bool, optional): Whether to disconnect from the voice channel. Defaults to True.

        Returns:
            bool: True if stopped successfully.
        """
        self.music_queue = []

        try:
            self.voice.stop()
        except:
            pass

        if disconnect:
            await self.voice.disconnect()

        return True

    @pre_check(check_queue=True)
    async def remove(self, index=0):
        """
        Removes a song from the queue.

        Args:
            index (int, optional): The index of the song to remove. Defaults to 0.

        Returns:
            Song: The removed song.
        """
        song = None
        if index == 0:
            song = await self.now_playing()
            await self.skip()
        elif index == -1:
            self.voice.stop()
            self.music_queue = []
        else:
            song = self.music_queue.pop(index)

        return song
