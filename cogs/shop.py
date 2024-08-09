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

from config.loader import default_language, lang
from database import user_handler
from database.guild_handler import get_guild_language
from module.embeds.generic import Embeds

class_namespace = "shop_class_title"


class ShopSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description=lang[default_language][class_namespace])
    async def shop(
        self,
        interaction: nextcord.Interaction,
    ):
        return

    @shop.subcommand(description=lang[default_language]["shop_catalog_description"])
    async def catalog(self, interaction):
        pass

    @shop.subcommand(description=lang[default_language]["shop_buy_description"])
    async def buy(
        self,
        interaction,
        item_id: int = nextcord.SlashOption(
            description=lang[default_language]["shop_buy_item_id_description"],
            required=True,
        ),
    ):
        pass


def setup(bot):
    bot.add_cog(ShopSystem(bot))
