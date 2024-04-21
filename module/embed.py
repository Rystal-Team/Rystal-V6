import nextcord, asyncio
from config.config import type_color
from typing import Callable, Optional
from module.musicPlayer import Song, MusicPlayer, NotPlaying, EmptyQueue
from datetime import timedelta
from module.progressBar import progressBar
from config.config import music_class_title
from config.config import lang

"""from module.lyrics import Searcher
"""


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
        self, interaction: nextcord.Interaction, button: nextcord.Button
    ):
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
                    title=lang["system_class_title"],
                    message=lang["unknown_error"],
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
                    title=lang["system_class_title"],
                    message=lang["unknown_error"],
                    message_type="error",
                ),
            )

            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )

    @nextcord.ui.button(emoji="⏪", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, interaction: nextcord.Interaction, button: nextcord.Button
    ):
        try:
            await self.player.previous()
            await self.update()
        except NotPlaying or EmptyQueue:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=music_class_title,
                    message=lang["nothing_is_playing"],
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
                    title=lang["system_class_title"],
                    message=lang["unknown_error"],
                    message_type="error",
                ),
            )
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )

    @nextcord.ui.button(emoji="⏩", style=nextcord.ButtonStyle.blurple)
    async def next(self, interaction: nextcord.Interaction, button: nextcord.Button):
        try:
            await self.player.skip()
            await self.update()
        except NotPlaying or EmptyQueue:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=Embeds.message(
                    title=music_class_title,
                    message=lang["nothing_is_playing"],
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
                    title=lang["system_class_title"],
                    message=lang["unknown_error"],
                    message_type="error",
                ),
            )

            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id, view=None
            )

    @nextcord.ui.button(emoji="🔃", style=nextcord.ButtonStyle.blurple)
    async def update_embed(
        self, interaction: nextcord.Interaction, button: nextcord.Button
    ):
        await self.update()

    """@nextcord.ui.button(emoji="📜", style=nextcord.ButtonStyle.blurple)
    async def update_embed(
        self, interaction: nextcord.Interaction, button: nextcord.Button
    ):
        await self.update()"""

    async def on_timeout(self):
        # remove buttons on timeout
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, view=None
        )

        self.is_timeout = True


"""
class UpdateDropdownLyricsView(nextcord.ui.View):
    def __init__(
        self, interaction: nextcord.Interaction, get_page: Callable, song: str
    ):
        self.interaction = interaction
        self.results = None
        self.follow_up = None
        self.get_page = get_page
        self.query = song
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=180)

    def get_options(self):
        options = []

        for song in self.results:
            options.append(nextcord.SelectOption(label=f"{song.title[:24]}"))

        return options

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = nextcord.Embed(
                description=lang["author_only_interactions"],
                color=16711680,
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False

    async def navegate(self):
        self.results = await Searcher.search_song(self.query)
        print(len(self.results))
        emb, self.total_pages = await self.get_page(self.index)

        if self.total_pages == 1:
            follow_up_msg: nextcord.Message = await self.interaction.followup.send(
                embed=emb
            )

            self.follow_up = follow_up_msg
        elif self.total_pages > 1:
            self.update_buttons()
            follow_up_msg: nextcord.Message = await self.interaction.followup.send(
                embed=emb, view=self
            )

            self.follow_up = follow_up_msg

    async def edit_page(self, interaction: nextcord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()

        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, embed=emb, view=self
        )

    def update_buttons(self):
        options = self.get_options()
        self.children[0].options = options
        self.children[1].disabled = self.index == 1
        self.children[2].disabled = self.index == self.total_pages

    @nextcord.ui.select(
        placeholder="Waiting for selection...",
        min_values=1,
        max_values=1,
        options=[nextcord.SelectOption(label="dwadaw")],
    )
    async def select_callback(
        self, interaction: nextcord.Interaction, select: nextcord.ui.Select
    ):
        options = self.get_options()
        print(options)
        super().__init__(options=options)
        print(select)

    @nextcord.ui.button(emoji="◀️", style=nextcord.ButtonStyle.blurple)
    async def previous(
        self, interaction: nextcord.Interaction, button: nextcord.Button
    ):
        self.index -= 1
        await self.edit_page(interaction)

    @nextcord.ui.button(emoji="▶️", style=nextcord.ButtonStyle.blurple)
    async def next(self, interaction: nextcord.Interaction, button: nextcord.Button):
        self.index += 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        await self.interaction.followup.edit_message(
            message_id=self.follow_up.id, view=None
        )

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1
"""
