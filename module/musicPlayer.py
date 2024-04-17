import asyncio
import aiohttp
import yt_dlp
import nextcord
import random
import time
import datetime
from urllib import parse
from youtube_search import YoutubeSearch
from module.timer import CountTimer
from termcolor import colored


def video_id(value):
    query = parse.urlparse(value)

    if query.hostname == "youtu.be":
        return query.path[1:]

    if query.hostname in ("www.youtube.com", "youtube.com"):
        if query.path == "/watch":
            p = parse.parse_qs(query.query)
            return p["v"][0]
        if query.path[:7] == "/embed/":
            return query.path.split("/")[2]
        if query.path[:3] == "/v/":
            return query.path.split("/")[2]

    return None


yt_dlp.utils.bug_reports_message = lambda: ""
ydl = yt_dlp.YoutubeDL(
    {
        "format": "bestaudio/best",
        "restrictfilenames": True,
        "noplaylist": True,
        "ignoreerrors": True,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "source_address": "0.0.0.0",
        "forceip": "4",
    }
)


class EmptyQueue(Exception):
    """Cannot skip because queue is empty"""


class NotConnectedToVoice(Exception):
    """Cannot create the player because bot is not connected to voice"""


class NotPlaying(Exception):
    """Cannot <do something> because nothing is being played"""


