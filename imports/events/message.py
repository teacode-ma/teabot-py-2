from setup.data.properties import *
from setup.actions.message import *
from setup.actions.common import *

def init_events_message(params):
	
	bot = params['bot']

	######################## ON MESSAGE ########################
	@bot.event
	async def on_message(message):
		try:
			if str(message.channel.type) == 'private':
				try:
					await log_member_dms(params, message)
				except Exception as ex:
					print('----- on_message(evt)/log_dms -----')
					print(ex)
					await log_exception(ex, 'on_message(evt)/log_dms', None, bot)
				return
			excludedCategories = [
				categories['system-corner']
			]
			if message.channel.category_id in excludedCategories:
				return
				
			try:
				if await prohibited_mentions(message):
					return
				# if await check_spam(message):
				# 	return
			except Exception as ex:
				print('----- on_message(evt)/everyone|spam -----')
				print(ex)
				await log_exception(ex, 'on_message(evt)/everyone|spam', None, bot)
			
			# await bot.process_commands(message)
		except Exception as ex:
			print('----- on_message(evt) -----')
			print(ex)
			await log_exception(ex, 'on_message(evt)', None, bot)

	######################## ON MESSAGE DELETE ########################
	@bot.event
	async def on_message_delete(message):
		try:
			if str(message.channel.type) == 'private':
				return
			excludedCategories = [
				categories['system-corner']
			]
			if message.channel.category_id in excludedCategories:
				return
				
			log = bot.get_channel(textChannels['log-txt'])
			msgs = []
			msg = '──────────────────────'
			msg += f'\n🗑 by {message.author.mention} in {message.channel.mention}'
			created_at = getTimeUtcPlusOne(message.created_at, "%d %B %Y - %H:%M")
			edited_at = None
			if message.edited_at:
				edited_at = getTimeUtcPlusOne(message.edited_at, "%d %B %Y - %H:%M")
			msg += f'\n📅 {created_at} ➜ {edited_at}'
			msg += f'\n__Content__\n'
			msgs.append(msg) #await log.send(msg)
			msg_content = f'{"--Sticker | Empty--" if (message.content == "") else message.content}'
			msgs.append(msg_content) #await log.send(msg_content)
			msg = get_attachments(message)
			if msg: msgs.append(msg) #await log.send(msg)
			msg = get_embeds(message)
			if msg: msgs.append(msg) #await log.send(msg)
			for msg in msgs:
				await log.send(msg)

		except Exception as ex:
			print('----- on_message_delete(evt) -----')
			print(ex)
			await log_exception(ex, 'on_message_delete(evt)', None, bot)


	######################## ON MESSAGE EDIT ########################
	@bot.event
	async def on_message_edit(before, after):
		try:
			if str(before.channel.type) == 'private':
				return
			excludedCategories = [
				categories['system-corner']
			]
			if before.channel.category_id in excludedCategories:
				return
			if (before.content.lower() == after.content.lower()):
				return
			log = bot.get_channel(textChannels['log-txt'])
			msgs = []
			msg = f'\n\nhttps://discord.com/channels/{guildId}/{after.channel.id}/{after.id}'
			msg += f'\n✏ by {before.author.mention} in {before.channel.mention}'
			created_at = getTimeUtcPlusOne(after.created_at, "%d %B %Y - %H:%M")
			edited_at = None
			if after.edited_at:
				edited_at = getTimeUtcPlusOne(after.edited_at, "%d %B %Y - %H:%M")
			msg += f'\n📅 {created_at} ➜ {edited_at}'
			msg += f'\n__Content__\n'
			msgs.append(msg) #await log.send(msg)
			msg_content = f'{"--Sticker | Empty--" if (before.content == "") else before.content}'
			msgs.append(msg_content) #await log.send(msg_content)
			msg = '\n──▼▼▼▼▼──\n'
			msgs.append(msg) #await log.send(msg)
			msg_content = f'{"--Sticker | Empty--" if (after.content == "") else after.content}'
			msgs.append(msg_content) #await log.send(msg_content)
			msg = get_attachments(before)
			if msg: msgs.append(msg) #await log.send(msg)
			msg = get_embeds(before)
			if msg: msgs.append(msg) #await log.send(msg)
			# msg += '\n──────────────────────'
			# msgs.append(msg) #await log.send(msg)
			for msg in msgs:
				await log.send(msg)
		except Exception as ex:
			print('----- on_message_edit(evt) -----')
			print(ex)
			await log_exception(ex, 'on_message_edit(evt)', None, bot)