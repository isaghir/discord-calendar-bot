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

bot = commands.Bot(
    command_prefix="!"
)  # bot recognises "!" as a command. "!" initialises bot

meetings = []

# Shows when the bot is connected to the discord server
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


# add meeting command
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
    #time = args[-1]  # time should always be the last argument
    #date = args[-2]  # date should always be 2nd to last
    time=" ".join(
        args[-2:]
    )
    print(type(time))
    print(time)
    time = datetime.strptime(time,"%d/%m/%Y %H:%M")
    print(type(time))
    print(time)
   

    title = " ".join(
        args[0:-2]
    )  # since we don't know how many spaces in the title, join up to the last 2 elements
    user_id=user.id
    server_id= server.id
    channel_id=channel.id
    cancelled=1 #will remove it after the flow is clear
    
    # insert meeting into database
    add_meeting(title, user_id, server_id, channel_id, time, cancelled)
   

    print(meetings)
    await ctx.send(f"<@{user.id}> your meeting has been added.")


@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send(f"Oops, something went wrong. {error}")


bot.run(TOKEN)
