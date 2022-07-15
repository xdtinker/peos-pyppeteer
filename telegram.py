import telebot
import os
from telebot import types
from functools import wraps
from app import pdata
from app import runme

API_TOKEN = os.environ['API_KEY']

bot = telebot.TeleBot(API_TOKEN, parse_mode=None)

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

2. How do I get access?

- Contact the developer and ask for permission.

3. After I provide the information(Ereg and name) it says 'Account not found', why?

- You may have provided Incorrect Info(Typo). If you think all your inputs are correct you may use /retry command to try again otherwise contact the developer.

4. I'm stuck in Module {module number}, why?

- Please be patient as Bot is trying It's best to pass the exam. however if you've been stuck for 5-10 minutes. You may try again or Contact the developer. 

5. The bot sent me "Something went wrong. Use /retry to try again" after passing the 7th Module.

- This is known issue. However if the bot has sent or notify you that Module 7 is passed, is means that it has passed the exam. 

6. The bot is occupied, what do I do?

- This bot is only capable of being used 1 (one) user at a time. What you can do is wait for 2-5 minutes. Don't worry It'll be quick.

@esperanzax
"""

temp_user = []
_admin = ['esperanzax']

def isOccupied():
    if pdata.is_occupied:
        return True
    else:
        return False

def chatId(id):
    _id = pdata.chat_id = id
    return _id

def isAdmin(username):
    '''
    Returns a boolean if the username is known in the user-list.
    '''
    admin = ['esperanzax'] + temp_user

    return username in admin


def isGuest(username):
    if (username in _admin):
        return False
    elif (username not in temp_user) or (username in temp_user):
        return True

def private_access():
    """
    Restrict access to the command to users allowed by the is_known_username function.
    """
    def deco_restrict(f):

        @wraps(f)
        def f_restrict(message, *args, **kwargs):
            username = message.from_user.username

            if isAdmin(username):
                return f(message, *args, **kwargs)
            else:
                bot.reply_to(message, text="You are not allowed to use this command.")

        return f_restrict  # true decorator+

    return deco_restrict

@bot.message_handler(commands=['members'])
def members(message):
    _user = message.from_user.username
    if isGuest(_user):
        bot.reply_to(message, text="You are not allowed to use this command.")
    else:
        if temp_user == []:
            bot.reply_to(message, 'No registered members')
        else:
            _members = 'Registered members\n\n' + '\n'.join([member for member in temp_user])
            bot.reply_to(message, _members)

@bot.message_handler(commands=['remove'])
def members(message):
    _user = message.from_user.username
    if isGuest(_user):
        bot.reply_to(message, text="You are not allowed to use this command.")
    else:
        if temp_user == []:
            bot.reply_to(message, 'No member/s to remove')
        else:
            bot.reply_to(message, 'OK, Send me the username you want to remove')
            bot.register_next_step_handler(message, remove_user)

def remove_user(message):
    _user = message.text
    if _user in temp_user:
        temp_user.remove(_user)
        bot.reply_to(message, 'User {} has been removed.'.format(_user))
    else:
        bot.reply_to(message, 'User {} not found.'.format(_user))

@bot.message_handler(commands=['add'])
def add_user(message):
    _user = message.from_user.username
    if isGuest(_user):
        bot.reply_to(message, text="You are not allowed to use this command.")
    else:
        bot.reply_to(message, 'Who would you like to grant privilege?')
        bot.register_next_step_handler(message, user)
        
def user(message):
    _user = message.text
    if _user in temp_user:
        bot.reply_to(message, 'User {} is existing member.'.format(_user))
    elif _user in _admin:
        bot.reply_to(message, 'You can\'t add yourself.'.format(_user))
    else:
        temp_user.append(str(_user))
        bot.reply_to(message, 'user {} is now a member.'.format(_user))
    
@bot.message_handler(commands=['start'])
def welcome(message):
    username = message.chat.first_name
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width = 1)
    markup.add('GET STARTED')
    bot.reply_to(message, 'Hi, {}'.format(username), reply_markup=markup)
    bot.register_next_step_handler(message, ereg_number)

@bot.message_handler(commands=['exam', 'retry'])
@private_access()
def ereg_number(message):
    if isOccupied():
        bot.reply_to(message, "Bot is currently occupied.. you can try again in 2-5 minutes.")
    else:
        bot.reply_to(message, "What's your E-Registration number?")
        bot.register_next_step_handler(message, getLastname)

def getLastname(message):
    try:
        pdata.eNumber = int(message.text)
        bot.reply_to(message, "What's your Last name?") 
        bot.register_next_step_handler(message, getFirstname)
    except ValueError:
        bot.reply_to(message, 'Strings are not allowed in E-Reg number. Use /retry to try again.')  
    except Exception as e:
        print('error', e.with_traceback)

def getFirstname(message):
    pdata.lasttname=message.text
    bot.reply_to(message, "What's your first name?") 
    bot.register_next_step_handler(message, run)

def run(message):
    pdata.firstname=message.text
    if isOccupied():
        bot.reply_to(message, "Bot is currently occupied.. you can try again in 2-5 minutes.")
    else:
        pdata.is_occupied = True
        userID = message.chat.id
        chatId(userID)
        runme()
@bot.message_handler(commands=['faq'])
def cmd(message):
    bot.reply_to(message, faqs)

@bot.message_handler(commands=['cmd'])
def cmd(message):
    bot.reply_to(message, commands)

@bot.message_handler(commands=['ping'])
def greet(message):
    bot.reply_to(message, "bot is working fine 😄")
    
bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()

bot.infinity_polling(skip_pending=True)
