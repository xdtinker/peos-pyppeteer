import telebot
from telebot import custom_filters
from app import pdata
from app import runme

API_TOKEN = '5560316134:AAEHvQhnGireamMnJzDNA-vqLbU5OW5H2aw'

bot = telebot.TeleBot(API_TOKEN)

bot.add_custom_filter(custom_filters.ChatFilter())

commands = """
These are the available commands
/start - run bot process
/help - get help
/ping - check if bot is working
"""

@bot.message_handler(commands=['cmd'])
def cmd(message):
    bot.send_message(message.chat.id, commands)

@bot.message_handler(commands=['ping'])
def greet(message):
  bot.send_message(message.chat.id, "I'm alive!")

@bot.message_handler(chat_id=[879252455], commands=['start', 'retry'])
def start(message):
    bot.send_message(message.chat.id, "What's your E-Registration number?")
    bot.register_next_step_handler(message, getLastname)

@bot.message_handler(commands=['start', 'retry'])
def guest(message):
    bot.send_message(message.chat.id, "You are not allowed to use this command, Administration rights required.")

def getLastname(message):
    try:
        pdata.eNumber = int(message.text)
        bot.send_message(message.chat.id, "What's your Last name?") 
        bot.register_next_step_handler(message, getFirstname)
    except ValueError:
        bot.send_message(message.chat.id, 'Strings are not allowed in E-Reg number. Use /retry to try again.')  
    except Exception as e:
        print('error', e.with_traceback)

def getFirstname(message):
    pdata.lasttname=message.text
    bot.send_message(message.chat.id, "What's your first name?") 
    bot.register_next_step_handler(message, run)

def run(message):
    pdata.firstname=message.text
    bot.send_message(message.chat.id, "Verifying account infromation")
    runme()

bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()

bot.infinity_polling(skip_pending=True)
