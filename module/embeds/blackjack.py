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

from config.config import lang, type_color
from database import user_handler
from database.guild_handler import get_guild_language
from module.games.blackjack import BlackjackResult

message_mapper = {
    BlackjackResult.PLAYER_BUSTS: "blackjack_player_busts",
    BlackjackResult.DEALER_BUSTS: "blackjack_dealer_busts",
    BlackjackResult.TIE: "blackjack_tie",
    BlackjackResult.PLAYER_WINS: "blackjack_player_wins",
    BlackjackResult.DEALER_WINS: "blackjack_dealer_wins",
    BlackjackResult.PLAYER_BLACKJACK: "blackjack_player_blackjack",
}


class BlackjackView(nextcord.ui.View):
    def __init__(self, blackjack, interaction, bet):
        super().__init__(timeout=120)
        self.blackjack = blackjack
        self.interaction = interaction
        self.guild_id = interaction.guild_id
        self.bet = bet
        self.follow_up = None
        self.ended = False

    def set_follow_up(self, follow_up):
        self.follow_up = follow_up

    async def get_lang(self):
        return lang[await get_guild_language(self.guild_id)]

    async def update_message(
        self,
        interaction,
        title,
        description,
        color,
        player_total,
        dealer_total,
        view=None,
    ):
        self.lang = await self.get_lang()
        embed = nextcord.Embed(title=title, description=description, color=color)
        embed.add_field(
            name=self.lang["blackjack_your_hand"],
            value=f"{self.blackjack.player_hand}, {self.lang['blackjack_total'].format(total=player_total)}",
        )
        embed.add_field(
            name=self.lang["blackjack_dealer_hand"],
            value=f"{self.blackjack.dealer_hand}, {self.lang['blackjack_total'].format(total=dealer_total)}",
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def handle_bet_result(self, result):
        self.ended = True
        user_id = self.interaction.user.id
        user_data = await user_handler.get_user_data(user_id)
        bot_data = await user_handler.get_user_data(self.interaction.client.user.id)

        if result in {BlackjackResult.PLAYER_WINS, BlackjackResult.DEALER_BUSTS}:
            user_data["points"] += self.bet * 2
            bot_data["points"] -= self.bet * 2
        elif result == BlackjackResult.PLAYER_BLACKJACK:
            user_data["points"] += round(self.bet * 2.5)
            bot_data["points"] -= round(self.bet * 2.5)
        elif result == BlackjackResult.TIE:
            user_data["points"] += self.bet
            bot_data["points"] -= self.bet

        await user_handler.update_user_data(user_id, user_data)
        await user_handler.update_user_data(self.interaction.client.user.id, bot_data)

    @nextcord.ui.button(label="Hit", style=nextcord.ButtonStyle.primary)
    async def hit_button(self, button, interaction):
        player_total, game_end = self.blackjack.hit(self.blackjack.player_hand)
        self.lang = await self.get_lang()
        if game_end:
            result = self.blackjack.check_winner()
            color = (
                type_color["win"]
                if result
                in {
                    BlackjackResult.PLAYER_WINS,
                    BlackjackResult.PLAYER_BLACKJACK,
                    BlackjackResult.DEALER_BUSTS,
                }
                else type_color["lose"]
            )
            await self.update_message(
                interaction,
                self.lang["blackjack_game_title"],
                self.lang[message_mapper[result]],
                color,
                player_total,
                self.blackjack.calculate_hand(self.blackjack.dealer_hand),
            )
            await self.handle_bet_result(result)
        else:
            await self.update_message(
                interaction,
                self.lang["blackjack_game_title"],
                self.lang["blackjack_your_move"],
                type_color["game"],
                player_total,
                self.blackjack.calculate_hand(self.blackjack.dealer_hand),
                self,
            )

    @nextcord.ui.button(label="Stand", style=nextcord.ButtonStyle.secondary)
    async def stand_button(self, button, interaction):
        dealer_total = self.blackjack.stand()
        self.lang = await self.get_lang()
        result = self.blackjack.check_winner()
        color = (
            type_color["win"]
            if result
            in {
                BlackjackResult.PLAYER_WINS,
                BlackjackResult.PLAYER_BLACKJACK,
                BlackjackResult.DEALER_BUSTS,
            }
            else type_color["lose"]
        )
        await self.update_message(
            interaction,
            self.lang["blackjack_game_title"],
            self.lang[message_mapper[result]],
            color,
            self.blackjack.calculate_hand(self.blackjack.player_hand),
            dealer_total,
        )
        await self.handle_bet_result(result)

    async def on_timeout(self):
        self.lang = await self.get_lang()
        await self.handle_bet_result(BlackjackResult.DEALER_WINS)
        player_total = self.lang["blackjack_total"].format(
            total=self.blackjack.calculate_hand(self.blackjack.player_hand)
        )
        dealer_total = self.lang["blackjack_total"].format(
            total=self.blackjack.calculate_hand(self.blackjack.dealer_hand)
        )
        if not self.ended:
            await self.interaction.followup.edit_message(
                message_id=self.follow_up.id,
                embed=nextcord.Embed(
                    title=self.lang["blackjack_game_title"],
                    description=self.lang["blackjack_timeout_message"],
                    color=type_color["lose"],
                )
                .add_field(
                    name=self.lang["blackjack_your_hand"],
                    value=f"{self.blackjack.player_hand}, {player_total}",
                )
                .add_field(
                    name=self.lang["blackjack_dealer_hand"],
                    value=f"{self.blackjack.dealer_hand}, {dealer_total}",
                ),
                view=None,
            )
