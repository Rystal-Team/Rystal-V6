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
from datetime import datetime, timedelta
from typing import Callable

import nextcord

from config.loader import lang, type_color
from config.perm import auth_guard
from database.guild_handler import get_guild_language
from module.embeds.generic import Embeds
from module.emoji import get_emoji
from module.nextcord_jukebox.exceptions import EmptyQueue, NotPlaying, NothingPlaying
from module.nextcord_jukebox.music_player import MusicPlayer
from module.nextcord_jukebox.song import Song
from module.progressBar import progressBar
from module.embeds.lyrics import LyricsLangEmbed

class_namespace = "music_class_title"


class NowPlayingMenu(nextcord.ui.View):
    """A Nextcord UI view for the Now Playing menu."""

    def __init__(
        self,
        interaction: nextcord.Interaction,
        title: str,
        message_type: str,
        player: MusicPlayer,
        playing: bool,
        song: Song,
        bot: nextcord.Client,
        thumbnail: str = None,
        on_toggle: Callable = None,
        on_next: Callable = None,
        on_previous: Callable = None,
    ):
        """
        Initialize the Now Playing menu.

        Args:
            interaction (nextcord.Interaction): The interaction that triggered this view.
            title (str): The title of the currently playing song.
            message_type (str): The type of message to determine the embed color.
            player (MusicPlayer): The music player instance.
            playing (bool): Whether a song is currently playing.
            song (Song): The current song being played.
            thumbnail (str, optional): URL of the thumbnail image.
            on_toggle (Callable, optional): Function to call when toggling play/pause.
            on_next (Callable, optional): Function to call when skipping to the next song.
            on_previous (Callable, optional): Function to call when going to the previous song.
        """
        self.interaction = interaction
        self.title = title
        self.message_type = message_type
        self.playing = playing
        self.player = player
        self.on_toggle = on_toggle
        self.on_next = on_next
        self.on_previous = on_previous
        self.thumbnail = thumbnail
        self.song = song
        self.bot = bot
        self.follow_up = None
        self.is_timeout = False
        self.source_url = self.song.source_url
        self.last_interact = datetime.now()
        self.__timeout = 180

        super().__init__()

        self.loop_task = asyncio.create_task(self.auto_update())

    async def auto_update(self):
        """Automatically update the Now Playing embed every 0.5 seconds."""
        await asyncio.sleep(1)
        while not self.is_timeout:
            if (datetime.now() - self.last_interact).total_seconds() > self.__timeout:
                await self.timeout_self()
                break
            await self.update()
            await asyncio.sleep(0.5)

    async def update(self):
        """Update the Now Playing embed and buttons."""
        try:
            self.song = await self.player.now_playing()
        except (NothingPlaying, EmptyQueue):
            embed = Embeds.message(
                title=lang[await get_guild_language(self.interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(self.interaction.guild.id)][
                    "nothing_is_playing"
                ],
                message_type="warn",
            )
            if self.follow_up is not None:
                await self.interaction.followup.edit_message(
                    message_id=self.follow_up.id, embed=embed, view=None
                )
            else:
                await self.interaction.followup.send(embed=embed)
            return

        self.title = self.song.title
        self.thumbnail = self.song.thumbnail

        embed = nextcord.Embed(
            title=self.title,
            color=(type_color[self.message_type]),
            url=self.song.url,
        )

        if self.thumbnail is not None:
            embed.set_thumbnail(url=self.thumbnail)

        time_elapsed = self.song.timer.elapsed

        elapsed_time_str = str(timedelta(seconds=round(time_elapsed)))
        duration_str = str(timedelta(seconds=self.song.duration))
        progress_bar = progressBar.splitBar(self.song.duration, round(time_elapsed))[0]

        embed.add_field(
            name=f"{progress_bar} | {elapsed_time_str}/{duration_str}",
            value=f"👁️ {'{:,}'.format(self.song.views)} | 🧑 {self.song.channel}",
            inline=False,
        )

        embed.set_footer(text=f"🔗 {self.song.url}")

        await self.update_button()

        if self.follow_up is None:
            follow_up_id: nextcord.Message = await self.interaction.followup.send(
                embed=embed, view=self
            )

            self.follow_up = follow_up_id
        else:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, embed=embed, view=self
            )

    async def update_button(self):
        """Update the play/pause button based on the playing state."""
        if self.playing:
            self.children[0].emoji = get_emoji("music_pause")
        else:
            self.children[0].emoji = get_emoji("music_resume")

    @nextcord.ui.button(
        emoji=get_emoji("music_resume"), style=nextcord.ButtonStyle.secondary
    )
    @auth_guard.check_permissions("music/pause")
    @auth_guard.check_permissions("music/resume")
    async def toggle_playing(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        """
        Toggle the playing state between play and pause.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
        self.last_interact = datetime.now()
        try:
            if self.playing:
                await self.player.pause()
            else:
                await self.player.resume()

            self.playing = not self.playing
            await self.update()
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
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )
        except Exception as e:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=lang[await get_guild_language(self.interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(self.interaction.guild.id)][
                        "unknown_error"
                    ],
                    message_type="error",
                ),
            )

            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )

    @nextcord.ui.button(
        emoji=get_emoji("music_previous"), style=nextcord.ButtonStyle.secondary
    )
    @auth_guard.check_permissions("music/skip")
    async def previous(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        """
        Skip to the previous song.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
        self.last_interact = datetime.now()
        try:
            await self.player.previous()
            await self.update()
        except (NotPlaying, EmptyQueue):
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(self.interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                ),
            )
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )
        except Exception as e:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=lang[await get_guild_language(self.interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(self.interaction.guild.id)][
                        "unknown_error"
                    ],
                    message_type="error",
                ),
            )
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )

    @nextcord.ui.button(
        emoji=get_emoji("music_next"), style=nextcord.ButtonStyle.secondary
    )
    @auth_guard.check_permissions("music/skip")
    async def next(self, button: nextcord.Button, interaction: nextcord.Interaction):
        """
        Skip to the next song.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
        self.last_interact = datetime.now()
        try:
            await self.player.skip()
            await self.update()
        except (NotPlaying, EmptyQueue):
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(self.interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                ),
            )
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )
        except Exception as e:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=lang[await get_guild_language(self.interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(self.interaction.guild.id)][
                        "unknown_error"
                    ],
                    message_type="error",
                ),
            )

            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )

    @nextcord.ui.button(
        emoji=get_emoji("music_loop"), style=nextcord.ButtonStyle.secondary
    )
    async def update_embed(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        """
        Refresh the Now Playing embed.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
        self.last_interact = datetime.now()
        await self.update()

    @nextcord.ui.button(emoji=get_emoji("lyrics"), style=nextcord.ButtonStyle.secondary)
    @auth_guard.check_permissions("music/lyrics")
    async def request_lyrics(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        """
        Request the lyrics of the currently playing song.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
        self.last_interact = datetime.now()
        try:

            song = await self.player.now_playing()

            embed = LyricsLangEmbed(
                interaction, player=self.player, song=song, link=song.url, bot=self.bot
            )

            await embed.send_initial_message()
        except (NotPlaying, EmptyQueue):
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(self.interaction.guild.id)][
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                ),
            )
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )
        except Exception as e:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=lang[await get_guild_language(self.interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(self.interaction.guild.id)][
                        "unknown_error"
                    ],
                    message_type="error",
                ),
            )

            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )

    async def timeout_self(self):
        """Timeout the view and stop the auto-update task."""
        self.is_timeout = True
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, view=None
        )
