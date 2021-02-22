# bot.py
# This file deals with the interections with the discord api only.
# This file uses concurrent programming hence the use of @, async, and wait. All commands can processes dynamically.
# We will only run this file

# Importing relevant libraries,modules and files
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
import database  # importing the database.py file
from datetime import datetime

# Create connection to RDS database and ensure the database and tables exist
print("Initialising the database.")
database.init_db()  # function in database.py file

# Loading your .env with your tokens
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

# bot recognises "!" as a command. "!" initialises bot
bot = commands.Bot(command_prefix="!")
# Shows when the bot is connected to the discord server
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


# Add meeting command
@bot.command(
    name="add_meeting",
    help="Specify meeting title and datetime in format dd/mm/yyyy HH:MM. e.g. !add_meeting ML Tutorial 06/03/2021 09:00",
)
async def add_meeting(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel (see https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments which are delimited by spaces in the user's command message
    time = " ".join(args[-2:])
    time = datetime.strptime(time, "%d/%m/%Y %H:%M")  # convert time to datetime object

    # since we don't know how many spaces are in the title, join up to the last 2 elements
    title = " ".join(args[0:-2])

    user_id = user.id
    server_id = server.id
    channel_id = channel.id
    cancelled = False

    # insert meeting into database
    database.add_meeting(title, user_id, server_id, channel_id, time, cancelled)

    await ctx.send(f"<@{user.id}> your meeting has been added.")


# sends a message to the user if they do not provide the right arguments
@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send(f"Oops, something went wrong. {error}")


bot.run(TOKEN)
