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

import os
import time
from datetime import timedelta
from io import BytesIO
from typing import Optional

import nextcord
from nextcord import File, Interaction, SlashOption
from nextcord import SelectOption
from nextcord.ext import commands
from termcolor import colored

from config.loader import SQLITE_PATH, USE_SQLITE, default_language, lang, type_color
from config.perm import auth_guard
from database.guild_handler import get_guild_language, get_guild_settings
from module.embeds.generic import Embeds
from module.embeds.nowplaying import NowPlayingMenu
from module.embeds.queue import QueueViewer
from module.embeds.lyrics import LyricsLangEmbed
from module.matcher import SongMatcher
from module.nextcord_jukebox.enums import LOOPMODE
from module.nextcord_jukebox.event_manager import EventManager
from module.nextcord_jukebox.exceptions import (
    AlreadyPaused,
    EmptyQueue,
    InvalidPlaylist,
    LoadingStream,
    NoQueryResult,
    NotConnected,
    NotPaused,
    NotPlaying,
    NothingPlaying,
    UserNotConnected,
    VoiceChannelMismatch,
)
from module.nextcord_jukebox.player_manager import PlayerManager
from module.nextcord_jukebox.utils import get_playlist_id
from module.progressBar import progressBar
from module.replay_card import create_top_songs_poster

class_namespace = "music_class_title"


