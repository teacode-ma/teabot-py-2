from setup.properties import *
from setup.actions import *
import pytz

def init_msg_log(params):
	
	bot = params['bot']
	slash = params['slash']
	purgedMsgs = []




	######################## PURGE ########################
	@slash.slash(name="purge", description="Clear all messages", guild_ids=[guildId],
		permissions={ guildId: slash_permissions({'founders'}, {'members', 'everyone'}) })
	async def purge(ctx, limit: int=None):
		try:
			nonlocal purgedMsgs
			
			if not is_founders(ctx):
				await ctx.send('❌ Missing Permissions')
				return
			
			purgedMsgs = []
			channelsToClear = [
				textChannels['voice-chat'],
				textChannels['help-chat']
			]
			if not limit and ctx.channel.id not in channelsToClear:
				await ctx.send('❌ Wrong Target Channel', hidden=True)
				return

			if limit:
				if limit > 500:
					await ctx.send('You cannot delete more than 500 messages', hidden=True)
					return
				else:
					await ctx.send('Clearing messages ...', hidden=True)
					deletedMsgs = await ctx.channel.purge(limit = limit, check = isNotPinned)
					await ctx.send(f'{len(deletedMsgs)} message(s) cleared', hidden=True)
					count = len(deletedMsgs)
					deletedMsgs.reverse()
					await logPurgedMessages(ctx, count, deletedMsgs)
				return

			MAX_TO_DELETE = 500
			await ctx.send('Clearing everything ...', hidden=True)
			# time.sleep(2)
			await deleteMsg(ctx, MAX_TO_DELETE)
		except Exception as ex:
			print('----- /purge() -----')
			print(ex)

	def isNotPinned(msg):
		return not msg.pinned

	async def deleteMsg(ctx, limit):
		try:
			nonlocal purgedMsgs
			deletedMsgs = await ctx.channel.purge(limit = limit, check = isNotPinned)
			purgedMsgs += deletedMsgs
			deletedMsgs = len(deletedMsgs)
			if (deletedMsgs > 0):
				return await deleteMsg(ctx, limit)
			else:
				count = len(purgedMsgs)
				purgedMsgs.reverse()
				await ctx.send(f'{len(purgedMsgs)} message(s) cleared', hidden=True)
				await logPurgedMessages(ctx, count, purgedMsgs)
				return len(purgedMsgs)
		except Exception as ex:
			print('----- deleteMsg() -----')
			print(ex)

	async def logPurgedMessages(ctx, count, _purgedMsgs):
		logMsgsChannel = bot.get_channel(textChannels['log-msg'])
		headerMsg = f"🗑 **purge({count}) | {ctx.channel.mention}** ──────────"
		await logMsgsChannel.send(headerMsg)
		for m in _purgedMsgs:
			msg = '──────────────────────'
			msg += f'\n🗑 by {m.author.mention} in {m.channel.mention}'
			
			timeZ_Ma = pytz.timezone('Africa/Casablanca')
			created_at = m.created_at.astimezone(timeZ_Ma).strftime("%d %B %Y - %H:%M")
			edited_at = None
			if m.edited_at:
				edited_at =  m.edited_at.astimezone(timeZ_Ma).strftime("%d %B %Y - %H:%M")	
			msg += f'\n📅 {created_at} ➜ {edited_at}'
			msg += f'\n__Content__\n{m.content}'
			msg += get_attachments(m)
			msg += get_embeds(m)
			msg += f'\n──────────────────────'
			await logMsgsChannel.send(msg)