async def ytbettersearch(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    index = html.find("watch?v")
    url = ""

    while True:
        char = html[index]
        if char == '"':
            break
        url += char
        index += 1

    url = f"https://www.youtube.com/{url}"
    return url


async def get_video_data(url, query, loop):
    timer = time.time()

    if not query:
        print(colored(text="(FROM URL)", color="dark_grey"))
        data = await loop.run_in_executor(
            None, lambda: ydl.extract_info(url, download=False)
        )
        url = "https://www.youtube.com/watch?v=" + data["id"]
        title = data["title"]
        description = data["description"]
        views = data["view_count"]
        duration = data["duration"]
        thumbnail = data["thumbnail"]
        channel = data["uploader"]
        channel_url = data["uploader_url"]
    else:
        print(colored(text="(FROM QUERY)", color="dark_grey"))
        result = video_id(url)
        if result is None:
            ytresult = YoutubeSearch(url, max_results=1).to_dict()
            result = ytresult[0]["id"]

        url = f"https://www.youtube.com/watch?v={result}"
        data = await loop.run_in_executor(
            None, lambda: ydl.extract_info(url, download=False)
        )
        url = "https://www.youtube.com/watch?v=" + data["id"]
        title = data["title"]
        description = data["description"]
        views = data["view_count"]
        duration = data["duration"]
        thumbnail = data["thumbnail"]
        channel = data["uploader"]
        channel_url = data["uploader_url"]

    print(colored(text=f"{title} [{url}]", color="magenta"))
    print(colored(text=f"Time taken: {time.time() - timer}", color="dark_grey"))

    return Song(
        url,
        title,
        description,
        views,
        duration,
        thumbnail,
        channel,
        channel_url,
    )


async def check_queue(player, interaction, opts, music, after, on_play, loop, bot):
    try:
        song = music.queue[interaction.guild.id][0]
    except IndexError:
        return

    if player.music_loop is None:
        try:
            music.queue[interaction.guild.id].pop(0)
        except IndexError:
            return

        if (
            (len(music.queue[interaction.guild.id]) == 0)
            or (not player.voice)
            or (not player.voice.is_connected())
        ):
            player.current_playing = None

            asyncio.run(
                bot.dispatch(
                    "queue_ended",
                    interaction,
                )
            )

            return
        elif len(music.queue[interaction.guild.id]) > 0:
            data = await loop.run_in_executor(
                None,
                lambda: ydl.extract_info(
                    music.queue[interaction.guild.id][0].url, download=False
                ),
            )
            source_url = data["url"]

            print(
                colored(
                    text=f"[PLAYING] {music.queue[interaction.guild.id][0].title}",
                    color="light_blue",
                )
            )
            expire_unix_time = parse.parse_qs(parse.urlparse(source_url).query)[
                "expire"
            ][0]
            print(
                colored(
                    text=f"Queue Source (Expire: {datetime.datetime.fromtimestamp(int(expire_unix_time))}):\n{source_url}",
                    color="dark_grey",
                )
            )

            source = nextcord.PCMVolumeTransformer(
                nextcord.FFmpegPCMAudio(source_url, **opts)
            )

            interaction.guild.voice_client.play(
                source,
                after=lambda error: after(
                    player, interaction, opts, music, after, on_play, loop, bot
                ),
            )

            song = music.queue[interaction.guild.id][0]
            player.current_playing = song
            song.elapsed = 0

            song.timer = CountTimer()
            song.timer.start()

            asyncio.run(
                bot.dispatch(
                    "queue_track_start",
                    interaction,
                    song,
                    player,
                )
            )

            if on_play:
                loop.create_task(on_play(interaction, song))
    elif player.music_loop == "single":
        data = await loop.run_in_executor(
            None,
            lambda: ydl.extract_info(
                music.queue[interaction.guild.id][0].url, download=False
            ),
        )
        source_url = data["url"]

        print(
            colored(
                text=f"[PLAYING] {music.queue[interaction.guild.id][0].title}",
                color="light_blue",
            )
        )
        expire_unix_time = parse.parse_qs(parse.urlparse(source_url).query)["expire"][0]
        print(
            colored(
                text=f"Queue Source (Expire: {datetime.datetime.fromtimestamp(int(expire_unix_time))}):\n{source_url}",
                color="dark_grey",
            )
        )

        source = nextcord.PCMVolumeTransformer(
            nextcord.FFmpegPCMAudio(source_url, **opts)
        )

        interaction.guild.voice_client.play(
            source,
            after=lambda error: after(
                player, interaction, opts, music, after, on_play, loop, bot
            ),
        )

        song = music.queue[interaction.guild.id][0]
        player.current_playing = song
        song.elapsed = 0

        song.timer = CountTimer()
        song.timer.start()

        asyncio.run(
            bot.dispatch(
                "queue_track_start",
                interaction,
                song,
                player,
            )
        )

        if on_play:
            loop.create_task(on_play(interaction, song))
    elif player.music_loop == "queue":
        empty_queue = False
        try:
            popped_song = music.queue[interaction.guild.id][0]
            music.queue[interaction.guild.id].pop(0)
        except IndexError:
            return

        if len(music.queue[interaction.guild.id]) == 0:
            empty_queue == True
            music.queue[interaction.guild.id].append(popped_song)

        if len(music.queue[interaction.guild.id]) > 0:
            data = await loop.run_in_executor(
                None,
                lambda: ydl.extract_info(
                    music.queue[interaction.guild.id][0].url, download=False
                ),
            )
            source_url = data["url"]

            print(
                colored(
                    text=f"[PLAYING] {music.queue[interaction.guild.id][0].title}",
                    color="light_blue",
                )
            )
            expire_unix_time = parse.parse_qs(parse.urlparse(source_url).query)[
                "expire"
            ][0]
            print(
                colored(
                    text=f"Queue Source (Expire: {datetime.datetime.fromtimestamp(int(expire_unix_time))}):\n{source_url}",
                    color="dark_grey",
                )
            )

            source = nextcord.PCMVolumeTransformer(
                nextcord.FFmpegPCMAudio(source_url, **opts)
            )

            interaction.guild.voice_client.play(
                source,
                after=lambda error: after(
                    player, interaction, opts, music, after, on_play, loop, bot
                ),
            )

            song = music.queue[interaction.guild.id][0]
            song.elapsed = 0

            song.timer = CountTimer()
            song.timer.start()

            if not empty_queue:
                music.queue[interaction.guild.id].append(popped_song)

            player.current_playing = song

            asyncio.run(
                bot.dispatch(
                    "queue_track_start",
                    interaction,
                    song,
                    player,
                )
            )

            if on_play:
                loop.create_task(on_play(interaction, song))


class Music(object):
    def __init__(self):
        self.queue = {}
        self.players = []

    def create_player(self, interaction, **kwargs):
        if not interaction.guild.voice_client:
            raise NotConnectedToVoice(
                "Cannot create the player because bot is not connected to voice"
            )

        player = MusicPlayer(interaction, self, **kwargs)
        self.players.append(player)
        print(
            colored(
                text=f"Created Player (Guild: {interaction.guild.name} [{interaction.guild.id}])",
                color="dark_grey",
            )
        )
        return player

    def get_player(self, **kwargs):
        guild = kwargs.get("guild_id")
        channel = kwargs.get("channel_id")
        for player in self.players:
            if (
                guild
                and channel
                and player.interaction.guild.id == guild
                and player.voice.channel.id == channel
            ):
                if player.voice and player.voice.is_connected():
                    return player
                else:
                    player.delete()
                    return None
            elif not guild and channel and player.voice.channel.id == channel:
                if player.voice and player.voice.is_connected():
                    return player
                else:
                    player.delete()
                    return None
            elif not channel and guild and player.interaction.guild.id == guild:
                if player.voice and player.voice.is_connected():
                    return player
                else:
                    player.delete()
                    return None
        else:
            return None


class MusicPlayer(object):
    def __init__(self, interaction, music, **kwargs):
        self.bot = kwargs.get("bot")
        self.interaction = interaction
        self.voice = interaction.guild.voice_client
        self.loop = interaction.guild.voice_client.loop
        self.music_loop = None
        self.music = music
        self.silent_mode = False
        self.paused = False
        self.current_playing = None
        self.leave_when_empty = False
        if self.interaction.guild.id not in self.music.queue.keys():
            self.music.queue[self.interaction.guild.id] = []

        self.after_func = check_queue
        self.on_play_func = self.on_queue_func = self.on_skip_func = (
            self.on_previous_func
        ) = self.on_stop_func = self.on_pause_func = self.on_resume_func = (
            self.on_queue_loop_toggle_func
        ) = self.on_loop_toggle_func = self.on_volume_change_func = (
            self.on_remove_from_queue_func
        ) = None
        ffmpeg_error = kwargs.get(
            "ffmpeg_error_betterfix", kwargs.get("ffmpeg_error_fix")
        )
        if ffmpeg_error and "ffmpeg_error_betterfix" in kwargs.keys():
            self.ffmpeg_opts = {
                "options": "-vn -loglevel quiet -hide_banner -nostats",
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin",
            }
        elif ffmpeg_error:
            self.ffmpeg_opts = {
                "options": "-vn",
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin",
            }
        else:
            self.ffmpeg_opts = {"options": "-vn", "before_options": "-nostdin"}

    def delete(self):
        print(
            colored(
                text=f"Deleted Player (Guild: {self.interaction.guild.name} [{self.interaction.guild.id}])",
                color="dark_grey",
            )
        )
        del self.music.queue[self.interaction.guild.id]
        self.music.players.remove(self)
        del self

    def on_queue(self, func):
        self.on_queue_func = func

    def on_play(self, func):
        self.on_play_func = func

    def on_skip(self, func):
        self.on_skip_func = func

    def on_previous(self, func):
        self.on_previous_func = func

    def on_stop(self, func):
        self.on_stop_func = func

    def on_pause(self, func):
        self.on_pause_func = func

    def on_resume(self, func):
        self.on_resume_func = func

    def on_loop_toggle(self, func):
        self.on_loop_toggle_func = func

    def on_loop_toggle(self, func):
        self.on_queue_loop_toggle_func = func

    def on_volume_change(self, func):
        self.on_volume_change_func = func

    def on_remove_from_queue(self, func):
        self.on_remove_from_queue_func = func

    async def queue(self, url, query=True):
        try:
            song = await get_video_data(url, query, self.loop)
            self.music.queue[self.interaction.guild.id].append(song)

            if self.on_queue_func:
                await self.on_queue_func(self.interaction, song)

            return True, song
        except Exception as e:
            return False, e

    async def play(self, url, search=False, query=True):
        try:
            data = await self.loop.run_in_executor(
                None,
                lambda: ydl.extract_info(
                    self.music.queue[self.interaction.guild.id][0].url, download=False
                ),
            )
            source_url = data["url"]

            source = nextcord.PCMVolumeTransformer(
                nextcord.FFmpegPCMAudio(
                    source_url,
                    **self.ffmpeg_opts,
                )
            )

            print(
                colored(
                    text=f"[PLAYING] {self.music.queue[self.interaction.guild.id][0].title}",
                    color="light_blue",
                )
            )
            expire_unix_time = parse.parse_qs(parse.urlparse(source_url).query)[
                "expire"
            ][0]
            print(
                colored(
                    text=f"Queue Source (Expire: {datetime.datetime.fromtimestamp(int(expire_unix_time))}):\n{source_url}",
                    color="dark_grey",
                )
            )

            self.voice.play(
                source,
                after=lambda error: self.after_func(
                    self,
                    self.interaction,
                    self.ffmpeg_opts,
                    self.music,
                    self.after_func,
                    self.on_play_func,
                    self.loop,
                    self.bot,
                ),
            )

            song = self.music.queue[self.interaction.guild.id][0]
            self.current_playing = song
            song.elapsed = 0

            song.timer = CountTimer()
            song.timer.start()

            if self.on_play_func:
                await self.on_play_func(self.interaction, song)

            return True, song
        except Exception as e:
            print(e)
            song = await self.queue(url, search, query)

            return False, song

    async def skip(self, force=True):
        if len(self.music.queue[self.interaction.guild.id]) == 0:
            raise NotPlaying("Cannot skip because nothing is being played")
        elif not len(self.music.queue[self.interaction.guild.id]) > 1 and not force:
            raise EmptyQueue("Cannot skip because queue is empty")
        else:
            old = self.current_playing
            self.voice.stop()

            try:
                new = self.music.queue[self.interaction.guild.id][1]

                if self.on_skip_func:
                    await self.on_skip_func(self.interaction, old, new)

                return old, new
            except IndexError:
                if self.on_skip_func:
                    await self.on_skip_func(self.interaction, old)

                return old, None

    async def jump(self, index: int):
        if len(self.music.queue[self.interaction.guild.id]) == 0:
            raise NotPlaying("Cannot skip because nothing is being played")
        else:
            old = self.current_playing
            self.voice.stop()

            try:
                for _ in range(index - 1):
                    last = self.music.queue[self.interaction.guild.id].pop(0)
                    self.music.queue[self.interaction.guild.id].append(last)

                new = self.music.queue[self.interaction.guild.id][1]

                if self.on_skip_func:
                    await self.on_skip_func(self.interaction, old, new)

                return old, new
            except IndexError:
                if self.on_skip_func:
                    await self.on_skip_func(self.interaction, old)

                return old, None

    async def previous(self):
        if len(self.music.queue[self.interaction.guild.id]) == 0:
            raise NotPlaying("Cannot replay because nothing is being played")
        else:
            old = self.current_playing
            self.voice.stop()

            try:
                # shift two places backwards
                # e.g. from [1, 4, 5, 6, 7, 8, 9, 12] to [9, 12, 1, 4, 5, 6, 7, 8]

                first = self.music.queue[self.interaction.guild.id][
                    : len(self.music.queue[self.interaction.guild.id]) - 2
                ]
                last = self.music.queue[self.interaction.guild.id][
                    len(self.music.queue[self.interaction.guild.id]) - 2 :
                ]
                last.extend(first)

                self.music.queue[self.interaction.guild.id] = last

                if not len(self.music.queue[self.interaction.guild.id]) > 1:
                    self.music.queue[self.interaction.guild.id].append(
                        self.music.queue[self.interaction.guild.id][0]
                    )

                new = self.music.queue[self.interaction.guild.id][1]

                if self.on_previous_func:
                    await self.on_previous_func(self.interaction, old, new)

                return new, old
            except IndexError:
                if self.on_previous_func:
                    await self.on_previous_func(self.interaction, old)

                return old, None

    async def stop(self):
        try:

            self.delete()
            self.voice.stop()
            await self.voice.disconnect()
        except:
            raise NotPlaying("Cannot loop because nothing is being played")

        if self.on_stop_func:
            await self.on_stop_func(self.interaction)

    async def pause(self):
        try:
            self.paused = True
            self.voice.pause()
            song = self.current_playing
            self.current_playing.timer.pause()
        except:
            raise NotPlaying("Cannot pause because nothing is being played")

        if self.on_pause_func:
            await self.on_pause_func(self.interaction, song)

        return song

    async def resume(self):
        try:
            self.paused = False
            self.voice.resume()
            song = self.current_playing
            self.current_playing.timer.resume()
        except:
            raise NotPlaying("Cannot resume because nothing is being played")

        if self.on_resume_func:
            await self.on_resume_func(self.interaction, song)

        return song

    def current_queue(self):
        try:
            return self.music.queue[self.interaction.guild.id]
        except KeyError:
            raise EmptyQueue("Queue is empty")

    def now_playing(self):
        try:
            return self.current_playing
        except:
            return None

    async def toggle_song_loop(self):
        try:
            song = self.current_playing
        except:
            raise NotPlaying("Cannot loop because nothing is being played")

        if not self.music_loop == "single":
            self.music_loop = "single"
        else:
            self.music_loop = None

        if self.on_loop_toggle_func:
            await self.on_loop_toggle_func(self.interaction, song)

        return song

    async def toggle_queue_loop(self):
        try:
            song = self.current_playing
        except:
            raise NotPlaying("Cannot loop because nothing is being played")

        if not self.music_loop == "queue":
            self.music_loop = "queue"
        else:
            self.music_loop = None

        if self.on_queue_loop_toggle_func:
            await self.on_queue_loop_toggle_func(self.interaction)

        return song

    async def disable_loop(self):
        try:
            song = self.current_playing
        except:
            raise NotPlaying("Cannot loop because nothing is being played")

        self.music_loop = None

        return song

    async def change_volume(self, vol):
        self.voice.source.volume = vol
        try:
            song = self.current_playing
        except:
            raise NotPlaying("Cannot loop because nothing is being played")

        if self.on_volume_change_func:
            await self.on_volume_change_func(self.interaction, song, vol)

        return (song, vol)

    async def shuffle(self):
        try:
            song = self.current_playing
        except:
            raise NotPlaying("Cannot loop because nothing is being played")

        if len(self.music.queue[self.interaction.guild.id]) > 0:
            self.current_playing
            rest = self.music.queue[self.interaction.guild.id][1:]
            random.shuffle(rest)
            self.music.queue[self.interaction.guild.id] = [
                self.music.queue[self.interaction.guild.id][0]
            ] + rest

        return song

    async def remove_from_queue(self, index):
        if index == 0:
            try:
                song = self.current_playing
            except:
                raise NotPlaying("Cannot loop because nothing is being played")

            await self.skip(force=True)
            return song

        song = self.music.queue[self.interaction.guild.id][index]
        self.music.queue[self.interaction.guild.id].pop(index)

        if self.on_remove_from_queue_func:
            await self.on_remove_from_queue_func(self.interaction, song)

    async def toggle_silent_mode(self):
        self.silent_mode = not self.silent_mode

        return self.silent_mode

    def delete(self):
        self.music.players.remove(self)


class Song(object):
    def __init__(
        self,
        url,
        title,
        description,
        views,
        duration,
        thumbnail,
        channel,
        channel_url,
    ):
        self.url = url
        self.title = title
        self.description = description
        self.views = views
        self.name = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.channel = channel
        self.channel_url = channel_url
        self.timer = None
