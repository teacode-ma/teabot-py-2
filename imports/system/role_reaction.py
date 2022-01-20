from database.reactions import * 
from setup.properties import *
from setup.actions import *

def init_bot_reaction(params):

	bot = params['bot']
	discord = params['discord']
	slash = params['slash']
	get = params['get']

	@bot.event
	async def on_raw_reaction_add(payload):
		try:
			guild = bot.get_guild(guildId)
			member = payload.member

			log = bot.get_channel(textChannels['log-channel'])
			url = f'https://discord.com/channels/{guildId}/{payload.channel_id}/{payload.message_id}'
			await log.send(f'{url}\n{member.mention} Added {payload.emoji}')

			if member.bot == True:
				return
			roleName = None
			if str(payload.channel_id) in reactions:
				if str(payload.message_id) in reactions[str(payload.channel_id)]:
					if str(payload.emoji) in reactions[str(payload.channel_id)][str(payload.message_id)]:
						roleName = reactions[str(payload.channel_id)][str(payload.message_id)][str(payload.emoji)]
			if roleName:
				role = get(guild.roles, name = roleName)
				await member.add_roles(role)
				await log.send(f'{member.mention} got a role {role.mention}')
		except Exception as ex:
			print('---------- on_raw_reaction_add(evt) --------')
			print(ex)
			await log_exception(ex, 'on_raw_reaction_add(evt)', None, bot)


	@bot.event
	async def on_raw_reaction_remove(payload):
		try:
			guild = bot.get_guild(guildId)
			member = await guild.fetch_member(payload.user_id)

			log = bot.get_channel(textChannels['log-channel'])
			url = f'https://discord.com/channels/{guildId}/{payload.channel_id}/{payload.message_id}'
			await log.send(f'{url}\n{member.mention} Removed {payload.emoji}')

			if member.bot == True:
				return
			roleName = None
			if str(payload.channel_id) in reactions:
				if str(payload.message_id) in reactions[str(payload.channel_id)]:
					if str(payload.emoji) in reactions[str(payload.channel_id)][str(payload.message_id)]:
						roleName = reactions[str(payload.channel_id)][str(payload.message_id)][str(payload.emoji)]
			if roleName:
				role = get(guild.roles, name = roleName)
				await member.remove_roles(role)
				await log.send(f'{member.mention} lost a role {role.mention}')
		except Exception as ex:
			print('---------- on_raw_reaction_remove(evt) --------')
			print(ex)
			await log_exception(ex, 'on_raw_reaction_remove(evt)', None, bot)


	@slash.slash(name = "rr", description=',', guild_ids = [guildId],
		permissions={ guildId: slash_permissions({'founders'}, {'members', 'everyone'}) })
	async def bot_react(ctx, msg_id=None, emojis=None, remove:int=0, member: discord.Member = None):
		try:

			if not is_founders(ctx):
				await ctx.send('❌ Missing Permissions')
				return
	
			if msg_id:
				if emojis:
					await ctx.send('Bot Reacting ....', hidden=True)
					msg = await ctx.channel.fetch_message(msg_id)
					emojis = emojis.split(',')
					for e in emojis:
						if remove: 
							if member: await msg.remove_reaction(e, member)
							else: await msg.clear_reaction(e)
						else: await msg.add_reaction(e)
					return
				else:
					await ctx.send('Reactions are setting up ....', hidden=True)
					if str(ctx.channel.id) in reactions and str(msg_id) in reactions[str(ctx.channel.id)]:
						msg = await ctx.channel.fetch_message(msg_id)
						for e in reactions[str(ctx.channel.id)][msg_id]:
							await msg.add_reaction(e)
						await ctx.send('Done Reacting.', hidden=True)
					else: await ctx.send('Could not find channel/message.', hidden=True)
					return

			await ctx.send('Updating members roles ....', hidden=True)
			guild = bot.get_guild(guildId)
			roles_assigned = 0
			_msg = ''
			for channel_id in reactions:
				channel = bot.get_channel(int(channel_id))
				for msg_id in reactions[str(channel_id)]:
					try:
						msg = await channel.fetch_message(int(msg_id))
						for r in msg.reactions:
							roleName = reactions[str(channel_id)][str(msg_id)][str(r.emoji)]
							role = get(guild.roles, name = roleName)
							async for u in r.users():
								try:
									if u.id != users['teabot']:
										member = await guild.fetch_member(u.id)
										if role not in member.roles:
											await member.add_roles(role)
											_msg += f'{member.mention} got {role.mention}\n'
											roles_assigned += 1
								except Exception as ex:
									print('---------- /bot_react()/add role user --------')
									print(ex)
									# await msg.remove_reaction(r.emoji, u)
									pass
					except Exception as ex:
						print('---------- /bot_react()/msg reactions --------')
						print(ex)
						pass
			await ctx.send(f'Done Updating members roles / {roles_assigned} updated.\n{_msg}', hidden=True)
		except Exception as ex:
			print('---------- /bot_react() --------')
			print(ex)
			await log_exception(ex, '/bot_react', ctx)