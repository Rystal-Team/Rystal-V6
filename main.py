import nextcord
import os
import asyncio
import traceback
from module.embed import Embeds
from config.config import type_color, bot_owner_id, error_log_channel_id
import datetime
from dotenv import load_dotenv

load_dotenv()

from nextcord.ext import commands

TOKEN = os.getenv("TOKEN")
intents = nextcord.Intents().all()
emcolor = 0x8042A9

bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
bot.remove_command("help")


@bot.event
async def on_ready():
    print("========= Rystal Bot is Online =========")
    for guild in bot.guilds:
        print(f"Guild: {guild.name} | Member: {guild.member_count}")


@bot.event
async def on_application_command_error(interaction, exception):
    if error_log_channel_id is not None:
        follow_up_sent = False
        not_sent_exception = None
        try:
            await interaction.followup.send(
                embed=Embeds.message(
                    title="🤖 | System",
                    message="Unknown Error Occured!",
                    message_type="error",
                )
            )

            follow_up_sent = True
        except Exception as e:
            not_sent_exception = e
            try:
                await interaction.send(
                    embed=Embeds.message(
                        title="🤖 | System",
                        message="Unknown Error Occured!",
                        message_type="error",
                    )
                )

                follow_up_sent = True
            except Exception as e:
                pass
                not_sent_exception = e
        finally:
            pass

        channel = bot.get_channel(error_log_channel_id)

        try:
            identifier = interaction.application_command.qualified_name
        except Exception:
            identifier = "Not Command"

        full_error = traceback.format_exception(
            type(exception), exception, exception.__traceback__
        )

        log_files = []

        exception_str = ""

        for line in full_error:
            exception_str += line

        message = f"""
            **Error Logged!**
        | Command: **/{identifier}**
        | User: {interaction.user.name}
        | Channel: {interaction.channel.name} | {interaction.channel.mention}
        | Guild: {interaction.guild.name} | Owner: {interaction.guild.owner} | Humans: {len(interaction.guild.humans)}
        | Follow Up Sent: {follow_up_sent}
        """

        if "options" in interaction.data:
            message += f"\nOptions : {interaction.data['options']}"

        with open("exception.txt", "w") as f:
            f.write(exception_str)
            f.close()

        log_files.append(nextcord.File("exception.txt"))

        if not follow_up_sent:
            not_sent_full_error = traceback.format_exception(
                type(not_sent_exception),
                not_sent_exception,
                not_sent_exception.__traceback__,
            )

            not_sent_exception_str = ""

            for line in not_sent_full_error:
                not_sent_exception_str += line

            with open("send_exception.txt", "w") as f:
                f.write(not_sent_exception_str)
                f.close()

            log_files.append(nextcord.File("send_exception.txt"))

        await channel.send(content=message, files=log_files)
        owner = await bot.fetch_user(bot_owner_id)
        mention = await channel.send(content=f"{owner.mention}")
        await mention.delete()

        try:
            os.remove("send_exception.txt")
        except Exception:
            pass
        finally:
            os.remove("exception.txt")


async def setup():
    cogs = 0
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Cogs: {filename[:-3]} is ready!")

                cogs += 1
            except Exception as e:
                print(f"Unable to load {filename[:-3]} Error: {e}")
        else:
            print(f"Passed file/folder {filename[:-3]}")

    return cogs


async def reloadSetup():
    cogs = 0
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                bot.reload_extension(f"cogs.{filename[:-3]}")
                print(f"Cogs: {filename[:-3]} is reloaded!")
                cogs += 1
            except Exception as e:
                print(f"Unable to reload {filename[:-3]} Error: {e}")
        else:
            print(f"Passed file/folder {filename[:-3]}")

    return cogs


@bot.command()
async def reloadcogs(ctx):
    if ctx.author.id == bot_owner_id:
        newcogs = await setup()
        reloadedcogs = await reloadSetup()
        await ctx.send(
            embed=Embeds.message(
                title="🤖 | System",
                message=f"Reloaded {reloadedcogs} cogs, loaded {newcogs} new cogs.",
                message_type="info",
            )
        )
    else:
        await ctx.send(
            embed=Embeds.message(
                title="🤖 | System", message=f"BRO TRIED LMAO", message_type="error"
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
        Para = "========= Guilds ========="
        for guild in bot.guilds:
            Para = Para + f"\nGuild: {guild.name} | Member: {guild.member_count}"

        await interaction.response.send_message(Para, ephemeral=True)
    else:
        await interaction.response.send_message(
            "You have no permission haha!", ephemeral=True
        )


asyncio.run(setup())
bot.run(TOKEN)
