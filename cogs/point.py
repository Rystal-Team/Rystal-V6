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

import datetime
import random

import nextcord
from nextcord.ext import commands

from config.config import lang
from database import user_handler
from database.guild_handler import get_guild_language
from module.embeds.generic import Embeds

class_namespace = "point_class_title"


class PointSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=class_namespace)
    async def points(
        self,
        interaction: nextcord.Interaction,
    ):
        return

    @points.subcommand(
        description="🎖️ | Claim your daily points (10-2000)!",
    )
    async def claim(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        data = await user_handler.get_user_data(user_id)

        last_claimed_str = data["last_point_claimed"]
        if not isinstance(last_claimed_str, str):
            last_claimed_str = datetime.datetime.min.isoformat()

        last_claimed = datetime.datetime.fromisoformat(last_claimed_str)
        now = datetime.datetime.now()
        cooldown_period = datetime.timedelta(hours=2)

        if now - last_claimed < cooldown_period:
            remaining_time = cooldown_period - (now - last_claimed)
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "cooldown_message"
                    ].format(hours=hours, minutes=minutes, seconds=seconds),
                    message_type="error",
                ),
            )
            return

        points_to_claim = random.randint(10, 2000)
        data["points"] += points_to_claim
        data["last_point_claimed"] = now.isoformat()
        await user_handler.update_user_data(user_id, data)

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "points_claimed"
                ].format(points=points_to_claim),
                message_type="success",
            ),
        )

    @points.subcommand(
        description="🎖️ | Bet your points on a coin flip!",
    )
    async def coinflip(
        self,
        interaction: nextcord.Interaction,
        guess=nextcord.SlashOption(
            name="guess", choices=["Heads", "Tails"], required=True
        ),
        bet: int = nextcord.SlashOption(
            name="bet",
            description="How much are you willing to bet?",
            required=True,
        ),
    ):
        await interaction.response.defer()
        user_id = interaction.user.id

        data = await user_handler.get_user_data(user_id)
        if bet < 0:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "must_be_positive"
                    ].format(option="bet"),
                    message_type="error",
                ),
            )
            return
        if data["points"] < bet:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "not_enough_points"
                    ],
                    message_type="error",
                ),
            )
            return

        outcome = random.choice(["Heads", "Tails"])
        if outcome == guess:
            data["points"] += bet
            result_message = lang[await get_guild_language(interaction.guild.id)][
                "coinflip_win"
            ].format(points=bet)
        else:
            data["points"] -= bet
            result_message = lang[await get_guild_language(interaction.guild.id)][
                "coinflip_lose"
            ].format(points=bet)

            bot_data = await user_handler.get_user_data(self.bot.user.id)
            bot_data["points"] += bet
            await user_handler.update_user_data(self.bot.user.id, bot_data)

        await user_handler.update_user_data(user_id, data)

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=result_message,
                message_type="win" if outcome == guess else "lose",
            ),
        )

    @points.subcommand(
        description="🎖️ | Give your points to another user!",
    )
    async def give(
        self,
        interaction: nextcord.Interaction,
        recipient: nextcord.Member = nextcord.SlashOption(
            name="recipient",
            description="The user you want to give points to",
            required=True,
        ),
        amount: int = nextcord.SlashOption(
            name="amount",
            description="The amount of points you want to give",
            required=True,
        ),
    ):
        await interaction.response.defer()
        giver_id = interaction.user.id
        recipient_id = recipient.id

        if amount <= 0:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "must_be_positive"
                    ].format(option="amount"),
                    message_type="error",
                ),
            )
            return

        giver_data = await user_handler.get_user_data(giver_id)
        recipient_data = await user_handler.get_user_data(recipient_id)

        if giver_data["points"] < amount:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "not_enough_points"
                    ],
                    message_type="error",
                ),
            )
            return

        giver_data["points"] -= amount
        recipient_data["points"] += amount

        await user_handler.update_user_data(giver_id, giver_data)
        await user_handler.update_user_data(recipient_id, recipient_data)

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "points_given"
                ].format(amount=amount, recipient=recipient.display_name),
                message_type="success",
            ),
        )

    @points.subcommand(
        description="🎖️ | Show your points or another user's points!",
    )
    async def show(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="The user whose points you want to see",
            required=False,
        ),
    ):
        await interaction.response.defer()
        user_id = user.id if user else interaction.user.id
        user_data = await user_handler.get_user_data(user_id)
        points = user_data["points"]

        if user:
            message = lang[await get_guild_language(interaction.guild.id)][
                "points_show_user"
            ].format(user=user.display_name, points=points)
        else:
            message = lang[await get_guild_language(interaction.guild.id)][
                "points_show_self"
            ].format(points=points)

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=message,
                message_type="info",
            ),
        )


def setup(bot):
    bot.add_cog(PointSystem(bot))
