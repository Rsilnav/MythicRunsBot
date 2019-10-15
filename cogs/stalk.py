#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands, tasks
import json
import os
import requests_async as requests
import re
import datetime

pattern = '^https\:\/\/raider\.io\/mythic-plus-runs\/season-bfa-3\/([0-9]+)\-.*$'

class Stalk(commands.Cog, name='Stalk'):
	def __init__(self, client, throttler, guild_id, channel_id):
		self.client = client
		self.throttler = throttler
		self.guild_id = guild_id
		self.channel_id = channel_id
		print('Stalk is available.')

	@commands.Cog.listener()
	async def on_ready(self):
		self.channel = discord.utils.get(discord.utils.get(self.client.guilds, id=self.guild_id).text_channels, id=self.channel_id)
		self.stalker.start()

	def cog_unload(self):
		self.stalker.cancel()

	@tasks.loop(seconds=10.0)
	async def stalker(self):

		with open('players.json', 'r', encoding='utf-8') as f:
			player_list = json.load(f)

		print(f'Stalked {len(player_list)} people at {datetime.datetime.now()}')

		dungeon_runs = set()
		names = {}
		thumbnail = {}
		changed = False
		
		for player_name in player_list:
			last_run = player_list[player_name]

			async with self.throttler:
				res = await requests.get(f"https://raider.io/api/v1/characters/profile?region=eu&realm=zuljin&name={player_name}&fields=mythic_plus_recent_runs")
			basic_data = res.json()

			run_ids = [int(re.search(pattern, x['url']).group(1)) for x in basic_data['mythic_plus_recent_runs']]
			new_ids = [new for new in run_ids if new > last_run]

			if len(new_ids) > 0:
				changed = True
				last_run_now = max(new_ids)
				player_list[player_name] = last_run_now

				for i in new_ids:
					names[i] = player_name
					thumbnail[i] = basic_data['thumbnail_url']
				dungeon_runs.update(new_ids)

		if changed:
			with open('players.json', 'w', encoding='utf-8') as f:
				json.dump(player_list, f, indent = 4)

		for run in sorted(list(dungeon_runs)):
			print(f"New run by {names[run]}")
			url = f"https://raider.io/api/mythic-plus/runs/season-bfa-3/{run}"

			async with self.throttler:
				res = await requests.get(url)
			detailed_data = res.json()
			
			embed = discord.Embed(
				title = f"{detailed_data['keystoneRun']['dungeon']['name']} +{detailed_data['keystoneRun']['mythic_level']}",
				description = f"por {names[run]}",
				colour = discord.Colour.blue()
			)
			embed.set_footer(text='Patrocinado por EL GRAN FAIRENSE')
			embed.set_thumbnail(url=f"{thumbnail[run]}")

			for person in detailed_data['keystoneRun']['roster']:
				embed.add_field(name=person['character']['name'], value=f"{round(person['ranks']['score'])} score")

			await self.channel.send(embed=embed)