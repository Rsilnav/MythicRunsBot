#!/usr/bin/env python
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json
import os
import requests_async as requests
import re

pattern = '^https\:\/\/raider\.io\/mythic-plus-runs\/season-bfa-3\/([0-9]+)\-.*$'

class Follow(commands.Cog, name='Peek'):
	def __init__(self, client, throttler):
		self.client = client
		self.throttler = throttler
		print('Follow is available.')

	@commands.command()
	async def follow(self, ctx, name):
		name = name.title()

		with open('players.json', 'r', encoding='utf-8') as f:
			player_list = json.load(f)

		if name not in player_list:
			if len(player_list) >= 10:
				await ctx.send("Maximo numero alcanzado, contacta con EL GRAN FAIRENSE")
			else:

				async with self.throttler:
					res = await requests.get(f"https://raider.io/api/v1/characters/profile?region=eu&realm=zuljin&name={name}&fields=mythic_plus_recent_runs")
				basic_data = res.json()

				run_ids = [int(re.search(pattern, x['url']).group(1)) for x in basic_data['mythic_plus_recent_runs']]
				player_list[name] = max(run_ids)

				with open('players.json', 'w', encoding='utf-8') as f:
					json.dump(player_list, f, indent = 4)

				await ctx.send(f"Jugador '{name}' agregado correctamente")
		else:
			await ctx.send(f"Jugador '{name}' ya trackeado.")

	@commands.command()
	async def unfollow(self, ctx, name):
		name = name.title()

		with open('players.json', 'r', encoding='utf-8') as f:
			player_list = json.load(f)

		player_list.pop(name)

		with open('players.json', 'w', encoding='utf-8') as f:
			json.dump(player_list, f, indent = 4)

		await ctx.send(f"Jugador '{name}' dejara de ser trackeado.")

	@commands.command()
	async def list(self, ctx):
		with open('players.json', 'r', encoding='utf-8') as f:
			player_list = json.load(f)

		player_names = [player.title() for player in player_list]
		embed = discord.Embed(
			title = f"Personajes siendo trackeados ({len(player_names)}/10)",
			description = "\n" + '\n'.join(player_names),
			colour = discord.Colour.blue()
		)
		embed.set_footer(text='Patrocinado por EL GRAN FAIRENSE')

		await ctx.send(embed=embed)

