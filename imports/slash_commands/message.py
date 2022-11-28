from setup.data.properties import *
from setup.actions.common import *
from setup.actions.message import *
from setup.data.params import *

def init_slash_commands_message(params):

	bot = params['bot']
	discord = params['discord']
	commands = params['commands']

	keys = [ rule['key'] for rule in rules ]
	######### RULES ########
	@bot.slash_command(name = "tag")
	async def tag_rules(interaction, query=commands.Param(choices=keys)):
		"""
		Reminde with a rule
		Parameters
		----------
		query: Choose a predefined rule by key
		"""
		try:
			if query not in keys:
				await interaction.send('Issue with the input (choose one of the provided options)', ephemeral=True)
				return
			rule = next(item for item in rules if item["key"] == query)
			# rule_index = rules.index(rule) + 1
			msg = f'**{query} :**\n{rule["value"]}'
			await interaction.send(msg)
		except Exception as ex:
			print('----- /tag_rules() -----')
			print(ex)
			await log_exception(ex, '/tag_rules', interaction)

	@bot.slash_command(name = "poll")
	async def poll(interaction, header, options, emojis, channel = None):
		"""
		Make a poll
		Parameters
		----------
		header: Header message (part I)
		options: Options of the poll separated by , or space (part II)
		emojis: emojis for the users
		"""
		try:
			await interaction.send('Creating the Poll...', ephemeral=True)
			if channel == None: channel = interaction.channel
			msg = f'{header}\n'
			emojis = split_str(emojis)
			options = split_str(options)
			index = 0
			for o in options:
				msg += f'\n{emojis[index]} - {o}'
				index += 1
			msg += '\n\n─────────────────────────'
			print(msg)
			msg = await channel.send(msg)
			for e in emojis:
				await msg.add_reaction(e)
		except Exception as ex:
			print('----- /poll() -----')
			print(ex)
			await log_exception(ex, '/poll', interaction)

	######################## PURGE ########################
	@bot.slash_command(name = "purge")
	async def purge(interaction, limit: int=None):
		"""
		Clear all messages
		Parameters
		----------
		limit: Optional for specific channels / limit <= 500
		"""
		try:
			channelsToClear = [
				textChannels['voice-chat'],
				textChannels['help-chat']
			]
			if not limit and interaction.channel.id not in channelsToClear:
				await interaction.send('❌ Wrong Target Channel', ephemeral=True)
				return

			if limit:
				if limit > 500:
					await interaction.send('You cannot delete more than 500 messages', ephemeral=True)
					return
				else:
					await interaction.send('Clearing messages ...', ephemeral=True)
					deletedMsgs = await interaction.channel.purge(limit = limit, check = isNotPinned, bulk = True)
					await interaction.send(f'{len(deletedMsgs)} message(s) cleared', ephemeral=True)
					count = len(deletedMsgs)
					deletedMsgs.reverse()
					if count:
						await logPurgedMessages(params, interaction, count, deletedMsgs)
				return

			MAX_TO_DELETE = 500
			await interaction.send('Clearing everything ...', ephemeral=True)
			#await deleteMsg(params, purgedMsgs, interaction, MAX_TO_DELETE)
			deletedMsgs = await deleteMsg(params, interaction, MAX_TO_DELETE)
			await interaction.send(f'{len(deletedMsgs)} message(s) cleared', ephemeral=True)
			count = len(deletedMsgs)
			# deletedMsgs.reverse()
			deletedMsgs = sorted(deletedMsgs, key=lambda msg: msg.created_at)
			if count:
				await logPurgedMessages(params, interaction, count, deletedMsgs)
			
		except Exception as ex:
			print('----- /purge() -----')
			print(ex)
			await log_exception(ex, '/purge', interaction)

	####################### MAKE A WEBHOOK #######################
	@bot.slash_command(name = "tc_make-webhook")
	async def make_webhook(interaction, member: discord.Member, channel: discord.TextChannel, msg, name=None):
		"""
		Make a webhook - \\n \\t /$
		Parameters
		----------
		member: Server existing member
		msg: Message to send by the webhook - \\n \\t /$
		channel: Channel where to send the msg
		name: Webhook name
		"""
		try:
			if name == None:
				name = member.display_name
			msg = replace_str(msg, {"\\n": "\n", "\\t": "	", "/$": " "})
			webhook = await channel.create_webhook(name=name)
			await webhook.send(f'{msg}', username=member.display_name, avatar_url=member.display_avatar.url)
			await webhook.delete()
			await interaction.send('✅ Webhook made', ephemeral=True)
		except Exception as ex:
			await interaction.send('❌ Webhook not made', ephemeral=True)
			print('----- /make_webhook() -----')
			print(ex)
			await log_exception(ex, '/make_webhook', interaction)
	
	######################## REPLY TO MSG ########################
	@bot.slash_command(name = "tc_edit-msg-channel")
	async def edit_msg_channel(interaction, content, msg_id, channel: discord.TextChannel, pin: int=0):
		"""
		Edit message channel - \\n \\t /$
		Parameters
		----------
		content: New message content - \\n \\t /$
		msg_id: Message ID to edit
		channel: Channel where to fetch the message by msg_id
		pin: Add to pinned channel messages
		"""
		try:
			msg = await channel.fetch_message(int(msg_id))
			content = replace_str(content, {"\\n": "\n", "\\t": "	", "/$": " "})
			await msg.edit(content=content)
			if pin:
				await msg.pin()
			await interaction.send('Edit done', ephemeral=True)
		except Exception as ex:
			print('----- /edit_msg_channel() -----')
			print(ex)
			await log_exception(ex, '/edit_msg_channel', interaction)


	######################## REPLY TO MSG ########################
	@bot.slash_command(name = "tc_reply-channel")
	async def reply_channel(interaction, reply, msg_id, channel: discord.TextChannel):
		"""
		Reply to msg channel - \\n \\t /$
		Parameters
		----------
		reply: Message content - \\n \\t /$
		msg_id: Message ID to reply to
		channel: Channel where to fetch the message by msg_id
		"""
		try:
			msg = await channel.fetch_message(int(msg_id))
			reply = replace_str(reply, {"\\n": "\n", "\\t": "	", "/$": " "})
			await msg.reply(reply)
			await interaction.send('Reply sent', ephemeral=True)
		except Exception as ex:
			print('----- /reply_channel() -----')
			print(ex)
			await log_exception(ex, '/reply_channel', interaction)


	######################## SEND MSG TO CHANNEL ########################
	@bot.slash_command(name = "tc_msg-channel")
	async def msg_channel(interaction, msg, channel: discord.TextChannel, pin: int=0):
		"""
		Send msg to channel - \\n \\t /$
		Parameters
		----------
		msg: Message content - \\n \\t /$
		channel: Channel where to send the message
		pin: Add to pinned channel messages
		"""
		try:
			msg = replace_str(msg, {"\\n": "\n", "\\t": "	", "/$": " "})
			msg = await channel.send(msg)
			if pin:
				await msg.pin()
			await interaction.send('Msg sent', ephemeral=True)
		
		except Exception as ex:
			print('----- /msg_channel() -----')
			print(ex)
			await log_exception(ex, '/msg_channel', interaction)

	######################## SEND MSG TO MEMBER ########################
	@bot.slash_command(name = "tc_msg-member")
	async def msg_member(interaction, msg, member: discord.Member = None, role: discord.Role = None):
		"""
		Send msg to member/role - \\n \\t /$
		Parameters
		----------
		msg: Message content - \\n \\t /$
		member: Server existing member
		role: Role members
		"""
		try:
			await interaction.send("Sending direct message...", ephemeral=True)
			msg = replace_str(msg, {"\\n": "\n", "\\t": "	", "/$": " "})

			if role == None and member == None:
				member = interaction.author

			channel = bot.get_channel(textChannels['log-dms'])
			log_thread = await make_thread(channel, f"✉ DM/ ==▷ 🎭 / 👤")

			if role:
				members = role.members
				for m in members:
					try:
						_sentMsg = await send_dm_msg(interaction, msg, m)
						notifyMe = '─────────────────'
						if _sentMsg:
							notifyMe += f'\nmessage ID : {_sentMsg.id}'
							notifyMe += f'\nchannel ID : {_sentMsg.channel.id}'
							notifyMe += f'\nMember: {m.mention} / {m.name}#{m.discriminator}'
						else: notifyMe += f'\nIssue with this member {m.mention} / {m.name}#{m.discriminator}'
						notifyMe += '\n--------------'
						await log_thread.send(notifyMe)
					except Exception as ex:
						print('----- /msg_member()/send_msg/role -----')
						print(ex)
						pass
				notifyMe = f'\nRole: **{role.mention}**'
				await log_thread.send(notifyMe)
			if member:
				_sentMsg = await send_dm_msg(interaction, msg, member)
				notifyMe = '─────────────────'
				if _sentMsg:
					notifyMe += f'\nmessage ID : {_sentMsg.id}'
					notifyMe += f'\nchannel ID : {_sentMsg.channel.id}'
					notifyMe += f'\nMember: {member.mention} / {member.name}#{member.discriminator}'
				else: notifyMe += f'\nIssue with this member {member.mention} / {member.name}#{member.discriminator}'
				notifyMe += '\n--------------'
				await log_thread.send(notifyMe)

			if role or member:
				notifyMe = f'\n__Content__\n'
				await log_thread.send(notifyMe)
				await log_thread.send(msg)
			await log_thread.edit(archived=True)

		except Exception as ex:
			print('----- /msg_member() -----')
			print(ex)
			await log_exception(ex, '/msg_member', interaction)

	######################## DELETE A MSG ########################
	@bot.slash_command(name = "tc_remove-msg-member")
	async def remove_msg_member(interaction, msg_ids, channel_id):
		"""
		Delete msg from public/private - ,
		Parameters
		----------
		msg_ids: Messages IDs separated by , or space
		channel_id: Channel where to fetch the messages
		"""
		try:
			await interaction.send("Deleting direct message...", ephemeral=True)
			msg_ids = split_str(msg_ids)
			_ch = await bot.fetch_channel(channel_id)
			for msg_id in msg_ids:
				try:
					msg = await _ch.fetch_message(msg_id)
					await msg.delete()
				except Exception as ex:
					print(msg_id)
					pass
		except Exception as ex:
			print('----- /remove_msg_member() -----')
			print(ex)
			await log_exception(ex, '/remove_msg_member', interaction)
