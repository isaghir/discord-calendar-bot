# bot.py

import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
import database

#loading your enivornement with your tokens (should be kept in a separate file .env as you dont want anyone to access tokens)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')  # bot recognises "!" as a command. "!" initialises bot

#using concurrent programming hence the use of @, async, and wait. All commands can processes dynamically.

#function to show when the bot is connected to the discord server
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#function to welcome new joiners

# A command that returns a quote from brooklyn 99 if "!99" is sent in the chat
#when the user invokes the !help command, the bot will present the description.
@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

# a command that mimicks rolling a dice. Converts the command arguments to integers
@bot.command(name='roll_dice', help='Simulates rolling dice.')
@commands.has_role('admin') # This would only allow those with admin roles to use a command.
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


bot.run(TOKEN)