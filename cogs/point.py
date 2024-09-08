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
from typing import Optional

import nextcord
from nextcord.ext import commands

from config.loader import banland, bot_owner_id, default_language, lang, point_receive_limit
from database import user_handler
from database.guild_handler import get_guild_language
from module.embeds.generic import Embeds
from module.utils import format_number

class_namespace = "point_class_title"


class PointSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=lang[default_language][class_namespace])
    async def points(
        self,
        interaction: nextcord.Interaction,
    ):
        return

    @points.subcommand(
        description=lang[default_language]["points_claim_description"],
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
        cooldown_period = datetime.timedelta(minutes=20)

        if now - last_claimed < cooldown_period:
            remaining_time = cooldown_period - (now - last_claimed)
            minutes, seconds = divmod(remaining_time.seconds, 60)
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "cooldown_message"
                    ].format(minutes=minutes, seconds=seconds),
                    message_type="error",
                ),
            )
            return

        points_to_claim = random.randint(999, 3500)
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
        description=lang[default_language]["points_give_description"],
    )
    async def give(
        self,
        interaction: nextcord.Interaction,
        recipient: nextcord.Member = nextcord.SlashOption(
            name="recipient",
            description=lang[default_language]["points_give_recipient_description"],
            required=True,
        ),
        amount: int = nextcord.SlashOption(
            name="amount",
            description=lang[default_language]["points_give_amount_description"],
            required=True,
        ),
        force: bool = nextcord.SlashOption(
            name="force",
            description=lang[default_language]["points_give_force_description"],
            required=False,
        ),
    ):
        await interaction.response.defer()
        giver_id = interaction.user.id
        recipient_id = recipient.id

        if recipient_id in banland:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "receive_not_allowed"
                    ].format(option="recipient"),
                    message_type="error",
                )
            )
            return

        if force and not giver_id == bot_owner_id:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "missing_permission"
                    ],
                    message_type="error",
                ),
            )
            return

        if amount <= 0 and not force:
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

        if giver_data["points"] < amount and not force:
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

        receive_reset_str = recipient_data["last_point_received"]
        if not isinstance(receive_reset_str, str):
            receive_reset_str = datetime.datetime.min.isoformat()

        last_received = datetime.datetime.fromisoformat(receive_reset_str)
        now = datetime.datetime.now()
        cooldown_period = datetime.timedelta(days=1)

        if now - last_received > cooldown_period:
            recipient_data["receive_limit_reached"] = False

        if recipient_data["receive_limit_reached"] and not force:
            remaining_time = cooldown_period - (now - last_received)
            hours, minutes, seconds = map(lambda x: int(x), [remaining_time.seconds//3600, remaining_time.seconds % 3600//60, remaining_time.seconds % 60])
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "recipient_limit_reached"
                    ].format(recipient=recipient.display_name, hours=hours, minutes=minutes, seconds=seconds),
                    message_type="error",
                ),
            )
            return

        if recipient_data["received_today"] + amount > point_receive_limit and not force:
            await interaction.followup.send(
                embed=Embeds.message(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    message=lang[await get_guild_language(interaction.guild.id)][
                        "higher_than_receive_limit"
                    ].format(recipient=recipient.display_name, limit=point_receive_limit),
                    message_type="error",
                ),
            )
            return

        if not force:
            giver_data["points"] -= amount
            recipient_data["received_today"] += amount
        recipient_data["points"] += amount
        recipient_data["last_point_received"] = now.isoformat()

        if recipient_data["received_today"] + amount >= point_receive_limit and not force:
            print("yes")
            recipient_data["receive_limit_reached"] = True

        await user_handler.update_user_data(giver_id, giver_data)
        await user_handler.update_user_data(recipient_id, recipient_data)

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "points_given"
                ].format(
                    amount=format_number(amount), recipient=recipient.display_name
                ),
                message_type="success",
            ),
        )

    @points.subcommand(
        description=lang[default_language]["points_show_description"],
    )
    async def show(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description=lang[default_language]["points_show_user_description"],
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
            ].format(user=user.display_name, points=format_number(points))
        else:
            message = lang[await get_guild_language(interaction.guild.id)][
                "points_show_self"
            ].format(points=format_number(points))

        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=message,
                message_type="info",
            ),
        )

    @points.subcommand(
        description=lang[default_language]["points_leaderboard_description"],
    )
    async def leaderboard(
        self,
        interaction: nextcord.Interaction,
        include: Optional[int] = nextcord.SlashOption(
            name="include",
            description=lang[default_language][
                "points_leaderboard_include_description"
            ],
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

        result = await user_handler.get_leaderboard(include, order_by="points")

        mbed = nextcord.Embed(
            title=lang[await get_guild_language(interaction.guild.id)][
                "points_leaderboard_header"
            ].format(include=include),
        )

        for user_id, data in result.items():
            member = await self.bot.fetch_user(user_id)
            mbed.add_field(
                name=member.display_name,
                value=lang[await get_guild_language(interaction.guild.id)][
                    "points_leaderboard_user_row"
                ].format(points=format_number(data["points"])),
                inline=False,
            )

        await interaction.followup.send(embed=mbed)


def setup(bot):
    bot.add_cog(PointSystem(bot))
