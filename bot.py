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
from datetime import datetime, timedelta

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
    help="Specify meeting title, datetime in format dd/mm/yyyy HH:MM and duration in minutes e.g. !add_meeting ML Tutorial 06/03/2021 09:00 60",
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
    duration = args[-1]
    if not duration.isnumeric():
        await ctx.send_help()
        raise Exception("Duration is not numeric")
    start_time = " ".join(args[-3:-1])
    try:
        start_time = datetime.strptime(
            start_time, "%d/%m/%Y %H:%M"
        )  # convert time to datetime object
    except Exception:
        await ctx.send_help()
        raise

    end_time = start_time + timedelta(minutes=int(duration))
    # since we don't know how many spaces are in the title, join up to the last 2 elements
    title = " ".join(args[0:-3])

    user_id = user.id
    server_id = server.id
    channel_id = channel.id
    cancelled = False

    # insert meeting into database
    database.add_meeting(
        title, user_id, server_id, channel_id, start_time, end_time, cancelled
    )

    await ctx.send(f"<@{user.id}> your meeting has been added.")


@bot.command(
    name="cancel_meeting",
    help="Specify meeting title and start time in format dd/mm/yyyy HH:MM e.g. !add_meeting ML Tutorial 06/03/2021 09:00",
)
async def cancel_meeting(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel (see https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    title = " ".join(args[0:-2])
    start_time = " ".join(args[-2:])
    try:
        start_time = datetime.strptime(
            start_time, "%d/%m/%Y %H:%M"
        )  # convert time to datetime object
    except Exception:
        await ctx.send_help()
        raise

    user_id = user.id
    server_id = server.id

    rows_affected = database.cancel_meeting(title, user_id, server_id, start_time)
    if rows_affected > 0:
        msg = "Meeting cancelled."
    else:
        msg = "Meeting not found."

    await ctx.send(msg)


@bot.command(
    name="lookup_meeting_by_day",
    help="Specify the date  in format dd/mm/yyyy e.g. !lookup_meeting_by_day 21/08/2021 ",
)
async def lookup_meeting_by_day(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel (see https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments such as date
    date = " ".join(args[-1:])
    date = datetime.strptime(date, "%d/%m/%Y")  # convert date to datetime object

    user_id = user.id
    server_id = server.id

    # looking into the database
    records = database.lookup_meeting_by_day(user_id, server_id, date)
    print(records)

    if records:  # if the database lookup returned records
        message = "```"  # triple backticks = put this text in a code block
        for record in records:
            title = record[0]
            # get time and remove the seconds (last 3 characters)
            start_time = record[1].strftime("%d/%m/%Y %H:%M")
            end_time = record[2].strftime("%H:%M")
            message += f"- {title} {start_time}-{end_time}\n"  # \n = newline
        message += "```"
    else:  # if the database lookup found no records
        message = (
            f"You have no meetings scheduled for the date {date.strftime('%d/%m/%Y')}"
        )

    await ctx.send(f"<@{user.id}> {message}")


@bot.command(
    name="lookup_meeting_by_week",
    help="schedule for the next 7 days ",
)
async def lookup_meeting_by_week(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel (see https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments such as date
    date = datetime.now()  # current date
    date_after_7_days = date + timedelta(days=7)  # incrementing current date by 7 days
    # we try to run sql queries to retrieve records from current date  to the next 7 days

    user_id = user.id
    server_id = server.id
    channel_id = channel.id
    cancelled = False

    # insert meeting into database
    database.lookup_meeting_by_week(
        user_id, server_id, channel_id, date, date_after_7_days, cancelled
    )

    await ctx.send(f"<@{user.id}> your meeting schedule for the next 7 days ")


@bot.command(
    name="lookup_meeting_by_month",
    help="schedule for the next 1 month",
)
async def lookup_meeting_by_month(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel (see https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments such as date
    date = datetime.now()
    date_after_30_days = date + timedelta(days=30)

    user_id = user.id
    server_id = server.id
    channel_id = channel.id
    cancelled = False

    # insert meeting into database
    database.lookup_meeting_by_month(
        user_id, server_id, channel_id, date, date_after_30_days, cancelled
    )

    await ctx.send(f"<@{user.id}> your meeting schedule for the next 1 month")


# sends a message to the user contaning the error observed when running the bot.py file
@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send(f"Oops, something went wrong. {error}")


bot.run(TOKEN)
