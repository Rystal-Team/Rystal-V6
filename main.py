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

import sys

sys.dont_write_bytecode = True

import asyncio
import datetime
import logging
import os
import traceback

import nest_asyncio
import nextcord
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

from nextcord.ext import commands
from termcolor import colored

from config.loader import bot_owner_id, error_log_channel_id, lang
from database.guild_handler import get_guild_language
from module.embeds.generic import Embeds

TOKEN = os.getenv("TOKEN")
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

if not os.path.exists("./logs"):
    os.makedirs("./logs")

if not os.path.exists("./sqlite"):
    os.makedirs("./sqlite")

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
bot.remove_command("help")
class_namespace = "system_class_title"

logger = logging.getLogger("nextcord")
logger.setLevel(logging.WARNING)
time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
handler = logging.FileHandler(
    filename=f"./logs/{time_str}.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


@bot.event
async def on_application_command_error(interaction, exception):
    if (
        str(exception)
        == "Command raised an exception: NotFound: 404 Not Found (error code: 10062): Unknown interaction"
    ):
        await interaction.channel.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "command_slowdown"
                ],
                message_type="warn",
            ),
        )
        return
    if not error_log_channel_id:
        return
    follow_up_sent = False
    error_msg = Embeds.message(
        title=lang[await get_guild_language(interaction.guild.id)][class_namespace],
        message=lang[await get_guild_language(interaction.guild.id)]["unknown_error"],
        message_type="error",
    )
    try:
        await interaction.followup.send(embed=error_msg)
        follow_up_sent = True
    except:
        try:
            await interaction.send(embed=error_msg)
            follow_up_sent = True
        except:
            pass

    channel = bot.get_channel(error_log_channel_id)
    identifier = getattr(
        interaction.application_command, "qualified_name", "Not Command"
    )
    full_error = traceback.format_exception(
        type(exception), exception, exception.__traceback__
    )
    exception_str = "".join(full_error)
    print(exception_str)

    message = f"""
**Error Logged!**
Command: **/{identifier}**
User: {interaction.user.name}
Channel: {interaction.channel.name} | {interaction.channel.mention}
Guild: {interaction.guild.name} | Owner: {interaction.guild.owner} | Humans: {len(interaction.guild.humans)}
Follow Up Sent: {follow_up_sent}
"""

    if "options" in interaction.data:
        message += f"\nOptions : {interaction.data['options']}"

    with open("exception.txt", "w") as f:
        f.write(exception_str)
    log_files = [nextcord.File("exception.txt")]

    if not follow_up_sent:
        not_sent_full_error = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )
        with open("send_exception.txt", "w") as f:
            f.write("".join(not_sent_full_error))
        log_files.append(nextcord.File("send_exception.txt"))

    await channel.send(content=message, files=log_files)
    owner = await bot.fetch_user(bot_owner_id)
    mention = await channel.send(content=f"{owner.mention}")
    await mention.delete()
    os.remove("exception.txt")
    if not follow_up_sent:
        os.remove("send_exception.txt")


async def setup():
    cogs = 0
    for root, dirs, files in os.walk("./cogs"):
        dirs[:] = [d for d in dirs if "disabled" and "__init__" not in d]
        files = [
            f for f in files if f.endswith(".py") and "disabled" and "__init__" not in f
        ]

        for filename in files:
            if (
                os.path.normpath(root) == os.path.normpath("./cogs/games")
                and filename != "base.py"
            ):
                continue
            cog_path = os.path.join(root, filename)
            relative_path = os.path.relpath(cog_path, "./cogs")
            module_name = relative_path.replace(os.sep, ".")[:-3]

            try:
                bot.load_extension(f"cogs.{module_name}")
                print(colored(text=f"Cogs: {module_name} is ready!", color="green"))
                cogs += 1
            except Exception as exception:
                full_error = traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
                print(
                    colored(
                        text=f"Unable to load {module_name} Error: {full_error}",
                        color="red",
                    )
                )
        for d in dirs:
            print(colored(text=f"Passed directory {d}", color="yellow"))

    return cogs


async def reloadSetup():
    cogs = 0
    for root, dirs, files in os.walk("./cogs"):
        dirs[:] = [d for d in dirs if "disabled" and "__init__" not in d]
        files = [
            f for f in files if f.endswith(".py") and "disabled" and "__init__" not in f
        ]

        for filename in files:
            if (
                os.path.normpath(root) == os.path.normpath("./cogs/games")
                and filename != "base.py"
            ):
                continue
            cog_path = os.path.join(root, filename)
            relative_path = os.path.relpath(cog_path, "./cogs")
            module_name = relative_path.replace(os.sep, ".")[:-3]

            try:
                bot.reload_extension(f"cogs.{module_name}")
                print(colored(text=f"Cogs: {module_name} is reloaded!", color="green"))
                cogs += 1
            except Exception as e:
                print(
                    colored(
                        text=f"Unable to reload {module_name} Error: {e}", color="red"
                    )
                )
        for d in dirs:
            print(colored(text=f"Passed directory {d}", color="yellow"))

    return cogs


@bot.command()
async def reloadcogs(ctx):
    if ctx.author.id == bot_owner_id:
        newcogs = await setup()
        reloadedcogs = await reloadSetup()
        await ctx.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(ctx.guild.id)][class_namespace],
                message=f"Reloaded {reloadedcogs} cogs, loaded {newcogs} new cogs.",
                message_type="info",
            )
        )
    else:
        await ctx.send(
            embed=Embeds.message(
                title=lang[await get_guild_language(ctx.guild.id)][class_namespace],
                message=lang[await get_guild_language(ctx.guild.id)][
                    "missing_permission"
                ],
                message_type="error",
            )
        )


@bot.slash_command(
    name="list",
    description="🤖 | See a list of servers that I am in!",
)
async def list(
    interaction: nextcord.Interaction,
):
    if interaction.user.id == bot_owner_id:
        para = "========= Guilds ========="
        for guild in bot.guilds:
            para = para + f"\nGuild: {guild.name} | Member: {guild.member_count}"

        await interaction.response.send_message(para, ephemeral=True)
    else:
        await interaction.response.send_message(
            embed=Embeds.message(
                title=lang[await get_guild_language(interaction.guild.id)][
                    class_namespace
                ],
                message=lang[await get_guild_language(interaction.guild.id)][
                    "missing_permission"
                ],
                message_type="warn",
            ),
            ephemeral=True,
        )


asyncio.run(setup())
bot.run(TOKEN)
