# bot.py

import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
import database

# loading your enivornement with your tokens (should be kept in a separate file .env as you dont want anyone to access tokens)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

bot = commands.Bot(
    command_prefix="!"
)  # bot recognises "!" as a command. "!" initialises bot

meetings = []

# using concurrent programming hence the use of @, async, and wait. All commands can processes dynamically.

# function to show when the bot is connected to the discord server


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.command(
    name="add_meeting",
    help="Specify meeting title and datetime in format dd/mm/yyyy HH:MM. e.g. !add_meeting ML Tutorial 06/03/2021 09:00",
)
async def add_meeting(ctx, *args):
    # send help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel (see https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments which are delimited by spaces in the user's command message
    time = args[-1]  # time should always be the last argument
    date = args[-2]  # date should always be 2nd to last
    title = " ".join(
        args[0:-2]
    )  # since we don't know how many spaces in the title, join up to the last 2 elements

    # insert meeting into list
    meetings.append(
        {
            "time": time,
            "date": date,
            "title": title,
            "user_id": user.id,
            "server_id": server.id,
            "channel_id": channel.id,
        }
    )

    print(meetings)
    await ctx.send(f"<@{user.id}> your meeting has been added.")


@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send(f"Oops, something went wrong. {error}")


bot.run(TOKEN)
