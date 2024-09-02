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

from config.loader import (
    default_language,
    jackpot_base_amount,
    jackpot_tax_rate,
    lang,
    type_color,
)
from database import user_handler
from database.global_handler import change_global, get_global
from database.guild_handler import get_guild_language
from module.embeds.blackjack import BlackjackView
from module.embeds.generic import Embeds
from module.embeds.jackpot import create_jackpot_embed
from module.games.blackjack import Blackjack
from module.games.roulette import Roulette, RouletteResult
from module.games.spinner import Spinner
from module.utils import format_number

class_namespace = "game_class_title"
MAX_DICE_LIMIT = 10


class GameSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jackpot_spinner = Spinner()

    @nextcord.slash_command(description=lang[default_language][class_namespace])
    async def game(self, interaction: nextcord.Interaction):
        return

    @game.subcommand(description=lang[default_language][class_namespace])
    async def rules(self, interaction: nextcord.Interaction):
        return

    @rules.subcommand(
        name="jackpot",
        description=lang[default_language]["game_jackpot_rules_description"],
    )
    async def jackpot_rule(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    "jackpot_game_title"
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "game_jackpot_rules"
                ],
                message_type="info",
            )
        )

    @game.subcommand(description=lang[default_language]["game_blackjack_description"])
    async def blackjack(
        self,
        interaction: nextcord.Interaction,
        bet: int = nextcord.SlashOption(
            name="bet",
            description=lang[default_language]["game_blackjack_bet_description"],
            required=True,
        ),
    ):
        await interaction.response.defer()

        user_id = interaction.user.id
        user_data = await user_handler.get_user_data(user_id)

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

        user_data = await user_handler.get_user_data(interaction.user.id)
        bot_data = await user_handler.get_user_data(self.bot.user.id)

        bot_data["points"] -= bet
        user_data["points"] -= bet

        await user_handler.update_user_data(interaction.user.id, user_data)
        await user_handler.update_user_data(self.bot.user.id, bot_data)

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
            value=f"[{blackjack.hand_str(blackjack.player_hand)}] {lang[await get_guild_language(interaction.guild.id)]['blackjack_total'].format(total=player_total)}",
        )
        embed.add_field(
            name=lang[await get_guild_language(interaction.guild.id)][
                "blackjack_dealer_hand"
            ],
            value=f"[{blackjack.hand_str(blackjack.dealer_hand)}] {lang[await get_guild_language(interaction.guild.id)]['blackjack_total'].format(total=dealer_total)}",
        )
        view = BlackjackView(blackjack, interaction, bet, self.bot.user.id)
        follow_up_msg = await interaction.followup.send(embed=embed, view=view)
        view.set_follow_up(follow_up_msg)

    @game.subcommand(description=lang[default_language]["game_dice_description"])
    async def dice(
        self,
        interaction: nextcord.Interaction,
        amount: int = nextcord.SlashOption(
            name="amount",
            description=lang[default_language]["game_dice_amount_description"],
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

    @game.subcommand(
        description=lang[default_language]["game_coinflip_description"],
    )
    async def coinflip(
        self,
        interaction: nextcord.Interaction,
        guess=nextcord.SlashOption(
            name="guess", choices=["Heads", "Tails"], required=True
        ),
        bet: int = nextcord.SlashOption(
            name="bet",
            description=lang[default_language]["game_coinflip_bet_description"],
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
        bot_data = await user_handler.get_user_data(self.bot.user.id)
        if outcome == guess:
            data["points"] += bet
            bot_data["points"] -= bet
            result_message = lang[await get_guild_language(interaction.guild.id)][
                "coinflip_win"
            ].format(points=format_number(bet))
        else:
            data["points"] -= bet
            bot_data["points"] += bet
            result_message = lang[await get_guild_language(interaction.guild.id)][
                "coinflip_lose"
            ].format(points=format_number(bet))

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

    @game.subcommand(
        description=lang[default_language]["game_roulette_description"],
    )
    async def roulette(
        self,
        interaction: nextcord.Interaction,
        bet: int = nextcord.SlashOption(
            name="amount",
            description=lang[default_language]["game_roulette_bet_description"],
            required=True,
        ),
        guess=nextcord.SlashOption(
            name="bet", choices=["Green", "Red", "Black"], required=True
        ),
    ):
        await interaction.response.defer()
        user_id = interaction.user.id

        message_mapper = {
            RouletteResult.ZEROS: "roulette_won_zeros",
            RouletteResult.RED: "roulette_won",
            RouletteResult.BLACK: "roulette_won",
            RouletteResult.LOST: "roulette_lost",
        }

        user_data = await user_handler.get_user_data(user_id)
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
        if user_data["points"] < bet:
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

        roulette = Roulette().spin_wheel()
        bot_data = await user_handler.get_user_data(self.bot.user.id)

        outcome, result = Roulette.check_winner(roulette, guess)
        if outcome in {
            RouletteResult.RED,
            RouletteResult.BLACK,
        }:
            user_data["points"] += bet
            bot_data["points"] -= bet
        elif outcome == RouletteResult.ZEROS:
            user_data["points"] += bet * 5
            bot_data["points"] -= bet * 5
        elif outcome == RouletteResult.LOST:
            user_data["points"] -= bet
            bot_data["points"] += bet

        await user_handler.update_user_data(user_id, user_data)
        await user_handler.update_user_data(self.bot.user.id, bot_data)

        embed = nextcord.Embed(
            title=lang[await get_guild_language(interaction.guild.id)][
                "roulette_game_title"
            ],
            description=lang[await get_guild_language(interaction.guild.id)][
                message_mapper[outcome]
            ].format(
                points=format_number(
                    bet
                    if outcome
                    in {RouletteResult.RED, RouletteResult.BLACK, RouletteResult.LOST}
                    else bet * 5
                )
            ),
            color=(
                type_color["win"]
                if not outcome == RouletteResult.LOST
                else type_color["lose"]
            ),
        )
        embed.add_field(
            name=lang[await get_guild_language(interaction.guild.id)][
                "roulette_your_bet"
            ],
            value=guess,
        )
        embed.add_field(
            name=lang[await get_guild_language(interaction.guild.id)][
                "roulette_result"
            ],
            value=result,
        )

        await interaction.followup.send(embed=embed)

    @game.subcommand(
        description=lang[default_language]["game_jackpot_description"],
    )
    async def jackpot(
        self,
        interaction: nextcord.Interaction,
    ):
        await interaction.response.defer()
        jackpot_total = await get_global("jackpot_total")
        if jackpot_total is None or jackpot_total < jackpot_base_amount:
            await change_global("jackpot_total", jackpot_base_amount)
            jackpot_total = jackpot_base_amount

        user_data = await user_handler.get_user_data(interaction.user.id)
        if user_data["points"] < 1000:
            return await interaction.followup.send(
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

        user_data["points"] -= 1000
        await user_handler.update_user_data(interaction.user.id, user_data)
        await change_global("jackpot_total", jackpot_total + 1000)
        jackpot_total = await get_global("jackpot_total")

        won, result, mega_score, deficient_score = self.jackpot_spinner.play()
        new_total = jackpot_total

        if won:
            # chunky code here, but it's just a simple jackpot result calculation lmao
            # if you want to make it more readable, help yourself
            if mega_score:
                new_total = round(jackpot_total * 1.5)
                bot_tax = round(jackpot_tax_rate * new_total)
                user_data["points"] += new_total - bot_tax
                await change_global("jackpot_total", jackpot_base_amount)
                bot_data = await user_handler.get_user_data(self.bot.user.id)
                bot_data["points"] += (
                    bot_tax - round(new_total - jackpot_total) - jackpot_base_amount
                )
            elif deficient_score:
                new_total = round(jackpot_total * 0.8)
                bot_tax = round(jackpot_tax_rate * new_total)
                user_data["points"] += new_total - bot_tax
                await change_global("jackpot_total", jackpot_base_amount)
                bot_data = await user_handler.get_user_data(self.bot.user.id)
                bot_data["points"] += (
                    bot_tax + round(jackpot_total - new_total) - jackpot_base_amount
                )
            else:
                bot_tax = round(jackpot_tax_rate * jackpot_total)
                user_data["points"] += jackpot_total - bot_tax
                await change_global("jackpot_total", jackpot_base_amount)
                bot_data = await user_handler.get_user_data(self.bot.user.id)
                bot_data["points"] += bot_tax - jackpot_base_amount
            await user_handler.update_user_data(self.bot.user.id, bot_data)
            await user_handler.update_user_data(interaction.user.id, user_data)

        await interaction.followup.send(
            embed=create_jackpot_embed(
                won,
                result,
                new_total,
                user_data["points"],
                mega_score,
                deficient_score,
                await get_guild_language(interaction.guild.id),
            ),
        )

        return

    @game.subcommand(
        description=lang[default_language]["game_showjackpot_description"],
    )
    async def showjackpot(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        jackpot_total = await get_global("jackpot_total")
        if jackpot_total is None:
            jackpot_total = jackpot_base_amount
        await interaction.followup.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    "jackpot_game_title"
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "jackpot_show_total"
                ].format(points=format_number(jackpot_total)),
                message_type="info",
            )
        )
        return jackpot_total


def setup(bot):
    bot.add_cog(GameSystem(bot))
