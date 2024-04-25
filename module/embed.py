from datetime import timedelta
from typing import Callable

import nextcord

from config.config import lang, type_color
from database.guild_handler import get_guild_language
from module.musicPlayer import EmptyQueue, MusicPlayer, NotPlaying, Song
from module.progressBar import progressBar

"""from module.lyrics import Searcher
"""
class_namespace = "music_class_title"


class Embeds:
    def message(title, message, message_type, thumbnail=None):
        embed = nextcord.Embed(
            title=title, description=message, color=(type_color[message_type])
        )

        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)

        return embed


class NowPlayingMenu(nextcord.ui.View):
    def __init__(
        self,
        interaction: nextcord.Interaction,
        title: str,
        message_type: str,
        player: MusicPlayer,
        playing: bool,
        song: Song,
        thumbnail: str = None,
        on_toggle: Callable = None,
        on_next: Callable = None,
        on_previous: Callable = None,
    ):
        """
        Args:
            interaction (nextcord.Interaction): interaction
            title (str): embed title
            description (str): embed description
            message_type (str): color type
            playing (bool): song paused or not
            on_toggle (Callable): on pause/resume button pressed
            on_next (Callable): on next song button
            on_previous (Callable): on previous song button
            thumbnail (str, optional): thumbnail url. Defaults to None.
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
        self.follow_up = None
        self.is_timeout = False

        super().__init__(timeout=180)

    async def update(self):
        self.song = self.player.now_playing()
        self.title = self.song.title
        self.thumbnail = self.song.thumbnail

        embed = nextcord.Embed(
            title=self.title,
            color=(type_color[self.message_type]),
            url=self.song.url,
        )

        if self.thumbnail is not None:
            embed.set_thumbnail(url=self.thumbnail)

        embed.add_field(
            name=f"{progressBar.splitBar(self.song.duration, round(self.song.timer.elapsed))[0]} | {str(timedelta(seconds=(round(self.song.timer.elapsed))))}/{str(timedelta(seconds=(self.song.duration)))}",
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
        if self.playing:
            self.children[0].emoji = "⏸️"
        else:
            self.children[0].emoji = "▶️"

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.blurple)
    async def toggle_playing(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer()
        try:
            if self.playing:
                await self.player.pause()
            else:
                await self.player.resume()

            self.playing = not self.playing
            await self.update()
        except NotPlaying or EmptyQueue:
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

    @nextcord.ui.button(emoji="⏪", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer()
        try:
            await self.player.previous()
            await self.update()
        except NotPlaying or EmptyQueue:
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

    @nextcord.ui.button(emoji="⏩", style=nextcord.ButtonStyle.blurple)
    async def next(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        try:
            await self.player.skip()
            await self.update()
        except NotPlaying or EmptyQueue:
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

    @nextcord.ui.button(emoji="🔃", style=nextcord.ButtonStyle.blurple)
    async def update_embed(
        self, button: nextcord.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer()
        await self.update()

    async def on_timeout(self):
        # remove buttons on timeout
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, view=None
        )

        self.is_timeout = True