class Music(commands.Cog, EventManager):
    def __init__(self, bot):
        self.bot = bot
        self.now_playing_menus = {}
        self.queue_menus = {}
        self.lyrics_menus = {}

        if USE_SQLITE:
            self.manager = PlayerManager(bot, db_type="sqlite", db_path=SQLITE_PATH)
        else:
            self.manager = PlayerManager(
                bot,
                db_type="mysql",
                mysql_host=os.getenv("MYSQL_HOST"),
                mysql_port=int(os.getenv("MYSQL_PORT")),
                mysql_user=os.getenv("MYSQL_USER"),
                mysql_password=os.getenv("MYSQL_PASSWORD"),
                mysql_database=os.getenv("MYSQL_DATABASE"),
            )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.manager.fire_voice_state_update(member, before, after)

    async def ensure_voice_state(self, bot, interaction):
        try:
            player = await self.manager.get_player(interaction, bot)
            return player
        except UserNotConnected:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "not_in_voice"
                    ],
                    message_type="warn",
                ),
            )
        except VoiceChannelMismatch:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "in_different_voice"
                    ],
                    message_type="warn",
                )
            )
        except NotConnected:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "not_in_voice"
                    ],
                    message_type="warn",
                )
            )

    @EventManager.listener
    async def track_start(self, player, interaction: Interaction, before, after):
        if interaction.guild.id in self.now_playing_menus:
            for menu in list(self.now_playing_menus[interaction.guild.id]):
                if menu.is_timeout:
                    self.now_playing_menus[interaction.guild.id].remove(menu)
                else:
                    await menu.update()

        if interaction.guild.id in self.queue_menus:
            for menu in list(self.queue_menus[interaction.guild.id]):
                if menu.is_timeout:
                    self.queue_menus[interaction.guild.id].remove(menu)
                else:
                    await menu.edit_page()

        if (
            await get_guild_settings(interaction.guild.id, "music_silent_mode")
            and before is not None
        ):
            return

        await interaction.channel.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "playing_song"
                ].format(title=after.name),
                message_type="info",
            )
        )

    @EventManager.listener
    async def queue_ended(self, player, interaction):
        await interaction.channel.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "queue_ended"
                ],
                message_type="info",
            )
        )

    @nextcord.slash_command(description=lang[default_language][class_namespace])
    async def music(self, interaction):
        return

    @music.subcommand(description=lang[default_language]["music_play_description"])
    @auth_guard.check_permissions("music/play")
    async def play(
        self,
        interaction: Interaction,
        query: str = SlashOption(
            name="query",
            description=lang[default_language]["music_play_query_description"],
            required=True,
        ),
        shuffle_added: Optional[bool] = SlashOption(
            name="shuffle",
            choices=[True, False],
            required=False,
            description=lang[default_language]["music_play_shuffle_added_description"],
        ),
    ):
        await interaction.response.defer()
        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            guild_loop = (
                await get_guild_settings(
                    interaction.guild.id, "music_default_loop_mode"
                )
                or 1
            )

            loop_method = LOOPMODE(guild_loop)
            if player.loop_mode != loop_method:
                await player.change_loop_mode(loop_method)

                if loop_method != LOOPMODE.off:
                    message_key = (
                        "enabled_loop_single"
                        if loop_method == LOOPMODE.single
                        else (
                            "enabled_loop_queue"
                            if loop_method == LOOPMODE.all
                            else "disabled_loop"
                        )
                    )
                    message = lang[await get_guild_language(interaction.guild.id)][
                        message_key
                    ]
                    if loop_method == LOOPMODE.single:
                        now_playing = await player.now_playing()
                        message = message.format(title=now_playing.name)
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=message,
                            message_type="success",
                        )
                    )

            playlist_id = await get_playlist_id(query)
            if playlist_id and not player.fetching_stream:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "loading_playlist"
                        ],
                        message_type="info",
                    )
                )

            result, failed_songs = await self.bot.loop.create_task(
                player.queue(interaction, query, shuffle_added=shuffle_added)
            )
            if playlist_id and result:
                await interaction.channel.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "queued_playlist"
                        ].format(playlist=result.title),
                        message_type="success",
                    ),
                )
            elif result:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "queued_song"
                        ].format(title=result.name),
                        message_type="success",
                    )
                )

            if failed_songs:
                failed_msg = "\n".join([f"• {song}" for song in failed_songs])
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "failed_to_queue_songs"
                        ].format(songs=failed_msg),
                        message_type="warn",
                    )
                )

        except NoQueryResult as e:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "failed_to_add_song"
                    ].format(title=query),
                    message_type="warn",
                ),
            )
            return
        except LoadingStream:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "command_slowdown"
                    ],
                    message_type="warn",
                ),
            )
            return
        except NotConnected:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "not_in_voice"
                    ],
                    message_type="warn",
                )
            )
            return
        except InvalidPlaylist:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "invalid_playlist"
                    ],
                    message_type="error",
                )
            )
            return

    @music.subcommand(description=lang[default_language]["music_previous_description"])
    @auth_guard.check_permissions("music/previous")
    async def previous(self, interaction: Interaction):
        await interaction.response.defer()
        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return
        try:
            old, new = await player.previous()
            if not new is None:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "skipped_from"
                        ].format(old=old.name, new=new.name),
                        message_type="success",
                    )
                )
            else:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "skipped"
                        ].format(old=old.name),
                        message_type="success",
                    )
                )
        except EmptyQueue:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )
        except LoadingStream:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "command_slowdown"
                    ],
                    message_type="warn",
                ),
            )

    @music.subcommand(description=lang[default_language]["music_skip_description"])
    @auth_guard.check_permissions("music/skip")
    async def skip(
        self,
        interaction: Interaction,
        index: int = nextcord.SlashOption(
            name="index",
            description=lang[default_language]["music_skip_index_description"],
            required=False,
            default=1,
        ),
    ):
        await interaction.response.defer()
        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return
        try:
            old, new = await player.skip(index=index)
            if not new is None:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "skipped_from"
                        ].format(old=old.name, new=new.name),
                        message_type="success",
                    )
                )
            else:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "skipped"
                        ].format(old=old.name),
                        message_type="success",
                    )
                )
        except EmptyQueue:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )
        except LoadingStream:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "command_slowdown"
                    ],
                    message_type="warn",
                ),
            )

    @music.subcommand(description=lang[default_language]["music_move_description"])
    @auth_guard.check_permissions("music/move")
    async def move(
        self,
        interaction: Interaction,
        current_index: int = nextcord.SlashOption(
            name="current_index",
            description=lang[default_language]["music_move_current_index_description"],
            required=True,
        ),
        new_index: int = nextcord.SlashOption(
            name="new_index",
            description=lang[default_language]["music_move_new_index_description"],
            required=True,
        ),
    ):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            queue_length = len(player.music_queue)
            if (
                current_index < 0
                or current_index >= queue_length
                or new_index < 0
                or new_index >= queue_length
            ):
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "invalid_index"
                        ],
                        message_type="warn",
                    )
                )
                return

            song = player.music_queue.pop(current_index)
            player.music_queue.insert(new_index, song)

            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "moved_song"
                    ].format(title=song.name, new_index=new_index),
                    message_type="success",
                )
            )
        except (NotPlaying, EmptyQueue):
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @music.subcommand(description=lang[default_language]["music_queue_description"])
    @auth_guard.check_permissions("music/queue")
    async def queue(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        async def get_page(page: int, query=""):
            # TODO: クエリ内のスコアに基づいて曲を表示する
            music_player = await self.ensure_voice_state(self.bot, interaction)
            if not music_player:
                return

            try:
                now_playing = await music_player.now_playing()
                duration_song_str = str(timedelta(seconds=now_playing.duration))
                time_elapsed = now_playing.timer.elapsed
                duration_passed = round(time_elapsed)
                duration_passed_str = str(timedelta(seconds=duration_passed))
                options = []
                no_result = True

                embed = nextcord.Embed(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        "currently_playing"
                    ].format(title=now_playing.title),
                    description=f"{progressBar.splitBar(now_playing.duration, duration_passed)[0]} | {duration_passed_str}/{duration_song_str}",
                    color=type_color["list"],
                )

                subset = (
                    [
                        song
                        for song, _ in SongMatcher.match(
                            await music_player.current_queue(),
                            query,
                            case_sens=False,
                            threshold=0.8,
                        )
                    ]
                    if query.replace(" ", "") != ""
                    else await music_player.current_queue()
                )

                for i, song in enumerate(
                    subset[(page - 1) * 10 : page * 10], start=(page - 1) * 10
                ):
                    if song == now_playing and i == 0:
                        continue

                    duration_str = str(timedelta(seconds=song.duration))
                    views_str = "{:,}".format(song.views)
                    current_queue = await music_player.current_queue()
                    field_name = (
                        f"{i}. {song.title}"
                        if query.replace(" ", "") == ""
                        else f"{current_queue.index(song)}. {song.title}"
                    )

                    embed.add_field(
                        name=field_name,
                        value=f"⏳ {duration_str} | 👁️ {views_str}",
                        inline=False,
                    )
                    options.append(
                        SelectOption(
                            label=song.title,
                            description=song.channel,
                            value=str(current_queue.index(song)),
                        )
                    )
                    no_result = False

                if no_result:
                    options.append(
                        SelectOption(
                            label=lang[await get_guild_language(interaction.guild.id)][
                                "music_queue_no_result"
                            ],
                            description=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["music_queue_no_result_description"],
                            value="no_result",
                        )
                    )

                total_pages = QueueViewer.compute_total_pages(len(subset), 10)
                footer_text_key = (
                    "queue_footer"
                    if query.replace(" ", "") == ""
                    else "queue_footer_with_query"
                )
                embed.set_footer(
                    text=lang[await get_guild_language(interaction.guild.id)][
                        footer_text_key
                    ].format(page=page, total_pages=total_pages, query=query)
                )

                return embed, total_pages, options
            except NothingPlaying:
                return (
                    Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "nothing_is_playing"
                        ],
                        message_type="warn",
                    ),
                    1,
                    [
                        SelectOption(
                            label=lang[await get_guild_language(interaction.guild.id)][
                                "music_queue_no_result"
                            ],
                            description=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["music_queue_no_result_description"],
                            value="no_result",
                        )
                    ],
                )

        queue_viewer = QueueViewer(interaction, get_page, player)
        await queue_viewer.navigate()
        QueueViewer.compute_total_pages(len(await player.current_queue()), 10)
        self.queue_menus.setdefault(interaction.guild.id, []).append(queue_viewer)

    @music.subcommand(description=lang[default_language]["music_shuffle_description"])
    @auth_guard.check_permissions("music/shuffle")
    async def shuffle(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)
        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            await player.shuffle()
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "shuffled_queue"
                    ],
                    message_type="info",
                )
            )
        except EmptyQueue:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @music.subcommand(description=lang[default_language]["music_loop_description"])
    @auth_guard.check_permissions("music/loop")
    async def loop(
        self,
        interaction: Interaction,
        loop_method: str = SlashOption(
            name="mode",
            choices=["Off", "Single", "All"],
            required=True,
            description=lang[default_language]["music_loop_mode_description"],
        ),
    ):
        await interaction.response.defer(with_message=True)
        loop_method = (
            LOOPMODE.all
            if loop_method == "All"
            else LOOPMODE.single if loop_method == "Single" else LOOPMODE.off
        )
        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return
        try:
            changed_mode = await player.change_loop_mode(loop_method)
            message_key = (
                "enabled_loop_single"
                if changed_mode == LOOPMODE.single
                else (
                    "enabled_loop_queue"
                    if changed_mode == LOOPMODE.all
                    else "disabled_loop"
                )
            )
            message = lang[await get_guild_language(interaction.guild.id)][message_key]
            if changed_mode == LOOPMODE.single:
                now_playing = await player.now_playing()
                message = message.format(title=now_playing.name)
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=message,
                    message_type="success",
                )
            )
        except (EmptyQueue, NothingPlaying):
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @music.subcommand(
        description=lang[default_language]["music_nowplaying_description"]
    )
    @auth_guard.check_permissions("music/nowplaying")
    async def nowplaying(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            song = await player.now_playing()

            menu = NowPlayingMenu(
                interaction=interaction,
                title=f"{song.title}",
                message_type="info",
                thumbnail=song.thumbnail,
                playing=not player.paused,
                player=player,
                song=song,
                bot=self.bot,
            )

            await menu.update()
            self.now_playing_menus.setdefault(interaction.guild.id, []).append(menu)

        except (NothingPlaying, EmptyQueue):
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @music.subcommand(description=lang[default_language]["music_stop_description"])
    @auth_guard.check_permissions("music/stop")
    async def stop(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        await player.stop()
        await self.manager.remove_player(interaction)

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "stopped_player"
                ],
                message_type="success",
            )
        )

    @music.subcommand(description=lang[default_language]["music_pause_description"])
    @auth_guard.check_permissions("music/pause")
    async def pause(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            await player.pause()
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "paused_queue"
                    ],
                    message_type="info",
                )
            )
        except (NotPlaying, EmptyQueue):
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )
        except AlreadyPaused:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "music_already_paused"
                    ],
                    message_type="warn",
                )
            )

    @music.subcommand(description=lang[default_language]["music_resume_description"])
    @auth_guard.check_permissions("music/resume")
    async def resume(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            await player.resume()
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "resumed_queue"
                    ],
                    message_type="info",
                )
            )
        except (NotPlaying, EmptyQueue):
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )
        except NotPaused:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "music_already_playing"
                    ],
                    message_type="warn",
                )
            )

    @music.subcommand(description=lang[default_language]["music_remove_description"])
    @auth_guard.check_permissions("music/remove")
    async def remove(
        self,
        interaction: Interaction,
        index: int = nextcord.SlashOption(
            name="index",
            description=lang[default_language]["music_remove_index_description"],
            required=True,
        ),
    ):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            if len(await player.current_queue()) < index:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "invalid_index"
                        ],
                        message_type="warn",
                    )
                )
                return
            song = await player.remove(index)

            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "removed_song"
                    ].format(
                        title=(
                            song.name
                            if song
                            else lang[await get_guild_language(interaction.guild.id)][
                                "all_songs"
                            ]
                        )
                    ),
                    message_type="success",
                )
            )

        except (NotPlaying, EmptyQueue):
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )
        except NotPaused:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "music_already_playing"
                    ],
                    message_type="warn",
                )
            )

    @music.subcommand(description=lang[default_language]["music_register_description"])
    @auth_guard.check_permissions("music/register")
    async def register(
        self,
        interaction: Interaction,
    ):
        await interaction.response.defer(with_message=True, ephemeral=True)
        secret = await self.manager.database.register(str(interaction.user.id))

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "music_secret"
                ].format(secret=secret),
                message_type="success",
            ),
        )

    @staticmethod
    def generate_canvas(
        interaction: Interaction, period: str, guild_language: str, result_list
    ):
        period_description = {
            "Week": "most_played_week",
            "Month": "most_played_month",
            "Year": "most_played_year",
        }

        canvas = create_top_songs_poster(
            result_list["replays"],
            lang[guild_language]["music_poster_title"],
            lang[guild_language][period_description.get(period, "????")],
            detail_texts=[
                lang[guild_language]["played_duration"].format(
                    hour=str(int(result_list["total_time"] / 3600))
                ),
                lang[guild_language]["total_played"].format(
                    count=str(result_list["total_replayed"])
                ),
                f"{result_list['top_artist']['percentage']}% {result_list['top_artist']['name']}",
            ],
        )

        return canvas

    @music.subcommand(
        description=lang[default_language]["music_most_played_description"]
    )
    @auth_guard.check_permissions("music/most_played")
    async def most_played(
        self,
        interaction: Interaction,
        period: str = SlashOption(
            name="period",
            choices=["Week", "Month", "Year"],
            description=lang[default_language]["music_most_played_period_description"],
            required=False,
            default="Month",
        ),
    ):
        await interaction.response.defer(with_message=True)
        timer = time.time()
        print(colored("Obtaining Entries...", "dark_grey"))
        guild_language = await get_guild_language(interaction.guild.id)
        period_dict = {"Week": 7, "Month": 30, "Year": 365}
        cutoff_days = period_dict.get(period, 30)

        replay_history = await self.manager.database.get_replay_history(
            str(interaction.user.id), cutoff_days
        )

        replay_aggregate = {}
        artist_counts = {}
        total_replays = 0

        for replay in replay_history:
            video_id = replay["song"]
            replay_aggregate[video_id] = replay_aggregate.get(video_id, 0) + 1
            total_replays += 1

        video_metadata = self.manager.database.get_bulk_video_metadata(
            list(replay_aggregate.keys())
        )

        for video_id, replay_count in replay_aggregate.items():
            metadata = video_metadata.get(video_id, {})
            if metadata:
                artist = metadata.get("channel", "Unknown")
                artist_counts[artist] = artist_counts.get(artist, 0) + replay_count

        top_artist = max(artist_counts, key=artist_counts.get, default="Unknown")
        top_artist_percentage = (
            round(artist_counts.get(top_artist, 0) / total_replays * 100)
            if total_replays
            else 0
        )

        result_list = {
            "total_replayed": len(replay_history),
            "total_time": 0,
            "replays": [],
            "top_artist": {"name": top_artist, "percentage": top_artist_percentage},
        }

        top_replays = sorted(
            (
                (video_id, replay_count)
                for video_id, replay_count in replay_aggregate.items()
            ),
            key=lambda item: item[1],
            reverse=True,
        )[:10]

        for video_id, replay_count in top_replays:
            metadata = video_metadata.get(video_id, {})
            result_list["replays"].append(
                {
                    "title": metadata.get("title", ""),
                    "artist": metadata.get("channel", ""),
                    "thumbnails": metadata.get("thumbnails", ""),
                    "replays": replay_count,
                }
            )
            result_list["total_time"] += metadata.get("duration", 0) * replay_count

        result_list["replays"].extend(
            {"title": "", "artist": "", "thumbnail": "", "replays": ""}
            for _ in range(10 - len(result_list["replays"]))
        )

        print(
            colored(
                f"Entries obtained and sorted, Time Taken: {time.time() - timer}",
                "dark_grey",
            )
        )

        timer = time.time()
        print(colored("Generating Canvas...", "dark_grey"))
        canvas = await self.bot.loop.run_in_executor(
            None,
            lambda: self.generate_canvas(
                interaction, period, guild_language, result_list
            ),
        )

        with BytesIO() as image_binary:
            canvas.save(image_binary, "PNG")
            image_binary.seek(0)
            poster = File(filename="most_played.png", fp=image_binary)
            await interaction.followup.send(files=[poster])
            print(
                colored(
                    f"Canvas Generated, Time Taken: {time.time() - timer}", "dark_grey"
                )
            )

    @music.subcommand(
        description=lang[default_language]["music_flush_cache_description"]
    )
    @auth_guard.check_permissions("music/flush_cache")
    async def flush_cache(
        self,
        interaction: Interaction,
    ):
        await interaction.response.defer(with_message=True)
        self.manager.database.clear_old_cache(days=0)
        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "music_cache_flushed"
                ],
                message_type="success",
            )
        )

    @music.subcommand(description=lang[default_language]["music_lyrics_description"])
    @auth_guard.check_permissions("music/lyrics")
    async def lyrics(
        self,
        interaction: Interaction,
    ):
        await interaction.response.defer()

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            song = await player.now_playing()

            embed = LyricsLangEmbed(
                interaction, player=player, song=song, link=song.url, bot=self.bot
            )

            await embed.send_initial_message()
        except (NothingPlaying, EmptyQueue):
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )


async def setup(bot):
    cog = Music(bot)
    bot.add_cog(cog)
    EventManager.attach(cog)
