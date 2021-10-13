import discord
import redis
from command_handler import CommandHandler

# https://python.plainenglish.io/hosting-a-python-discord-bot-using-aws-redis-7a320b2702a0
redis_server = redis.Redis() # Create access to Redis
intents = discord.Intents(messages=True, guilds=True, members=True)
client = discord.Client(intents=intents)
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
        guild: discord.Guild
        for guild in client.guilds:
            print(f"  {guild.name} (id: {guild.id})")
            await guild.query_members(query="")
    print("\nReady!")



@client.event
async def on_message(message: discord.Message):
    """Catch all for messages"""

    # don't react to bots
    if message.author.bot:
        return

    response = CommandHandler.handle_command(message)
    if response is not None:
        await message.channel.send(response)


client.run(TOKEN)