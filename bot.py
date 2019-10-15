#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bs4

from asyncio_throttle import Throttler
import discord
from discord.ext import commands, tasks

from cogs.peek import Peek
from cogs.stalk import Stalk
from cogs.follow import Follow

import json


with open('config.json') as json_data_file:
    data = json.load(json_data_file)

TOKEN = data['discord']['token']

guild_id = data['discord']['guild_id']
channel_id = data['discord']['channel_id']

client = commands.Bot(command_prefix = "!")
throttler = Throttler(rate_limit=100, period=60)

@client.event
async def on_ready():
	print("Bot ready!")

@client.command()
async def ping(ctx):
	await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

	#channel = discord.utils.get(discord.utils.get(client.guilds, id=guild_id).text_channels, id=channel_id)
	#await channel.send('Hello!')

client.add_cog(Peek(client, throttler))
client.add_cog(Stalk(client, throttler, guild_id, channel_id))
client.add_cog(Follow(client, throttler))
client.run(TOKEN)