import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from module.musicPlayer import Music as MusicModule
from pytube import Playlist
from module.pagination import Pagination
from datetime import timedelta
from module.progressBar import progressBar
from config.config import type_color
from config.config import music_class_title as class_title
from module.embed import Embeds, NowPlayingMenu

music = MusicModule()

class_title = "🎵 | Music Module"


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.now_playing_menus = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog Ready!")

    @commands.Cog.listener()
    async def on_queue_ended(self, interaction):
        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title, message="Queue Ended!", message_type="info"
                )
            )
        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Music Player has been disconnected!",
                    message_type="info",
                )
            )

    @commands.Cog.listener()
    async def on_queue_track_start(self, interaction, song, player):
        for menu in self.now_playing_menus:
            if menu.is_timeout == True:
                self.now_playing_menus.remove(menu)
            else:
                await menu.update()

        if not player.silent_mode:
            await interaction.channel.send(
                embed=Embeds.message(
                    title=class_title,
                    message=f"Playing **{song.name}**",
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
                        title=class_title,
                        message="You are not in a voice channel!",
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

        if not interaction.guild.voice_client.is_playing():
            if is_playlist:
                follow_up_msg: nextcord.Message = await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message="Loading Playlist...",
                        message_type="info",
                    )
                )

                try:
                    for i, url in enumerate(playlist.video_urls):
                        await interaction.followup.edit_message(
                            message_id=follow_up_msg.id,
                            embed=Embeds.message(
                                title=class_title,
                                message=f"Loading: {progressBar.filledBar(len(playlist.video_urls), i + 1)[0]} {i + 1}/{len(playlist.video_urls)}",
                                message_type="info",
                            ),
                        )
                        que_suc, feed = await player.queue(
                            url, search=False, query=True
                        )

                        if not que_suc:
                            await interaction.channel.send(
                                embed=Embeds.message(
                                    title=class_title,
                                    message=f"Failed to add song **{url}!**",
                                    message_type="error",
                                )
                            )
                            return

                        if i == 0:
                            suc, song = await player.play(
                                query, search=False, query=True
                            )

                            if suc:
                                await interaction.channel.send(
                                    embed=Embeds.message(
                                        title=class_title,
                                        message=f"Playing **{song.name}** from **{playlist.title}**!",
                                        message_type="info",
                                    )
                                )

                    await interaction.followup.edit_message(
                        message_id=follow_up_msg.id,
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Queued Playlist **{playlist.title}**!",
                            message_type="success",
                        ),
                    )
                except Exception as e:
                    await interaction.followup.edit_message(
                        message_id=follow_up_msg.id,
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Invalid Playlist!",
                            message_type="error",
                        ),
                    )
            else:
                que_suc, feed = await player.queue(query, search=False, query=True)

                if not que_suc:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Failed to add song **{query}**!",
                            message_type="error",
                        )
                    )
                    return

                suc, song = await player.play(query, search=False, query=True)

                if suc:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Playing **{song.name}**!",
                            message_type="info",
                        )
                    )
                else:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Queued **{song.name}**!",
                            message_type="success",
                        )
                    )
        else:
            if is_playlist:
                follow_up_msg: nextcord.Message = await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message="Loading Playlist...",
                        message_type="info",
                    )
                )
                try:
                    for i, url in enumerate(playlist.video_urls):
                        await interaction.followup.edit_message(
                            message_id=follow_up_msg.id,
                            embed=Embeds.message(
                                title=class_title,
                                message=f"Loading: {progressBar.filledBar(len(playlist.video_urls), i + 1)[0]} {i + 1}/{len(playlist.video_urls)}",
                                message_type="info",
                            ),
                        )
                        que_suc, feed = await player.queue(
                            url, search=False, query=True
                        )

                        if not que_suc:
                            await interaction.channel.send(
                                embed=Embeds.message(
                                    title=class_title,
                                    message=f"Failed to add song **{url}**!",
                                    message_type="error",
                                )
                            )
                            return

                    await interaction.followup.edit_message(
                        message_id=follow_up_msg.id,
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Queued Playlist **{playlist.title}**!",
                            message_type="success",
                        ),
                    )
                except Exception as e:
                    await interaction.followup.edit_message(
                        message_id=follow_up_msg.id,
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Invalid Playlist!",
                            message_type="error",
                        ),
                    )
            else:
                que_suc, song = await player.queue(query, search=False, query=True)

                if not que_suc:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Failed to add song **{query}**!",
                            message_type="error",
                        )
                    )
                    return

                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message=f"Queued **{song.name}**!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            if loop_mode == "Single":
                song = await player.toggle_song_loop()

                if player.music_loop == "single":
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Enabled loop mode for **{song.name}**",
                            message_type="success",
                        )
                    )
                else:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Disabled loop mode for **{song.name}**",
                            message_type="success",
                        )
                    )
            elif loop_mode == "All":
                song = await player.toggle_queue_loop()

                if player.music_loop == "queue":
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Enabled loop mode for this queue!",
                            message_type="success",
                        )
                    )
                else:
                    await interaction.followup.send(
                        embed=Embeds.message(
                            title=class_title,
                            message=f"Disabled loop mode for this queue!",
                            message_type="success",
                        )
                    )
            else:
                await player.disable_loop()

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            await player.stop()
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message=f"Stopped the player!",
                    message_type="success",
                )
            )

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            song, volume = await player.change_volume(float(vol) / 100)
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message=f"Changed volume for **{song.name}** to {volume*100}%!",
                    message_type="success",
                )
            )

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            old, new = await player.skip(force=True)

            if not new is None:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message=f"Skipped from **{old.name}** to **{new.name}**!",
                        message_type="success",
                    )
                )
            else:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message=f"Skipped **{old.name}**!",
                        message_type="success",
                    )
                )
        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            old, new = await player.previous()

            if not new is None:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message=f"Replayed from **{old.name}** to **{new.name}**!",
                        message_type="success",
                    )
                )
            else:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message=f"Replayed **{old.name}**!",
                        message_type="success",
                    )
                )

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
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
                                title=class_title,
                                message="Nothing is playing!",
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
                        title=f"Currently Playing... {player.now_playing().title}",
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
                            title=class_title,
                            message="Nothing is playing!",
                            message_type="warn",
                        ),
                        1,
                    )

            await Pagination(interaction, get_page).navegate()

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            await player.shuffle()

            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Shuffled the queue!",
                    message_type="info",
                )
            )

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
                    message_type="warn",
                )
            )

    @nextcord.slash_command(
        description="🎵 | Turn on silent mode! (Mute track start notification)"
    )
    async def silent_mode(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)

        player = music.get_player(guild_id=interaction.guild.id)

        if player:
            if len(player.current_queue()) == 0:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            toggle = await player.toggle_silent_mode()

            toggle_represent = {
                True: "on",
                False: "off",
            }

            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message=f"Silent mode is {toggle_represent[toggle]}!",
                    message_type="info",
                )
            )

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            if player.paused:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message="Music already paused! use `/resume` to resume the music!",
                        message_type="warn",
                    )
                )
            else:
                await player.pause()

                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message="Paused the queue!",
                        message_type="info",
                    )
                )

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
                        message_type="warn",
                    )
                )
                return

            if not player.paused:
                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message="Music already playing! use `/pause` to pause the music!",
                        message_type="warn",
                    )
                )
            else:
                await player.resume()

                await interaction.followup.send(
                    embed=Embeds.message(
                        title=class_title,
                        message="Resumed the queue!",
                        message_type="info",
                    )
                )

        else:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=class_title,
                    message="Nothing is playing!",
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
                        title=class_title,
                        message="Nothing is playing!",
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
                    title=class_title,
                    message="Nothing is playing!",
                    message_type="warn",
                )
            )


def setup(bot):
    bot.add_cog(Music(bot))
