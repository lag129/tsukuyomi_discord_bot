import os
import soundfile as sf
import discord
import openai
import numpy as np

from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio
from tsukuyomichan_talksoft import TsukuyomichanTalksoft

# DiscordのAPI設定 
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

talksoft = TsukuyomichanTalksoft(model_version='v.1.2.0')
voiceChannel : VoiceChannel

# ファイルを実行した時
@client.event
async def on_ready():
	print('つくよみちゃんがサーバーにログインしました！')

@client.event
async def on_message(message):
	global voiceChannel

	# Botを無視する 
	if message.author.bot:
		return
	# 入出した時
	if message.content == '!tsukuyomi':
		voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
		await message.channel.send('つくよみちゃんが参加したよ！')
		return
	# 退出した時
	elif message.content == '!dtsukuyomi':
		voiceChannel.stop()
		await message.channel.send('つくよみちゃんが退出したよ！')
		await voiceChannel.disconnect()
		return

	# URLを無視する
	if message.content.startswith('.'):
		pass
	else:
		if message.guild.voice_client and message.guild.voice_client.is_playing():
			return
		
		# 文章を読み上げる
		if message.guild.voice_client:
			print(message.content)

			# ChatGPTに送信
			openai.api_key = os.environ['OPENAI_API_KEY'] 
			response = openai.ChatCompletion.create(
				model="gpt-3.5-turbo",
				messages=[
					{"role": "system", "content": "簡潔に日本語で答えて。"},
					{"role": "user", "content": message.content},
					],
				)
			response_result = response["choices"][0]["message"]["content"]
			print(response_result)

			# DiscordのChannelに送信
			await message.channel.send(response_result)
			# 音声読み上げ
			play_voice(response_result)
		else:
			pass

# 音声合成
def play_voice(text):
	wav = talksoft.generate_voice(text, 1)
	wav = wav * 32768.0
	wav = wav.astype(np.int16)
	os.makedirs('output', exist_ok=True)
	sf.write(f"output.wav", wav, 24000, 'PCM_16')
	voiceChannel.play(FFmpegPCMAudio(f"output.wav"))

client.run(os.environ['DISCORD_API_KEY'])