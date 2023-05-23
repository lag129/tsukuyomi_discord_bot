from tsukuyomichan_talksoft import TsukuyomichanTalksoft
tsukuyomichan_talksoft = TsukuyomichanTalksoft(model_version='v.1.2.0')

import os
import soundfile as sf
import discord
import numpy as np
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio

MAX_WAV_VALUE = 32768.0
fs = 24000
wav = []
seed = 1
text = ''
voice = ''
talksoft = TsukuyomichanTalksoft(model_version='v.1.2.0')

TOKEN = '***'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

voiceChannel : VoiceChannel

@client.event
async def on_ready():
	print('つくよみちゃんがサーバーにログインしました！')

@client.event
async def on_message(message):
	global voiceChannel

	#botを無視する 
	if message.author.bot:
		return
	if message.content == '!tsukuyomi':
		voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
		await message.channel.send('つくよみちゃんが参加したよ！')
		return
	elif message.content == '!dtsukuyomi':
		voiceChannel.stop()
		await message.channel.send('つくよみちゃんが退出したよ！')
		await voiceChannel.disconnect()
		return

	#URLを無視する
	if message.content.startswith('.'):
		pass
	else:
		if message.guild.voice_client and message.guild.voice_client.is_playing():
			return
		
		if message.guild.voice_client:
			print(message.content)
			play_voice(message.content)
			source = discord.FFmpegPCMAudio("output.mp3")
			message.guild.voice_client.play(source)
		else:
			pass

def play_voice(text):
	global seed, wav

	wav = talksoft.generate_voice(text, seed)
	wav = wav * MAX_WAV_VALUE
	wav = wav.astype(np.int16)
	os.makedirs('output', exist_ok=True)
	sf.write(f"output.wav", wav, fs, 'PCM_16')
	voiceChannel.play(FFmpegPCMAudio(f"output.wav"))

client.run(TOKEN)