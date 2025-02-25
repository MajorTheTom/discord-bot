# Chess Reward Bot for Discord (Using Lichess, Chess.com, and UnbelievaBoat)

import discord
import requests
import asyncio
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
UNBELIEVABOAT_API_TOKEN = os.getenv('UNBELIEVABOAT_API_TOKEN')

# Lichess and Chess.com API URLs
LICHESS_API_URL = 'https://lichess.org/api/user/'
CHESS_COM_API_URL = 'https://api.chess.com/pub/player/'

# Bot Initialization
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to award SQR using UnbelievaBoat API
def award_sqr(user_id, amount):
    url = f'https://unbelievaboat.com/api/v1/guilds/{GUILD_ID}/users/{user_id}'
    headers = {'Authorization': f'Bearer {UNBELIEVABOAT_API_TOKEN}', 'Content-Type': 'application/json'}
    data = {'cash': amount}
    response = requests.patch(url, json=data, headers=headers)
    return response.status_code == 200

# Check Chess Results
async def check_results(username, platform, user_id):
    try:
        if platform.lower() == 'lichess':
            response = requests.get(LICHESS_API_URL + username)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', '')
        else:
            response = requests.get(CHESS_COM_API_URL + username + '/games/archives')
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', '')

        # Award SQR based on result
        if 'win' in status:
            award_sqr(user_id, 100)
            return 'Victory! +100 SQR'
        elif 'draw' in status:
            award_sqr(user_id, 50)
            return 'Draw! +50 SQR'
        elif 'loss' in status:
            award_sqr(user_id, 20)
            return 'Defeat! +20 SQR'

    except Exception as e:
        return f'Error occurred: {str(e)}'

    return 'No recent games found'

# Command to manually trigger result check
@bot.command(name='checkgame')
async def checkgame(ctx, username: str, platform: str = 'lichess'):
    user_id = ctx.author.id
    result = await check_results(username, platform, user_id)
    await ctx.send(f'{ctx.author.mention}, {result}')

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Run Bot - Updated to use await bot.start(DISCORD_TOKEN) to avoid event loop issues
async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e) == 'Event loop is closed':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
