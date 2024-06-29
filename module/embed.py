from datetime import timedelta
from typing import Callable

import nextcord

from config.config import lang, type_color
from database.guild_handler import get_guild_language
from module.nextcord_jukebox.exceptions import EmptyQueue, NotPlaying
from module.nextcord_jukebox.song import Song
from module.nextcord_jukebox.music_player import MusicPlayer
from module.progressBar import progressBar

class_namespace = "music_class_title"

class Embeds:
    """Class for creating Nextcord embed messages."""

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
        self.follow_up = None
        self.is_timeout = False
        self.source_url = self.song.source_url

        super().__init__(timeout=180)

    async def update(self):
        """
        Update the Now Playing embed and buttons.
        """
        self.song = await self.player.now_playing()
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

        embed.add_field(
            name=f"{progressBar.splitBar(self.song.duration, round(time_elapsed))[0]} | {str(timedelta(seconds=(round(time_elapsed))))}/{str(timedelta(seconds=(self.song.duration)))}",
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
        """
        Update the play/pause button based on the playing state.
        """
        if self.playing:
            self.children[0].emoji = "⏸️"
        else:
            self.children[0].emoji = "▶️"

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.blurple)
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
            print(e)
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
        """
        Skip to the previous song.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
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
            print(e)
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
        """
        Skip to the next song.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
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
            print(e)
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
        """
        Refresh the Now Playing embed.

        Args:
            button (nextcord.Button): The button that was clicked.
            interaction (nextcord.Interaction): The interaction that triggered this action.
        """
        await interaction.response.defer()
        await self.update()

    async def on_timeout(self):
        """
        Handle timeout event by removing buttons from the view.
        """
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, view=None
        )

        self.is_timeout = True
