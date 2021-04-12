# bot.py
# This file deals with the interactions with the discord API only.
# This file uses concurrent programming hence the use of @, async, and wait. All commands can process dynamically.

# Importing relevant libraries,modules and files
import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks
import database  # importing the database.py file as we will be using the functions from it
from datetime import datetime, timedelta

# Create connection to RDS database and ensuring the database and tables exist
print("Initialising the database.")
# function in database.py file to create a connection to postgres and creates an meetings table ifit does not already exist.
database.init_db()

# Loading the discord token from the  .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# enable collection of user data so the bot.get_user function works
intents = discord.Intents.default()
intents.members = True
# bot recognises "!" as a command. "!" initialises bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Add meeting command
@bot.command(
    name="add_meeting",
    help="Specify meeting title, datetime in format dd/mm/yyyy HH:MM and duration in minutes e.g. !add_meeting ML Tutorial 06/03/2021 09:00 60",
)
async def add_meeting(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel using ctx
    # (https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context)
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments which are delimited by spaces in the user's command message
    duration = args[-1]
    if not duration.isnumeric():
        await ctx.send_help()
        raise Exception(
            "Duration is not numeric"
        )  # sending an error message if the duration input is  incorrect
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

    # insert meeting into database by calling the add_meeting function from database.py
    database.add_meeting(
        title, user_id, server_id, channel_id, start_time, end_time, cancelled
    )

    await ctx.send(f"<@{user.id}> your meeting has been added.")


# Cancel Meetings command
@bot.command(
    name="cancel_meeting",
    help="Specify meeting title and start time in format dd/mm/yyyy HH:MM e.g. !add_meeting ML Tutorial 06/03/2021 09:00",
)
async def cancel_meeting(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel
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

    # lookup the meetings in the RDS database using the cancel_meeting function from database.py
    rows_affected = database.cancel_meeting(title, user_id, server_id, start_time)
    if rows_affected > 0:  # If >0, meeting(s) have been cancelled.
        # cancel_meeting returns the number of rows it has updated and set to cancelled in the meetings table.
        msg = "Meeting cancelled."
    else:
        msg = "Meeting not found."

    await ctx.send(msg)


# Look up meetings by day command
@bot.command(
    name="lookup_meeting_by_day",
    help="Specify the date in format dd/mm/yyyy e.g. !lookup_meeting_by_day 21/08/2021 ",
)
async def lookup_meeting_by_day(ctx, *args):
    # send the help message if user does not specify arguments
    if len(args) == 0:
        await ctx.send_help()

    # gather information about the user, server and channel
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments such as date
    date = " ".join(args[-1:])
    date = datetime.strptime(date, "%d/%m/%Y")  # convert date to datetime object
    date_after_1_day = date + timedelta(days=1)  # find the date tomorrow

    user_id = user.id
    server_id = server.id

    print(
        f"Looking up meetings on date {date} for user {user_id} from server {server_id}"
    )

    # looking into the database using the lookup_meeting_by_date_window function from database.py.
    # We set end_date =  date_after_1_day for this function.
    records = database.lookup_meeting_by_date_window(
        user_id, server_id, date, date_after_1_day
    )
    print(f"Found {len(records)} meetings.")

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


# Lookup meetings by week
@bot.command(
    name="lookup_meeting_by_week",
    help="Shows your schedule for the next 7 days from now.",
)
async def lookup_meeting_by_week(ctx, *args):
    # gather information about the user, server and channel
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments such as date
    date = datetime.now()  # current date
    date_after_7_days = date + timedelta(days=7)  # incrementing current date by 7 days

    user_id = user.id
    server_id = server.id
    channel_id = channel.id

    print(
        f"Looking up meetings in the next week for user {user_id} from server {server_id}"
    )

    # looking into the database using the lookup_meeting_by_date_window function from database.py.
    # We set end_date = date_after_7_day for this function.
    records = database.lookup_meeting_by_date_window(
        user_id, server_id, date, date_after_7_days
    )
    print(f"Found {len(records)} meetings.")

    if records:  # if the database lookup returned records
        message = "Your meetings for the next week:\n```"  # triple backticks = put this text in a code block
        for record in records:
            title = record[0]
            # get time and remove the seconds (last 3 characters)
            start_time = record[1].strftime("%d/%m/%Y %H:%M")
            end_time = record[2].strftime("%H:%M")
            message += f"- {title} {start_time}-{end_time}\n"  # \n = newline
        message += "```"
    else:  # if the database lookup found no records
        message = f"You have no meetings scheduled for the next 7 days"

    await ctx.send(f"<@{user.id}> {message}")


# Lookup meetings by month
@bot.command(
    name="lookup_meeting_by_month",
    help="Shows your schedule for the next 1 month from now.",
)
async def lookup_meeting_by_month(ctx, *args):
    # gather information about the user, server and channel
    user = ctx.author
    server = ctx.guild
    channel = ctx.channel

    # gather command arguments such as date
    date = datetime.now()  # current date
    date_after_30_days = date + timedelta(
        days=30
    )  # incrementing current date by 30 days

    user_id = user.id
    server_id = server.id
    channel_id = channel.id

    print(
        f"Looking up meetings in the next month for user {user_id} from server {server_id}"
    )

    # looking into the database using the lookup_meeting_by_date_window function from database.py.
    # We set end_date = date_after_30_day for this function.
    records = database.lookup_meeting_by_date_window(
        user_id, server_id, date, date_after_30_days
    )
    print(f"Found {len(records)} meetings.")

    if records:  # if the database lookup returned records
        message = "Your meetings for the next month:\n```"  # triple backticks = put this text in a code block
        for record in records:
            title = record[0]
            # get time and remove the seconds (last 3 characters)
            start_time = record[1].strftime("%d/%m/%Y %H:%M")
            end_time = record[2].strftime("%H:%M")
            message += f"- {title} {start_time}-{end_time}\n"  # \n = newline
        message += "```"
    else:  # if the database lookup found no records
        message = f"You have no meetings scheduled for the next 30 days"

    await ctx.send(f"<@{user.id}> {message}")


# NOTIFICATIONS: every minute, check for meetings starting in the next minute and DM the creator of the meeting
@tasks.loop(
    minutes=1.0
)  # The tasks decorator allows the function to be run in the background, in our case every 1 minute for all users.
async def notify_meeting_start():
    date = datetime.now()
    date_after_1_minute = date + timedelta(
        minutes=1
    )  # calculate the time after 1 minute

    records = database.lookup_all_meetings_by_date_window(date, date_after_1_minute)

    if records:
        print(
            f"Notifying meeting start for {len(records)} meetings."
        )  # use the lookup_all_meetings_by_date_window from database.py (here we query for all users)
        for record in records:
            title = record[0]
            start_time = record[1].strftime("%d/%m/%Y %H:%M")
            end_time = record[2].strftime("%H:%M")
            user_id = record[3]
            message = "Your meeting is starting in the next minute:\n"
            message += f"```{title} {start_time}-{end_time}```"
            user = bot.get_user(int(user_id))
            await user.send(message)


# This code block executes when the bot first connects to Discord
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")
    notify_meeting_start.start()  # Starts the background task loop


# Sends information back to the channel when errors occur
@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.send(f"Oops, something went wrong. {error}")


bot.run(TOKEN)
