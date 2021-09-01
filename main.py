import discord
import redis
import os
import json
from datetime import datetime

redis_server = redis.Redis() # Create access to Redis

client = discord.Client()

AUTH_TOKEN = str(redis_server.get('AUTH_TOKEN').decode('utf-8'))

# keep track of whoever requested a reset
# TODO: this will get cleared whenever this program stops running,
# which might be ok or might not, I don't know...
reset_requested = set()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
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

    if message.content == '!point':
        aid = str(author.id)
        if aid not in data.keys():
            data[aid] = {'points': 0, 'last_workout': datetime.now()}

        data[aid]['points'] += 1
        data[aid]['last_workout'] = datetime.now()

        with open(fname, 'w') as f:
            json.dump(data, f)
        await message.channel.send(points_print(author.id, data[aid]['points']))

    elif message.content == '!loser':
        aid = str(author.id)
        if aid in data.keys():
            if (data[aid]['points'] > 0):
                data[aid]['points'] -= 1
                # get dropped to bottom of people with tied points
                data[aid]['last_workout'] = datetime.max

                with open(fname, 'w') as f:
                    json.dump(data, f)
                await message.channel.send(points_print(author.id, data[aid]['points']))

            else:
                await message.channel.send('<@!{}> has no points!'.format(author.id))

        else:
            await message.channel.send('<@!{}> has never even made a point!'.format(author.id))

    elif message.content == '!reset':
        aid = str(author.id)
        if aid in data.keys():
            data[aid]['points'] = 0
            # get dropped to bottom of list
            data[aid]['last_workout'] = datetime.max

            with open(fname, 'w') as f:
                json.dump(data, f)
            await message.channel.send('<@!{}> has reset their score to 0'.format(author.id))

    elif message.content == '!quitter':
        aid = str(author.id)
        if aid in data.keys():
            data.pop(aid)

            with open(fname, 'w') as f:
                json.dump(data, f)
            await message.channel.send('<@!{}> has quit the competition, how pathetic'.format(author.id))

    elif message.content == '!scoreboard':
        # sort aids by:
        # 1. points (highest first, so use -points)
        # 2. last_workout (lowest first)
        aids = data.keys()

        if aids:
            sortable_list = [(-data[aid]['points'], data[aid]['last_workout'], aid) for aid in aids]
            sorted_list = sorted(sortable_list)

            string = ''
            for _, _, aid in sorted_list:
                member = await guild.fetch_member(int(aid))
                string += '{}: {}'.format(member, data[aid]['points'])
                string += '\n'

            await message.channel.send(string)
        else:
            string = 'scoreboard is empty'
            await message.channel.send(string)

    elif message.content == '!resetscoreboard':
        aid = str(author.id)

        if not data.keys():
            string = 'scoreboard is already empty!'
            await message.channel.send(string)

        # use system of super majority to reset
        # ex. with 6 people 4 people need to vote to reset
        # ex. with 5 people 3 people need to vote to reset
        reset_requirement = int(len(data.keys())/2)+1
        if aid in reset_requested:
            string = f'You already requested a reset. Currently {len(reset_requested)} of {reset_requirement} needed have requested the reset'
            await message.channel.send(string)
        else:
            reset_requested.add(aid)
            if len(reset_requested) >= reset_requested:
                data = {}
                reset_requested = set()
                with open(fname, 'w') as f:
                    json.dump(data, f)
                await message.channel.send('All scores reset!')
            else:
                string = f'Your vote to reset has been counted. Currently {len(reset_requested)} of {reset_requirement} needed have requested the reset'
                await message.channel.send(string)

    elif message.content == '!help':
        string = ''
        string += '!point: give yourself a point\n'
        string += '!loser: remove a point of yours\n'
        string += '!reset: set your points to 0\n'
        string += '!quitter: remove yourself from the competition\n'
        string += '!scoreboard: displays the scores of all users\n'
        string += '!resetscoreboard: vote to set all user points to 0'
        await message.channel.send(string)

def points_print(aid, points):
    if points == 1:
        return '<@!{}> now has {} point'.format(aid, points)
    else:
        return '<@!{}> now has {} points'.format(aid, points)


client.run(AUTH_TOKEN)
