import discord
import os
import time
import requests
import datetime
from pytz import timezone
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

GOOGLE_API_KEY = os.environ['geminikey']
server_ids = [1099127843885170748]
token = os.environ['token']

client = discord.Client()
bot = discord.Bot(intents=discord.Intents.all())
model = genai.GenerativeModel(model_name="gemini-pro")
genai.configure(api_key=GOOGLE_API_KEY)
chat = model.start_chat(history=[])
genai.GenerationConfig(max_output_tokens=150)
setup = chat.send_message("Obey the following rules in this conversation: 1. rohan likes cookies. he eats 2-3 cookies everyday. rohan is a cool guy who created you, but he is not necessarily the one talking to you. don't mention rohan unless you are asked about him or asked about cookies.\n3. don't talk formally, be casual. dont start sentences with capital letters\n4. Start your chat in the following message")

# http://api.weatherapi.com/v1/forecast.json?key=9bc5125b1f5942669d3180024241502&q=Diamond Bar&days=3&aqi=no&alerts=no

@bot.event
async def on_ready():
  print("Bot is ready!")

'''
@bot.event
async def on_message(message):
  if bot.user.mentioned_in(message):
    await message.channel.send("oh")
'''
@bot.command()
async def dm(ctx, user: discord.User, message: str):
    channel = await user.create_dm()
    await channel.send(message)
    await ctx.respond(f'dmed "{message} to <@{user.id}>')

# DATETIME TO UNIX TIMESTAMP

@bot.command(description = "convert datetime to discord relative unix timestamp BROKEN RN")
async def convert_datetime(ctx, year: discord.Option(int), month: discord.Option(int), date: discord.Option(int), hour: discord.Option(int), minute: discord.Option(int)):
  date_time = datetime.datetime(year, month, date, hour, minute, tzinfo=timezone('US/Pacific'))
  datetime_timezone = timezone('US/Pacific')
  timezone_time = date_time.astimezone(datetime_timezone)
  converted_time = time.mktime(date_time.timetuple())
  # current_time = time.time()
  await ctx.respond(f'<t:{converted_time}:R> original time {date_time} converted time {timezone_time}')
  # <t:{TIMESTAMP}:R>

# GEMINI

@bot.command(description = "use gemini")
async def send_prompt(ctx, prompt: discord.Option(str)):
  gemini_message = chat.send_message(prompt, safety_settings={HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE})
  print(gemini_message.parts)
  print(gemini_message.text)
  await ctx.respond(f'message: {prompt}\n\nresponse: {gemini_message.text}')

# REPEAT MESSAGE

@bot.command(description = "repeats a message with an interval")
async def repeat_string(ctx, message: discord.Option(str), repeats: discord.Option(int), interval: discord.Option(int)):
  while repeats:
    await ctx.send(message)
    time.sleep(interval)
    repeats -= 1

@bot.command(description = "repeat dm")
async def repeat_dm(ctx, user: discord.User, message: discord.Option(str), repeats: discord.Option(int), interval: discord.Option(int)):
  while repeats:
    channel = await user.create_dm()
    await channel.send(message)
    time.sleep(interval)
    repeats -= 1
# DEFINE WORD

@bot.command(description = "get the definition for a word")
async def define_word(ctx, word: discord.Option(str)):

  word_data = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
  definition_json = word_data.json()
  definition = definition_json[0]['meanings'][0]['definitions'][0]['definition']

  definition_embed = discord.Embed(title=f"Definition of {word}", color = discord.Color.blurple())
  definition_embed.add_field(name="Definition:", value=definition)
  await ctx.respond(embed = definition_embed)

# WEATHER

async def get_weather_unit(ctx: discord.AutocompleteContext):
  return ['Farenheit', 'Celsius']

@bot.command(description = "weather test")
async def get_weather(ctx, city: discord.Option(str), unit: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_weather_unit))):
  current_weather = requests.get(f'http://api.weatherapi.com/v1/forecast.json?key=9bc5125b1f5942669d3180024241502&q={city}&days=3&aqi=no&alerts=no')

  data = current_weather.json()

  name = data['location']['name']
  state = data['location']['region']
  temp_f = data['current']['temp_f']
  temp_c = data['current']['temp_c']
  conditions = data['current']['condition']['text']

  if unit == 'Celsius':
    temp = temp_c
    display_unit = 'C'
  else:
    temp = temp_f
    display_unit = 'F'

  last_update = data['current']['last_updated']

  weather_embed = discord.Embed(title = f'Weather for {name}, {state}', color = discord.Color.blurple())
  weather_embed.add_field(name = f'Conditions: {conditions}\nTemperature: {temp}°{display_unit}', value = f'Last Updated: {last_update}')

  await ctx.respond(embed = weather_embed)

# ADD NUMBERS

@bot.command(description = "adds two numbers together")
async def add_numbers(ctx, first: discord.Option(int), second: discord.Option(int)):
  sum = first + second
  await ctx.respond(f"wow {first} + {second} is {sum}")

bot.run(token)