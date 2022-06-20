import telebot
from telebot import types
from telebot import custom_filters
from functools import wraps
from app import pdata
from app import runme


API_TOKEN = '5560316134:AAEHvQhnGireamMnJzDNA-vqLbU5OW5H2aw'

bot = telebot.TeleBot(API_TOKEN)
bot.add_custom_filter(custom_filters.ChatFilter())


commands = """
These are the available commands
/start - run bot process
/exam - teka PEOS exam
/ping - check if bot is working
/cmd - check available commands
/faq - Frequently asked questions
"""

faqs = """
Frequently Asked Questions

1. I can't access the bot, why?

- This bot is for private use only, unknown user/s are blocked from accessing the bot.

2. After I provide the information(Ereg and name) it says 'Account not found', why?

- You may have provided Incorrect Info(Typo). If you think all your inputs are correct you may use /retry command to try again otherwise contact the developer.

3. I'm stuck in Module {module number}, why?

- Please be patient as Bot is trying It's best to pass the exam. however if you've been stuck for 5-10 minutes. You may try again or Contact the developer. 

@esperanzax
"""


from functools import wraps


def is_known_username(username):
    '''
    Returns a boolean if the username is known in the user-list.
    '''
    known_usernames = ['esperanzax']

    return username in known_usernames


def private_access():
    """
    Restrict access to the command to users allowed by the is_known_username function.
    """
    def deco_restrict(f):

        @wraps(f)
        def f_restrict(message, *args, **kwargs):
            username = message.from_user.username

            if is_known_username(username):
                return f(message, *args, **kwargs)
            else:
                bot.reply_to(message, text="You are not allowed to use this command.")

        return f_restrict  # true decorator

    return deco_restrict
    
@bot.message_handler(commands=['start'])
def welcome(message):
    username = message.chat.first_name
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width = 1)
    markup.add('GET STARTED')
    bot.send_message(message.chat.id, 'Hi, {}'.format(username), reply_markup=markup)
    bot.register_next_step_handler(message, ereg_number)

@bot.message_handler(commands=['exam', 'retry'])
@private_access()
def ereg_number(message):
    bot.send_message(message.chat.id, "What's your E-Registration number?")
    bot.register_next_step_handler(message, getLastname)

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

@bot.message_handler(commands=['faq'])
def cmd(message):
    bot.send_message(message.chat.id, faqs)

@bot.message_handler(commands=['cmd'])
def cmd(message):
    bot.send_message(message.chat.id, commands)

@bot.message_handler(commands=['ping'])
def greet(message):
    bot.send_message(message.chat.id, "bot is working fine 😄")
    
bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()

bot.infinity_polling(skip_pending=True)
