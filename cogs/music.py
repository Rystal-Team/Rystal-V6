

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

from datetime import timedelta

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from config.config import lang, type_color
from database.guild_handler import get_guild_language, get_guild_settings
from module.embed import Embeds, NowPlayingMenu
from module.matcher import SongMatcher
from module.nextcord_jukebox.enums import LOOPMODE
from module.nextcord_jukebox.event_manager import EventManager
from module.nextcord_jukebox.exceptions import *
from module.nextcord_jukebox.player_manager import PlayerManager
from module.nextcord_jukebox.utils import get_playlist_id
from module.pagination import Pagination
from module.progressBar import progressBar

class_namespace = "music_class_title"


class Music(commands.Cog, EventManager):
    def __init__(self, bot):
        self.bot = bot
        self.now_playing_menus = []
        self.manager = PlayerManager(bot)

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
                )
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
        for menu in self.now_playing_menus:
            if menu.is_timeout:
                self.now_playing_menus.remove(menu)
            else:
                await menu.update()

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

    @nextcord.slash_command(description="🎵 | Music")
    async def music(self, interaction):
        return

    @music.subcommand(description="🎵🎵 | Play a song!")
    async def play(
        self,
        interaction: Interaction,
        query: str = SlashOption(name="query", description="Enter the song name!"),
    ):
        await interaction.response.defer()
        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        try:
            playlist_id = await get_playlist_id(query)
            if playlist_id and not player._fetching_stream:
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

            feed = await player.queue(interaction, query)
            if playlist_id:
                await interaction.channel.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "queued_playlist"
                        ].format(playlist=feed.title),
                        message_type="success",
                    ),
                )
            else:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "queued_song"
                        ].format(title=feed.name),
                        message_type="success",
                    )
                )
        except NoQueryResult:
            pass
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

    @music.subcommand(description="🎵 | Skip the music!")
    async def skip(
        self,
        interaction: Interaction,
        index: int = nextcord.SlashOption(
            name="index",
            description="The position of the song in the queue!",
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
            if not (new is None):
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

    @music.subcommand(description="🎵 | Get the current music queue.")
    async def queue(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = await self.ensure_voice_state(self.bot, interaction)
        if not player:
            return

        async def get_page(page: int, query=""):
            # TODO: クエリ内のスコアに基づいて曲を表示する
            music_player = await self.ensure_voice_state(self.bot, interaction)

            try:
                now_playing = await music_player.now_playing()
                duration_song_str = str(timedelta(seconds=now_playing.duration))
                time_elapsed = now_playing.timer.elapsed
                duration_passed = round(time_elapsed)
                duration_passed_str = str(timedelta(seconds=duration_passed))

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
                    subset[(page - 1) * 10: page * 10], start=(page - 1) * 10
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

                total_pages = Pagination.compute_total_pages(len(subset), 10)
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

                return embed, total_pages
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
                )

        await Pagination(interaction, get_page).navegate()
        Pagination.compute_total_pages(len(await player.current_queue()), 10)

    @music.subcommand(description="🎵 |Shuffles the queue.")
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

    @music.subcommand(description="🎵 | Loop the current queue.")
    async def loop(
        self,
        interaction: Interaction,
        loop_method: str = SlashOption(
            name="mode", choices=["Off", "Single", "All"], required=True
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

    @music.subcommand(description="🎵 | Now playing...")
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
            )

            await menu.update()
            self.now_playing_menus.append(menu)

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

    @music.subcommand(description="🎵 | Stop the music!")
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

    @music.subcommand(description="🎵 | Pause the music!")
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

    @music.subcommand(description="🎵 | Resume the music!")
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

    @music.subcommand(description="🎵 | Remove from queue!")
    async def remove(
        self,
        interaction: Interaction,
        index: int = nextcord.SlashOption(
            name="index",
            description="The position of the song in the queue! -1 for All.",
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
                            else lang[
                                await get_guild_language(interaction.guild.id)
                            ]["all_songs"]
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

    @music.subcommand(
        description="🎵 | Register/Regenerate a secret to use our RPC client!"
    )
    async def register(
        self,
        interaction: Interaction,
    ):
        await interaction.response.defer(with_message=True)
        secret = await self.manager.database.register(str(interaction.user.id))

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "music_registered_secret"
                ],
                message_type="success",
            )
        )

        await interaction.user.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "music_secret"
                ].format(secret=secret),
                message_type="success",
            )
        )


async def setup(bot):
    cog = Music(bot)
    bot.add_cog(cog)
    EventManager.attach(cog)
