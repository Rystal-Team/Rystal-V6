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

from config.loader import lang, type_color
from database import user_handler
from database.guild_handler import get_guild_language
from module.games.roulette import RouletteResult, Roulette
from modules.dropdown import DropdownSelector
#rewrite this in dropdown.py ty

message_mapper = {
    RouletteResult.ZEROS: "roulette_zeros",
    RouletteResult.RED: "roulette_red",
    RouletteResult.BLACK: "roulette_black",
    RouletteResult.ODD: "roulette_odd",
    RouletteResult.EVEN: "roulette_even",
}


class RouletteView(nextcord.ui.View):
    def __init__(self, interaction, bet):
        super().__init__(timeout=120)
        self.interaction = interaction
        self.bet = bet
        self.guild_id = interaction.guild.id
        self.follow_up = None
        self.Wheel = [
            "Green 0", "Black 28", "Red 9", "Black 26", "Red 30", "Black 11", "Red 7", "Black 20", "Red 32", "Black 17", "Red 5", "Black 22", "Red 34", "Black 15", "Red 3", "Black 24", "Red 36", "Black 13", "Red 1", "Green 00", "Red 27", "Black 10", "Red 25", "Black 29", "Red 12", "Black 8", "Red 19", "Black 31", "Red 18", "Black 6", "Red 21", "Black 33", "Red 16", "Black 4", "Red 23", "Black 35", "Red 14", "Black 2"
        ]
        self.bet_options = ["zeros", "red", "black", "odd", "even"]

    def set_follow_up(self, follow_up):
        self.follow_up = follow_up

    async def get_lang(self):
        return lang[await get_guild_language(self.guild_id)]

    async def update_message(
        self,
        interaction,
        option,
        result,
        outcome,
        view=None,
    ):
        self.lang = await self.get_lang()
        embed = nextcord.Embed(title=self.lang["roulette_game_title"], description=self.lang["roulette_game_description"].format(result=outcome), color=typecolor["game"])
        embed.add_field(
            name=self.lang["roulette_your_bet"],
            value=option
        )
        embed.add_field(
            name=self.lang["roulette_result"],
            value=result
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def handle_bet_result(self, result):
        user_id = self.interaction.user.id
        user_data = await user_handler.get_user_data(user_id)
        bot_data = await user_handler.get_user_data(self.interaction.client.user.id)

        if result in {RouletteResult.RED, RouletteResult.ODD, RouletteResult.EVEN, RouletteResult.BLACK}:
            user_data["points"] += self.bet
            bot_data["points"] -= self.bet
        elif result == RouletteResult.ZEROS:
            user_data["points"] += self.bet * 10
            bot_data["points"] -= self.bet * 10
        elif result == RouletteResult.LOST:
            user_data["points"] -= self.bet
            bot_data["points"] += self.bet

        await user_handler.update_user_data(user_id, user_data)
        await user_handler.update_user_data(self.interaction.client.user.id, bot_data)
