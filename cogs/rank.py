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

from io import BytesIO
from typing import Optional

import nextcord
from PIL import Image, ImageDraw, ImageFont
from nextcord import File
from nextcord.ext import commands

from config.loader import default_language, lang, theme_color
from config.perm import auth_guard
from database import user_handler
from database.guild_handler import get_guild_language
from module.embeds.generic import Embeds
from module.utils import format_number

class_namespace = "rank_class_title"


class RankSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            data = await user_handler.get_user_data(message.author.id)

            xp = data["xp"]
            lvl = data["level"]

            increased_xp = xp + 25
            new_level = round(increased_xp / 100)

            data["xp"] = increased_xp

            if new_level > lvl:
                data["level"] = new_level
                data["xp"] = 0

            new_xp = int(data["xp"])
            userlvl = int(data["level"])
            usertotalxp = int(
                ((((userlvl * userlvl) / 2) + (userlvl / 2)) * 100) + new_xp
            )

            data["totalxp"] = usertotalxp
            await user_handler.update_user_data(message.author.id, data)

            if new_level > lvl:
                await message.channel.send(
                    lang[await get_guild_language(message.guild.id)]["level_up"].format(
                        user=message.author.mention, level=data["level"]
                    )
                )

    @nextcord.slash_command(description=lang[default_language][class_namespace])
    async def rank(
        self,
        interaction: nextcord.Interaction,
    ):
        return

    @rank.subcommand(
        description=lang[default_language]["rank_card_description"],
    )
    @auth_guard.check_permissions("setting/rank/card")
    async def card(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.User] = nextcord.SlashOption(
            name="member",
            description=lang[default_language]["rank_card_member_description"],
            required=False,
        ),
    ):
        await interaction.response.defer()

        if member is None:
            user = interaction.user
        else:
            user = member

        data = await user_handler.get_user_data(user.id)

        xp = data["xp"]
        lvl = data["level"]

        next_level_xp = (lvl + 1) * 100
        xp_need = next_level_xp
        xp_have = data["xp"]

        percentage = int(((xp_have * 100) / xp_need))

        if percentage < 1:
            percentage = 0

        # Rank card
        background = Image.open("./rankCardBase.png").convert("RGBA")
        profile = Image.open(BytesIO(await user.display_avatar.read())).convert("RGBA")
        profile = profile.resize((135, 135), Image.LANCZOS)
        mask = Image.new("L", profile.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + profile.size, fill=255)
        profile.putalpha(mask)

        background.paste(profile, (40, 70), profile)

        draw = ImageDraw.Draw(background)
        font_paths = {
            "title": "./font/GoNotoKurrent-Bold.ttf",
            "description": "./font/GoNotoKurrent-Regular.ttf",
        }
        title_font = ImageFont.truetype(font_paths["title"], 45)
        description_font = ImageFont.truetype(font_paths["description"], 22)

        draw.rectangle((200, 200, 700, 208), fill="#D7D7D7", outline=None)
        draw.rectangle(
            (200, 200, 200 + int(500 * (percentage / 100)), 208),
            fill=theme_color,
            outline=None,
        )

        draw.text(
            (560, 75),
            lang[await get_guild_language(interaction.guild.id)]["level_text"],
            font=description_font,
            fill="#e6e6e6",
        )
        draw.text((625, 57), f"{lvl}", font=title_font, fill=theme_color)

        name_font = ImageFont.truetype(font_paths["title"], 50)
        draw.text((200, 100), str(user.global_name), font=name_font, fill=theme_color)

        draw.text(
            (560, 160),
            lang[await get_guild_language(interaction.guild.id)]["level_xp"].format(
                xp=format_number(xp), totalxp=format_number((lvl + 1) * 100)
            ),
            font=description_font,
            fill="#fff",
        )

        with BytesIO() as image_binary:
            background.save(image_binary, "PNG")
            image_binary.seek(0)
            card = File(fp=image_binary, filename="rankcard.png")
            await interaction.followup.send(files=[card])

    @rank.subcommand(
        description=lang[default_language]["rank_leaderboard_description"],
    )
    @auth_guard.check_permissions("setting/rank/leaderboard")
    async def leaderboard(
        self,
        interaction: nextcord.Interaction,
        include: Optional[int] = nextcord.SlashOption(
            name="include",
            description=lang[default_language]["rank_leaderboard_include_description"],
            required=False,
        ),
    ):
        if include is None:
            include = 5

        if include < 1 or include > 25:
            await interaction.response.send_message(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "leaderboard_out_of_range"
                    ],
                    message_type="warn",
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        result = await user_handler.get_leaderboard(include, order_by="total_xp")

        mbed = nextcord.Embed(
            title=lang[await get_guild_language(interaction.guild.id)][
                "leaderboard_header"
            ].format(include=include),
        )

        for user_id, data in result.items():
            member = await self.bot.fetch_user(user_id)
            mbed.add_field(
                name=member.display_name,
                value=lang[await get_guild_language(interaction.guild.id)][
                    "leaderboard_user_row"
                ].format(
                    level=format_number(data["level"]),
                    totalxp=format_number(data["totalxp"]),
                ),
                inline=False,
            )

        await interaction.followup.send(embed=mbed)


def setup(bot):
    bot.add_cog(RankSystem(bot))
