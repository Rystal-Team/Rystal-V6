from datetime import timedelta

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from pytube import Playlist

from termcolor import colored
from config.config import lang
from config.config import type_color
from database.guild_handler import get_guild_language, get_guild_settings
from module.embed import Embeds, NowPlayingMenu
from module.musicPlayer import Music as MusicModule
from module.pagination import Pagination
from module.progressBar import progressBar

"""from module.lyrics_handler import Handler
"""

music = MusicModule()
class_namespace = "music_class_title"


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.now_playing_menus = []

    @commands.Cog.listener()
    async def on_queue_ended(self, interaction):
        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            await interaction.followup.send(
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
        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "player_disconnected"
                    ],
                    message_type="info",
                )
            )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client
        if voice_state is None:
            return

        if len(voice_state.channel.members) == 1:
            player = music.get_player(guild_id=member.guild.id)
            if player is not None:
                if await get_guild_settings(member.guild.id, "music_auto_leave"):
                    await player.interaction.channel.send(
                        embed=Embeds.message(
                            title=lang[
                                await get_guild_language(player.interaction.guild.id)
                            ][class_namespace],
                            message=lang[
                                await get_guild_language(player.interaction.guild.id)
                            ]["stopped_player"],
                            message_type="success",
                        )
                    )

                    await player.stop()
                    music.remove_player(member.guild.id)

                    print(colored(text="[PLAYER] LEFT WHEN EMPTY", color="dark_grey"))
                else:
                    return

    @commands.Cog.listener()
    async def on_queue_track_start(self, interaction, song, player):
        for menu in self.now_playing_menus:
            if menu.is_timeout == True:
                self.now_playing_menus.remove(menu)
            else:
                await menu.update()

        if not (await get_guild_settings(interaction.guild.id, "music_silent_mode")):
            await interaction.channel.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "playing_song"
                    ].format(title=song.name),
                    message_type="info",
                )
            )

    @nextcord.slash_command(description="🎵 | Play a song!")
    async def play(
        self,
        interaction: Interaction,
        query: str = SlashOption(name="query", description="Enter the song name!"),
    ):
        await interaction.response.defer(with_message=True)

        is_playlist = False

        try:
            playlist = Playlist(query)

            if playlist and (playlist is not None):
                is_playlist = True
        except:
            pass

        if not interaction.guild.voice_client:
            if interaction.user.voice is None:
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
            else:
                await interaction.user.voice.channel.connect()

        player = music.get_player(guild_id=interaction.guild.id)
        if not player:
            player = music.create_player(
                interaction, ffmpeg_error_betterfix=True, bot=self.bot
            )

        # async def handler():
        if is_playlist:
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

            for i, url in enumerate(playlist.video_urls):
                que_suc, feed = await player.queue(url, query=False)

                if not que_suc:
                    await interaction.channel.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["failed_to_add_song"].format(title=url),
                            message_type="error",
                        )
                    )

                    break

                if (
                    not interaction.guild.voice_client.is_playing()
                    and not player.paused
                ):
                    try:
                        suc, song = await player.play(query, query=True)

                        await interaction.channel.send(
                            embed=Embeds.message(
                                title=lang[
                                    await get_guild_language(interaction.guild.id)
                                ][class_namespace],
                                message=lang[
                                    await get_guild_language(interaction.guild.id)
                                ]["playing_song"].format(title=song.name),
                                message_type="info",
                            )
                        )
                    except Exception:
                        pass

            await interaction.channel.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "queued_playlist"
                    ].format(playlist=playlist.title),
                    message_type="success",
                ),
            )
        else:
            que_suc, feed = await player.queue(query, query=True)

            if not que_suc:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "failed_to_add_song"
                        ].format(title=query),
                        message_type="error",
                    )
                )

            if not interaction.guild.voice_client.is_playing():
                suc, song = await player.play(query, query=True)

                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "playing_song"
                        ].format(title=song.name),
                        message_type="info",
                    )
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

    @nextcord.slash_command(description="🎵 | Loop the current queue.")
    async def loop(
        self,
        interaction: Interaction,
        loop_mode: str = SlashOption(
            name="mode", choices=["Off", "Single", "All"], required=True
        ),
    ):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)
        if player:
            if len(player.current_queue()) == 0:
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
                return

            if loop_mode == "Single":
                song = await player.toggle_song_loop()

                if player.music_loop == "single":
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["enabled_loop_single"].format(title=song.name),
                            message_type="success",
                        )
                    )
                else:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["disabled_loop_single"].format(title=song.name),
                            message_type="success",
                        )
                    )
            elif loop_mode == "All":
                song = await player.toggle_queue_loop()

                if player.music_loop == "queue":
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["enabled_loop_queue"],
                            message_type="success",
                        )
                    )
                else:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["disabled_loop_queue"],
                            message_type="success",
                        )
                    )
            else:
                await player.disable_loop()

                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "disabled_loop"
                        ],
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
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @nextcord.slash_command(description="🎵 | Stop the music!")
    async def stop(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)
        if player:
            if len(player.current_queue()) == 0:
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
                return

            await player.stop()
            music.remove_player(interaction.guild.id)

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

        else:
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

    @nextcord.slash_command(description="🎵 | Change the volume!")
    async def volume(
        self,
        interaction: Interaction,
        vol: int = SlashOption(name="volume", description="Select a desired volume!"),
    ):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)
        if player:
            if len(player.current_queue()) == 0:
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
                return

            song, volume = await player.change_volume(float(vol) / 100)
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "changed_volume"
                    ].format(title=song.name, volume=volume * 100),
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
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @nextcord.slash_command(description="🎵 | Skip the music!")
    async def skip(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)
        if player:
            if len(player.current_queue()) == 0:
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
                return

            old, new = await player.skip(force=True)

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
        else:
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

    @nextcord.slash_command(description="🎵 | Go back to the previous song!")
    async def previous(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)
        if player:
            if len(player.current_queue()) == 0:
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
                return

            old, new = await player.previous()

            if not new is None:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "replayed_from"
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
                            "replayed"
                        ].format(old=old.name),
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
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @nextcord.slash_command(description="🎵 | Get the current music queue.")
    async def queue(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)
        if player:
            if len(player.current_queue()) == 0:
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
                return

            async def get_page(page: int):
                player = music.get_player(guild_id=interaction.guild.id)
                if player:
                    if len(player.current_queue()) == 0:
                        return (
                            Embeds.message(
                                title=lang[
                                    await get_guild_language(interaction.guild.id)
                                ][class_namespace],
                                message=lang[
                                    await get_guild_language(interaction.guild.id)
                                ]["nothing_is_playing"],
                                message_type="warn",
                            ),
                            1,
                        )

                    duration_passed = round(player.now_playing().timer.elapsed)
                    duration_song_str = str(
                        timedelta(seconds=(player.now_playing().duration))
                    )
                    duration_passed_str = str(timedelta(seconds=(duration_passed)))

                    embed = nextcord.Embed(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            "currently_playing"
                        ].format(title=player.now_playing().title),
                        description=f"{progressBar.splitBar(player.now_playing().duration, duration_passed)[0]} | {duration_passed_str}/{duration_song_str}",
                        color=type_color["list"],
                    )

                    for i, song in enumerate(player.current_queue()):
                        if (page - 1) * 10 <= i < (page) * 10:
                            if (song == player.now_playing()) and i == 0:
                                pass
                            else:
                                duration_str = str(timedelta(seconds=(song.duration)))
                                views_str = "{:,}".format(song.views)

                                embed.add_field(
                                    name=f"{i}. {song.title}",
                                    value=f"⏳ {duration_str} | 👁️ {views_str}",
                                    inline=False,
                                )

                    total_pages = Pagination.compute_total_pages(
                        len(player.current_queue()), 10
                    )
                    embed.set_footer(text=f"{page}/{total_pages}")
                    return embed, total_pages
                else:
                    return (
                        Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["nothing_is_playing"],
                            message_type="warn",
                        ),
                        1,
                    )

            await Pagination(interaction, get_page).navegate()

        else:
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

    @nextcord.slash_command(description="🎵 |Shuffles the queue.")
    async def shuffle(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            if len(player.current_queue()) == 0:
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
                return

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

        else:
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

    @nextcord.slash_command(description="🎵 | Pause the music!")
    async def pause(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            if len(player.current_queue()) == 0:
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
                return

            if player.paused:
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
            else:
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

        else:
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

    @nextcord.slash_command(description="🎵 | Resume the music!")
    async def resume(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            if len(player.current_queue()) == 0:
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
                return

            if not player.paused:
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
            else:
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

        else:
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

    @nextcord.slash_command(description="🎵 | Remove from queue!")
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

        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            if len(player.current_queue()) == 0 and index < -1:
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
                return

            if len(player.current_queue()) < index:
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
            else:
                song = await player.remove_from_queue(index)

                await interaction.followup.send(
                    embed=Embeds.message(
                        title=lang[await get_guild_language(interaction.guild.id)][
                            class_namespace
                        ],
                        message=lang[await get_guild_language(interaction.guild.id)][
                            "removed_song"
                        ].format(title=song.name),
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
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @nextcord.slash_command(description="🎵 | Jump to...")
    async def jump(
        self,
        interaction: Interaction,
        index: int = nextcord.SlashOption(
            name="index",
            description="The position of the song in the queue!",
            required=False,
        ),
    ):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            if len(player.current_queue()) == 0:
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
                return

            if len(player.current_queue()) < index or index <= 0:
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
            else:
                old, new = await player.jump(index)

                if not new is None:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["jumped_from"].format(old=old.name, new=new.name),
                            message_type="success",
                        )
                    )
                else:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=lang[await get_guild_language(interaction.guild.id)][
                                class_namespace
                            ],
                            message=lang[
                                await get_guild_language(interaction.guild.id)
                            ]["jumped"].format(old=old.name),
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
                        "nothing_is_playing"
                    ],
                    message_type="warn",
                )
            )

    @nextcord.slash_command(description="🎵 | Now playing...")
    async def nowplaying(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            if len(player.current_queue()) == 0:
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
                return

            song = player.now_playing()

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

        else:
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


def setup(bot):
    bot.add_cog(Music(bot))
