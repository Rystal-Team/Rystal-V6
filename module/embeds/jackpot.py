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
from module.utils import format_number


def create_jackpot_embed(
    won, result, jackpot_total, user_points, mega_score, deficient_score, guild_lang
):
    """
    Creates an embed for the jackpot game.

    Returns:
        discord.Embed: The jackpot game embed.
    """
    embed = nextcord.Embed(
        title=lang[guild_lang]["jackpot_game_title"],
        description=(
            lang[guild_lang]["jackpot_lost"]
            if not won
            else (
                lang[guild_lang]["jackpot_mega_score"].format(
                    points=format_number(jackpot_total)
                )
                if mega_score
                else (
                    lang[guild_lang]["jackpot_deficient_score"].format(
                        points=format_number(jackpot_total)
                    )
                    if deficient_score
                    else lang[guild_lang]["jackpot_won"].format(
                        points=format_number(jackpot_total)
                    )
                )
            )
        ),
        color=(
            type_color["lose"]
            if not won
            else type_color["big_win"] if mega_score else type_color["win"]
        ),
    )

    embed.add_field(
        name=lang[guild_lang]["jackpot_result"],
        value=f"`{' | '.join(result)}`",
        inline=False,
    )
    if won:
        embed.add_field(
            name=lang[guild_lang]["jackpot_won"],
            value=format_number(jackpot_total),
            inline=False,
        )
    else:
        embed.add_field(
            name=lang[guild_lang]["jackpot_point_lost"],
            value=format_number(1000),
            inline=False,
        )
    embed.add_field(
        name=lang[guild_lang]["game_your_points"],
        value=format_number(user_points),
        inline=False,
    )
    if not won:
        embed.add_field(
            name=lang[guild_lang]["jackpot_total_points"],
            value=format_number(jackpot_total),
            inline=False,
        )

    return embed
