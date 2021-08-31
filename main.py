import discord
import redis
import os
import json

redis_server = redis.Redis() # Create access to Redis

client = discord.Client()

AUTH_TOKEN = str(redis_server.get('AUTH_TOKEN').decode('utf-8'))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    # user = message.member.user

    author=message.author
    guild=message.guild

    if author == client.user:
        return

    ## create file if doesn't exist, and get discord channel data
    fname = str(guild.id) + '.json'
    data = {}
    try:
      with open(fname) as json_file:
        data = json.load(json_file)
    except OSError:
      print ("Adding Discord Channel" + guild.name + ":" + fname)
      with open(fname, 'w') as f:
        json.dump(data, f)

    if message.content.startswith('!point'):
        aid = str(author.id)
        if aid not in data.keys():
          data[aid] = {}
          data[aid]['points'] = 0

        data[aid]['points'] += 1
        points = data[aid]['points']
        with open(fname, 'w') as f:
          json.dump(data, f)
        await message.channel.send(points_print(author.id, points))

    if message.content.startswith('!loser'):
      aid = str(author.id)
      if aid in data.keys():
        if (data[aid]['points'] > 0):
          data[aid]['points']-=1
        with open(fname, 'w') as f:
          json.dump(data, f)
        await message.channel.send(points_print(author.id, data[aid]['points']))

      else:
        await message.channel.send('<@!{}> has never even made a point!'.format(author.id))

    if message.content.startswith('!reset'):
      aid = str(author.id)
      if aid in data.keys():
        data.pop(aid)
        with open(fname, 'w') as f:
          json.dump(data, f)
        await message.channel.send('<@!{}> has reset their score'.format(author.id))

    if message.content.startswith('!scoreboard'):
      string = ''
      for aid in data.keys():
        member = await guild.fetch_member(int(aid))
        string += '{}: {}'.format(member, data[aid]['points'])
        string += '\n'
      if string == '':
        string = 'scoreboard is empty'
      await message.channel.send(string)

    if message.content.startswith('!resetscoreboard'):
      data = {}
      with open(fname, 'w') as f:
        json.dump(data, f)
      await message.channel.send('All scores reset!')

    if message.content.startswith('!help'):
      string = ''
      string += '!point: give yourself a point\n'
      string += '!loser: remove a point of yours\n'
      string += '!reset: set your points to 0\n'
      string += '!scoreboard: displays the scores of all users\n'
      string += '!resetscoreboard: sets all user points to 0'
      await message.channel.send(string)

def points_print(aid, points):
      if points == 1:
        return '<@!{}> now has {} point'.format(aid, points)
      else:
        return '<@!{}> now has {} points'.format(aid, points)


client.run(AUTH_TOKEN)