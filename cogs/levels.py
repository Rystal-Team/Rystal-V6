from typing import Optional

import nextcord, json
from easy_pil import Editor, Font, load_image_async
from nextcord import File
from nextcord.ext import commands
from module.embed import Embeds
from config.config import lang, theme_color
from database import rank_handler
from database.guild_handler import get_guild_language

class_namespace = "level_class_title"


class RankSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            data = await rank_handler.get_user_data(message.author.id)

            xp = data["xp"]
            lvl = data["level"]

            increased_xp = xp + 25
            new_level = round(increased_xp / 100)

            data["xp"] = increased_xp

            if new_level > lvl:
                data["level"] = new_level
                data["xp"] = 0

            newXP = int(data["xp"])
            userlvl = int(data["level"])
            usertotalxp = int(
                ((((userlvl * userlvl) / 2) + (userlvl / 2)) * 100) + newXP
            )

            data["totalxp"] = usertotalxp
            await rank_handler.update_user_data(message.author.id, data)

            if new_level > lvl:
                await message.channel.send(
                    lang[await get_guild_language(message.guild.id)]["level_up"].format(
                        user=message.author.mention, level=data["level"]
                    )
                )

    @nextcord.slash_command(
        name="rank",
        description="🎖️ | Get your rank or other member's rank!",
    )
    async def rank(
        self,
        interaction: nextcord.Interaction,
        member: Optional[nextcord.User] = nextcord.SlashOption(
            name="member",
            description="Choose a user to view their rank!",
            required=False,
        ),
    ):
        await interaction.response.defer()

        if member is None:
            user = interaction.user
        else:
            user = member

        data = await rank_handler.get_user_data(user.id)

        xp = data["xp"]
        lvl = data["level"]

        next_level_xp = (lvl + 1) * 100
        xp_need = next_level_xp
        xp_have = data["xp"]

        percentage = int(((xp_have * 100) / xp_need))

        if percentage < 1:
            percentage = 0

        # Rank card
        background = Editor(f"./rankCardBase.png")
        profile = await load_image_async(str(user.display_avatar.url))

        profile = Editor(profile).resize((135, 135)).circle_image()

        poppins = Font.poppins(variant="bold", size=45)
        poppins_small = Font.poppins(size=22)

        background.paste(profile.image, (40, 70))

        background.rectangle((200, 200), width=500, height=8, fill="#D7D7D7", radius=5)
        background.bar(
            (200, 200),
            max_width=500,
            height=8,
            percentage=percentage,
            fill=theme_color,
            radius=5,
        )

        background.text(
            (560, 70),
            lang[await get_guild_language(interaction.guild.id)]["level_text"],
            font=poppins_small,
            color="#e6e6e6",
        )
        background.text((625, 57), f"{lvl}", font=poppins, color=theme_color)

        nameFont = Font.poppins(variant="bold", size=50)
        background.text(
            (200, 100), str(user.global_name), font=nameFont, color=theme_color
        )

        background.text(
            (550, 167),
            lang[await get_guild_language(interaction.guild.id)]["level_xp"].format(
                xp=xp, totalxp=(lvl+1) * 100
            ),
            font=poppins_small,
            color="#fff",
        )

        card = File(filename="rankcard.png", fp=background.image_bytes)
        await interaction.followup.send(files=[card])

    @nextcord.slash_command(
        name="leaderboard",
        description="🎖️ | View the leaderboard of top ranked users!",
    )
    async def leaderboard(
        self,
        interaction: nextcord.Interaction,
        range: Optional[int] = nextcord.SlashOption(
            name="range",
            description="Select how many users you want to include on the list!",
            required=False,
        ),
    ):
        if range is None:
            range = 5

        if range < 1 or range > 50:
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

        result = await rank_handler.get_leaderboard(range)

        mbed = nextcord.Embed(
            title=lang[await get_guild_language(interaction.guild.id)][
                "leaderboard_header"
            ].format(range=range),
        )

        for user in result:
            member = await self.bot.fetch_user(user[0])
            data = json.loads(user[1])
            mbed.add_field(
                name=member.display_name,
                value=lang[await get_guild_language(interaction.guild.id)][
                    "leaderboard_user_row"
                ].format(level=data["level"], totalxp=data["totalxp"]),
                inline=False,
            )

        await interaction.followup.send(embed=mbed)


def setup(bot):

    bot.add_cog(RankSystem(bot))
