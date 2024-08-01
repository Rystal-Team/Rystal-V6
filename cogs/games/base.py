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
from nextcord.ext import commands

from module.embeds.blackjack import BlackjackView
from module.games.blackjack import Blackjack


class GameSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Start a game!")
    async def game(self, interaction: nextcord.Interaction):
        return

    @game.subcommand(description="Start a game of blackjack!")
    async def blackjack(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        blackjack = Blackjack()
        player_total, dealer_total = blackjack.start_game()
        embed = nextcord.Embed(title="Blackjack", description="Game started!")
        embed.add_field(
            name="Your hand",
            value=f"{blackjack.player_hand}, total: {player_total}",
        )
        embed.add_field(
            name="Dealer's hand",
            value=f"{blackjack.dealer_hand}, total: {dealer_total}",
        )
        view = BlackjackView(blackjack, interaction)
        await interaction.followup.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(GameSystem(bot))
