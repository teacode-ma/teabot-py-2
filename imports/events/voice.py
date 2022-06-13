from setup.data.params import *
from setup.actions.voice import *
from setup.actions.common import *

def init_events_voice(params):

	bot = params['bot']

	######################## VOICE ########################
	@bot.event
	async def on_voice_state_update(member, voice1, voice2):
		try:
			await check_deafen(params, member, voice1, voice2)
			if (voice1 and voice2) and (voice1.channel and voice2.channel) and (voice1.channel.id == voice2.channel.id):
				return
			guild = bot.get_guild(guildId)
			if voice1 and voice1.channel:
				await logVoice(params, guild, member, voice1, False, member.remove_roles)
			if voice2 and voice2.channel:
				await logVoice(params, guild, member, voice2, True, member.add_roles, voice1, voice2)

			# voice_state = member.guild.voice_client
			# if voice_state and len(voice_state.channel.members) == 1:
			# 	await voice_state.disconnect()
		except Exception as ex:
			print('----- on_voice_state_update(evt) -----')
			print(ex)
			await log_exception(ex, 'on_voice_state_update(evt)', None, bot)
