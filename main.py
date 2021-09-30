import os
import discord
from dotenv import load_dotenv
from command_handler import CommandHandler


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()


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
