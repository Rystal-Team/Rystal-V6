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

import random

import nextcord
from nextcord.ext import commands

from config.loader import default_lang, lang, type_color
from database import user_handler
from database.guild_handler import get_guild_language
from module.embeds.blackjack import BlackjackView
from module.embeds.generic import Embeds
from module.games.blackjack import Blackjack

class_namespace = "game_class_title"
MAX_DICE_LIMIT = 10


class GameSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=lang[default_lang][class_namespace])
    async def game(self, interaction: nextcord.Interaction):
        return

    @game.subcommand(description=lang[default_lang]["game_blackjack_description"])
    async def blackjack(
        self,
        interaction: nextcord.Interaction,
        bet: int = nextcord.SlashOption(
            name="bet",
            description=lang[default_lang]["game_blackjack_bet_description"],
            required=True,
        ),
    ):
        await interaction.response.defer()

        user_id = interaction.user.id
        user_data = await user_handler.get_user_data(user_id)
        bot_data = await user_handler.get_user_data(self.bot.user.id)

        if bet <= 0:
            await interaction.followup.send(
                embed=nextcord.Embed(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    description=lang[await get_guild_language(interaction.guild.id)][
                        "must_be_positive_not_zero"
                    ].format(option="bet"),
                    color=type_color["error"],
                )
            )
            return
        if bet > user_data["points"]:
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

        user_data["points"] -= bet
        bot_data["points"] += bet
        await user_handler.update_user_data(user_id, user_data)

        blackjack = Blackjack()
        player_total, dealer_total = blackjack.start_game()
        embed = nextcord.Embed(
            title=lang[await get_guild_language(interaction.guild.id)][
                "blackjack_game_title"
            ],
            description=lang[await get_guild_language(interaction.guild.id)][
                "blackjack_your_move"
            ],
            color=type_color["game"],
        )
        embed.add_field(
            name=lang[await get_guild_language(interaction.guild.id)][
                "blackjack_your_hand"
            ],
            value=f"{blackjack.player_hand}, total: {player_total}",
        )
        embed.add_field(
            name=lang[await get_guild_language(interaction.guild.id)][
                "blackjack_dealer_hand"
            ],
            value=f"{blackjack.dealer_hand}, total: {dealer_total}",
        )
        view = BlackjackView(blackjack, interaction, bet)
        follow_up_msg = await interaction.followup.send(embed=embed, view=view)
        view.set_follow_up(follow_up_msg)

    @game.subcommand(description=lang[default_lang]["game_dice_description"])
    async def dice(
        self,
        interaction: nextcord.Interaction,
        amount: int = nextcord.SlashOption(
            name="amount",
            description=lang[default_lang]["game_dice_amount_description"],
            required=False,
            default=1,
        ),
    ):
        await interaction.response.defer()

        if amount <= 0:
            await interaction.followup.send(
                embed=nextcord.Embed(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    description=lang[await get_guild_language(interaction.guild.id)][
                        "must_be_positive_not_zero"
                    ].format(option="number of dice"),
                    color=type_color["error"],
                )
            )
            return

        if amount > MAX_DICE_LIMIT:
            await interaction.followup.send(
                embed=nextcord.Embed(
                    title=lang[await get_guild_language(interaction.guild.id)][
                        class_namespace
                    ],
                    description=lang[await get_guild_language(interaction.guild.id)][
                        "exceeds_max_dice_limit"
                    ].format(limit=MAX_DICE_LIMIT),
                    color=type_color["error"],
                )
            )
            return

        dice_results = [random.randint(1, 6) for _ in range(amount)]
        total = sum(dice_results)

        embed = nextcord.Embed(
            title=lang[await get_guild_language(interaction.guild.id)][
                "dice_roll_title"
            ],
            description=lang[await get_guild_language(interaction.guild.id)][
                "dice_roll_description"
            ].format(num_dices=amount, total=total),
            color=type_color["game"],
        )
        embed.add_field(
            name=lang[await get_guild_language(interaction.guild.id)][
                "dice_roll_results"
            ],
            value=", ".join(map(str, dice_results)),
        )

        await interaction.followup.send(embed=embed)


def setup(bot):
    bot.add_cog(GameSystem(bot))
