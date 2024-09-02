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

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from config.loader import default_language, lang, lang_list, lang_mapping
from database.guild_handler import (
    change_guild_language,
    change_guild_settings,
    get_guild_language,
    get_guild_settings,
)
from module.embeds.generic import Embeds

class_namespace = "setting_class_title"


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=lang[default_language][class_namespace])
    async def setting(
        self,
        interaction: Interaction,
    ):
        return

    @setting.subcommand(
        description=lang[default_language]["setting_language_description"]
    )
    async def language(
        self,
        interaction: Interaction,
        language: str = SlashOption(
            name="language",
            choices=lang_list,
            required=True,
            description=lang[default_language]["setting_language_option_description"],
        ),
    ):
        await interaction.response.defer(with_message=True)

        try:
            await change_guild_language(interaction.guild.id, lang_mapping[language])

            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "language_changed"
                    ].format(language=language),
                    message_type="info",
                )
            )
        except Exception:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "unknown_error"
                    ],
                    message_type="error",
                )
            )

    @setting.subcommand(description=lang[default_language]["setting_game_description"])
    async def game(self, interaction: Interaction):
        return

    @game.subcommand(
        description=lang[default_language]["setting_game_announce_channel_description"]
    )
    async def jackpot_announce_channel(
        self,
        interaction: Interaction,
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description=lang[default_language][
                "setting_game_announce_channel_option_description"
            ],
            required=True,
        ),
    ):
        await interaction.response.defer(with_message=True)
        await change_guild_settings(
            interaction.guild.id, "game_announce_channel", channel.id
        )

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "game_announce_channel_changed"
                ].format(channel=channel.mention),
                message_type="info",
            )
        )

    @setting.subcommand(description=lang[default_language]["setting_music_description"])
    async def music(self, interaction: Interaction):
        return

    @music.subcommand(
        description=lang[default_language]["setting_music_volume_description"]
    )
    async def silent_mode(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)
        toggle = not (
            await get_guild_settings(interaction.guild.id, "music_silent_mode")
        )

        await change_guild_settings(interaction.guild.id, "music_silent_mode", toggle)

        toggle_represent = {
            True: "on",
            False: "off",
        }

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "toggle_silent_mode"
                ].format(toggle=toggle_represent[toggle]),
                message_type="info",
            )
        )

    @music.subcommand(
        description=lang[default_language]["setting_music_auto_leave_description"]
    )
    async def auto_leave(self, interaction: Interaction):
        await interaction.response.defer(with_message=True)
        toggle = not (
            await get_guild_settings(interaction.guild.id, "music_auto_leave")
        )

        await change_guild_settings(interaction.guild.id, "music_auto_leave", toggle)

        toggle_represent = {
            True: "on",
            False: "off",
        }

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "toggle_auto_leave"
                ].format(toggle=toggle_represent[toggle]),
                message_type="info",
            )
        )

    @music.subcommand(
        description=lang[default_language]["setting_music_default_loop_description"]
    )
    async def default_loop_mode(
        self,
        interaction: Interaction,
        mode: str = nextcord.SlashOption(
            name="mode",
            description=lang[default_language][
                "setting_music_default_loop_mode_description"
            ],
            choices=[
                "Off",
                "Single",
                "All",
            ],
            required=True,
        ),
    ):
        await interaction.response.defer(with_message=True)
        loop_mode = {
            "Off": 1,
            "Single": 2,
            "All": 3,
        }

        await change_guild_settings(
            interaction.guild.id, "music_default_loop_mode", loop_mode[mode]
        )

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "default_loop_mode_changed"
                ].format(mode=mode),
                message_type="info",
            )
        )


async def setup(bot):
    bot.add_cog(Settings(bot))
