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

from config.loader import lang
from database import user_handler
from database.guild_handler import get_guild_language
from module.games.roulette import RouletteResult, Roulette
from module.dropdown import DropdownSelector

# rewrite this in dropdown.py ty

message_mapper = {
    RouletteResult.ZEROS: "roulette_zeros",
    RouletteResult.RED: "roulette_red",
    RouletteResult.BLACK: "roulette_black",
    RouletteResult.ODD: "roulette_odd",
    RouletteResult.EVEN: "roulette_even",
}


class RouletteView(nextcord.ui.View):
    def __init__(self, interaction, bet, outcome):
        super().__init__(timeout=120)
        self.interaction = interaction
        self.bet = bet
        self.guild_id = interaction.guild.id
        self.follow_up = None
        self.bet_options = ["green", "red", "black", "odd", "even"]

    def set_follow_up(self, follow_up):
        self.follow_up = follow_up

    async def get_lang(self):
        return lang[await get_guild_language(self.guild_id)]

    async def update_message(
        self,
        interaction,
        bet,
        result,
        outcome,
        view=None,
    ):
        self.lang = await self.get_lang()
        embed = nextcord.Embed(
            title=self.lang["roulette_game_title"],
            description=self.lang["roulette_game_description"].format(result=outcome),
            color=typecolor["game"],
        )
        embed.add_field(
            name=self.lang["roulette_your_bet"],
            value=bet
        )
        embed.add_field(
            name=self.lang["roulette_result"],
            value=result
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def handle_bet_result(self, roulette):
        user_id = self.interaction.user.id
        user_data = await user_handler.get_user_data(user_id)
        bot_data = await user_handler.get_user_data(self.interaction.client.user.id)

        outcome, result = Roulette.check_winner(roulette)
        if outcome in {
            RouletteResult.RED,
            RouletteResult.ODD,
            RouletteResult.EVEN,
            RouletteResult.BLACK,
        }:
            user_data["points"] += self.bet
            bot_data["points"] -= self.bet
        elif outcome == RouletteResult.ZEROS:
            user_data["points"] += self.bet * 10
            bot_data["points"] -= self.bet * 10
        elif outcome == RouletteResult.LOST:
            user_data["points"] -= self.bet
            bot_data["points"] += self.bet

        await user_handler.update_user_data(user_id, user_data)
        await user_handler.update_user_data(self.interaction.client.user.id, bot_data)

        return result

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user == self.author

    async def on_selected(self, _, option):
        result_type, result = Roulette.check_winner(option)

        if await self.handle_bet_result(result_type) == RouletteResult.LOST:
            outcome = "Lose"
        else:
            outcome = "Win"

        await self.update_message(
            self.interaction,
            option,
            result,
            outcome,
        )

    async def start(self, interaction: nextcord.Interaction):
        print("dropdown")
        self.author = interaction.user
        self.channel = interaction.channel
        self.interaction = interaction
        dropdown = DropdownSelector(
            options=self.bet_options,
            placeholder=self.placeholder,
            async_callback=self.on_selected,
        )
        self.add_item(dropdown)
        await interaction.followup.send("Selector", view=self)

    async def on_timeout(self):
        self.lang = await self.get_lang()
        outcome = await self.handle_bet_result(RouletteResult.LOST)

        await self.update_message(
            self.interaction,
            "None",
            "None",
            outcome
        )

    @nextcord.ui.select(placeholder="Select a bet")
    async def bet_select(self, interaction: nextcord.ui.Select):
        print("dropdown")
        self.author = interaction.user
        self.channel = interaction.channel
        self.interaction = interaction
        dropdown = DropdownSelector(
            options=self.bet_options,
            placeholder=self.placeholder,
            async_callback=self.on_selected,
        )
        self.add_item(dropdown)
        await interaction.followup.send("Selector", view=self)
