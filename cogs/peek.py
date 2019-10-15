#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json
import os
import requests_async as requests
import re

pattern = '^https\:\/\/raider\.io\/mythic-plus-runs\/season-bfa-3\/([0-9]+)\-.*$'

class Peek(commands.Cog, name='Peek'):
	def __init__(self, client, throttler):
		self.client = client
		self.throttler = throttler
		print('Peek is available.')

	@commands.command()
	async def last(self, ctx, name):
		async with self.throttler:
			res = await requests.get(f"https://raider.io/api/v1/characters/profile?region=eu&realm=zuljin&name={name}&fields=mythic_plus_recent_runs")
			basic_data = res.json()
			
			if 'status_code' not in basic_data:

				ids = [re.search(pattern, x['url']).group(1) for x in basic_data['mythic_plus_recent_runs']]
				url = f"https://raider.io/api/mythic-plus/runs/season-bfa-3/{ids[0]}"

				res = await requests.get(url)
				detailed_data = res.json()
				
				embed = discord.Embed(
					title = f"{detailed_data['keystoneRun']['dungeon']['name']} +{detailed_data['keystoneRun']['mythic_level']}",
					description = f"por {name.title()}",
					colour = discord.Colour.blue()
				)
				embed.set_footer(text='Patrocinado por EL GRAN FAIRENSE')
				embed.set_thumbnail(url=f"{basic_data['thumbnail_url']}")

				for person in detailed_data['keystoneRun']['roster']:
					embed.add_field(name=person['character']['name'], value=f"{round(person['ranks']['score'])} score")

				await ctx.send(embed=embed)

			else:
				await ctx.send("API caida o jugador no encontrado")