import telebot
import time
import eventlet
import requests
import weather
from time import sleep
import forecastio
import datetime

FORECASTIO_API = ''
URL_VK = 'https://api.vk.com/method/wall.get?domain=rt_russian&count=10&filter=owner'
FILENAME_VK = 'last_known_id.txt'
BASE_POST_URL = 'https://vk.com/wall-40316705_'
BOT_TOKEN = ''
CHANNEL_NAME = '@wentus_news_feed'
LAT = 55.752220
LNG = 37.615560

time = datetime.datetime.now()
forecast = forecastio.load_forecast(FORECASTIO_API, LAT, LNG, time)
cc = forecast.currently()
currstat = cc.summary
currtemp = cc.temperature

ch = forecast.hourly()
df = ch.summary

cd = forecast.daily()
for hourlyData in cd.data:
     hitemp = hourlyData.temperatureMax
for hourlyData in cd.data:
    lowtemp = hourlyData.temperatureMin

lowtemp = int(lowtemp)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['welcome'])
def send_welcome(message):
    bot.reply_to(message, "Welcome, how are you doing?")


@bot.message_handler(commands=['info'])
def send_help(message):
    _help = ('The bot has following commands: \n/welcome: Welcoming new person. \n/info: Information about bot. \n/news: Latest News from Russia Today. \n/weather: Moscow''s weather for today.')
    bot.reply_to(message, _help)



def get_data():
    timeout = eventlet.Timeout(10)
    try:
        feed = requests.get(URL_VK)
        return feed.json()
    except eventlet.timeout.Timeout:
        return None
    finally:
        timeout.cancel()

def send_new_posts(items, last_id):
    for item in items:
        if item['id'] <= last_id:
            break
        link = '{!s}{!s}'.format(BASE_POST_URL, item['id'])
        bot.send_message(CHANNEL_NAME, link)
        time.sleep(1)
    return

@bot.message_handler(commands=['weather'])
def get_weather(message):
    bot.reply_to(message, "Current conditions: %s %dC.\nToday: %s \nHigh: %dC.\nLow: %sC." % (currstat, currtemp, df, hitemp, lowtemp))

@bot.message_handler(commands=['news'])
def check_new_posts_vk(message):
    with open(FILENAME_VK, 'rt') as file:
        last_id = int(file.read())
        if last_id is None:
            return
    try:
        feed = get_data()
        if feed is not None:
            entries = feed['response'][1:]
            try:
                tmp = entries[0]['is_pinned']
                send_new_posts(entries[1:], last_id)
            except KeyError:
                send_new_posts(entries, last_id)
            with open(FILENAME_VK, 'wt') as file:
                try:
                    tmp = entries[0]['is_pinned']
                    file.write(str(entries[1]['id']))
                except KeyError:
                    file.write(str(entries[0]['id']))
    except Exception as ex:
        pass
    return

bot.polling()

