import os
import discord
import redis
from command_handler import CommandHandler

# https://python.plainenglish.io/hosting-a-python-discord-bot-using-aws-redis-7a320b2702a0
redis_server = redis.Redis() # Create access to Redis
client = discord.Client()
if redis_server.get("DISCORD_TOKEN") is None:
    raise Exception("redis token DISCORD_TOKEN not set")
TOKEN = str(redis_server.get("DISCORD_TOKEN").decode("utf-8"))


@client.event
async def on_ready():
    """Handle all startup tasks"""

    if len(client.guilds) == 0:
        print(f"{client.user} is not connected to any guilds")
    else:
        print(f"{client.user} is connected to the following guild{'s' if len(client.guilds) != 1 else ''}:")
        for guild in client.guilds:
            print(f"  {guild.name} (id: {guild.id})")


@client.event
async def on_message(message):
    """Catch all for messages"""

    # don't react to your own messages
    if message.author == client.user:
        return

    response = CommandHandler.handle_command(message)
    if response is not None:
        await message.channel.send(response)


client.run(TOKEN)
