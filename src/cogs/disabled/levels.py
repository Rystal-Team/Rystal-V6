import nextcord
import json
import os
import time
import asyncio

from typing import Optional
from nextcord.ext import commands
from easy_pil import Editor, load_image_async, Font
from nextcord import File
from config.config import level_class_title


class RankSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Leveling Cog Ready!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            with open("./levels.json", "r") as f:
                data = json.load(f)

            if str(message.author.id) in data:
                xp = data[str(message.author.id)]["xp"]
                lvl = data[str(message.author.id)]["level"]

                increased_xp = xp + 25
                new_level = int(increased_xp / 100)

                data[str(message.author.id)]["xp"] = increased_xp

                if new_level > lvl:
                    await message.channel.send(
                        f"{message.author.mention} Has Just Leveled Up to Level {new_level}!!!"
                    )

                    data[str(message.author.id)]["level"] = new_level
                    data[str(message.author.id)]["xp"] = 0

                    with open("./levels.json", "w") as f:
                        json.dump(data, f)

                newXP = int(data[str(message.author.id)]["xp"])
                userlvl = int(data[str(message.author.id)]["level"])
                usertotalxp = int(
                    ((((userlvl * userlvl) / 2) + (userlvl / 2)) * 100) + newXP
                )

                data[str(message.author.id)]["totalxp"] = usertotalxp
                with open("./levels.json", "w") as f:
                    json.dump(data, f)
            else:
                data[str(message.author.id)] = {}
                data[str(message.author.id)]["xp"] = 0
                data[str(message.author.id)]["totalxp"] = 0
                data[str(message.author.id)]["level"] = 0

                with open("./levels.json", "w") as f:
                    json.dump(data, f)

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
        if member is None:
            userr = interaction.user
        else:
            userr = member

        with open("./levels.json", "r") as f:
            data = json.load(f)

        if not str(userr.id) in data:
            data[str(userr.id)] = {}
            data[str(userr.id)]["xp"] = 0
            data[str(userr.id)]["level"] = 0
            data[str(userr.id)]["totalxp"] = 0

            with open("./levels.json", "w") as f:
                json.dump(data, f)

        xp = data[str(userr.id)]["xp"]
        lvl = data[str(userr.id)]["level"]

        next_level_xp = (lvl + 1) * 100
        xp_need = next_level_xp
        xp_have = data[str(userr.id)]["xp"]

        percentage = int(((xp_have * 100) / xp_need))

        if percentage < 1:
            percentage = 0

        # colors
        theme_color = "#5895DC"

        # Rank card
        background = Editor(f"./rankCardBase.png")
        profile = await load_image_async(str(userr.display_avatar.url))

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

        background.text((560, 70), f"Level", font=poppins_small, color="#e6e6e6")
        background.text((625, 57), f"{lvl}", font=poppins, color=theme_color)

        nameFont = Font.poppins(variant="bold", size=50)
        background.text(
            (200, 100), str(userr.display_name), font=nameFont, color=theme_color
        )

        background.text(
            (550, 167),
            f"{xp} / {(lvl+1) * 100} XP",
            font=poppins_small,
            color="#fff",
        )

        card = File(filename="RankCard.png", fp=background.image_bytes)
        await interaction.response.send_message(files=[card])

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
        await interaction.response.defer()
        if range is None:
            range = 5

        with open("./levels.json", "r") as f:
            data = json.load(f)

        mbed = nextcord.Embed(
            title=f"Leaderboard - Top {range}",
        )

        for user_id, user_data in sorted(
            data.items(), key=lambda x: x[1]["totalxp"], reverse=True
        )[:range]:
            member = await self.bot.fetch_user(user_id)
            mbed.add_field(
                name=member.display_name,
                value=f"**Level: {user_data['level']} | Total XP: {user_data['totalxp']}**",
                inline=False,
            )

        await interaction.followup.send(embed=mbed)

    @commands.command(name="rank_initialize")
    async def rank_initialize(self, ctx):
        level = {}
        with open("./levels.json", "r") as f:
            data = json.load(f)

        for userid in data:
            level[userid] = {}
            level[userid]["xp"] = data[str(userid)]["xp"]
            level[userid]["level"] = data[str(userid)]["level"]

            userlvl = int(data[str(userid)]["level"])
            usertotalxp = int(
                ((((userlvl * userlvl) / 2) + (userlvl / 2)) * 100)
                + int(data[str(userid)]["xp"])
            )

            level[userid]["totalxp"] = usertotalxp

        with open("./levels.json", "w") as f:
            json.dump(level, f)

        await ctx.send(f"{ctx.author.mention}, successfully intialized `levels.json`")


def setup(bot):
    bot.add_cog(RankSystem(bot))
