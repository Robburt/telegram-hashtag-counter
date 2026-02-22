import telebot
from modules import WindowInterface

with open('TOKEN.txt') as f:
    TOKEN = f.readline()

bot = telebot.TeleBot(TOKEN)

@bot.channel_post_handler()
def scanner(msg):
    print(msg)

if __name__ == "__main__":
    WindowInterface.WindowInterface()