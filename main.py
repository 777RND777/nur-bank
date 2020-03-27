from db import *
from datetime import datetime
import telebot


bot = telebot.TeleBot("990303016:AAEQfd5PnZsjgitwo0HvcLVLMQty47JI_WU")


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Приветствуем вас в НурБанке!", reply_markup=bank_keyboard)


@bot.message_handler(commands=["set_name"])
def set_name(message):
    bot.send_message(message.chat.id, "Как вас зовут?")
    user.name = "murat"
    # bot.send_message(message.chat.id, "Здравствуйте, " + murat.name + "! Что вы хотите сделать?")


@bot.message_handler(commands=["request"])
def create_request(message):
    bot.send_message(message.chat.id, "Какую сумму вы хотите взять в долг?")
    user.debt += 0


@bot.message_handler(commands=["payment"])
def payment_notification(message):
    bot.send_message(message.chat.id, "Какую сумму из вашего долга " + str(user.debt) + "k вы оплатили?")
    user.wait += 0


@bot.message_handler(commands=["debt"])
def get_current_debt(message):
    current_time = datetime.now().strftime("%H:%M:%S   %d/%m/%Y")
    bot.send_message(message.chat.id, "Ваш долг на " + current_time + " состовляет: " + str(user.debt) + "k")
    bot.send_message(message.chat.id, "Из этой суммы ожидает подтверждения: " + str(user.wait) + "k")


user = User()
bank_keyboard = telebot.types.ReplyKeyboardMarkup()
bank_keyboard.row_width = 2
bank_keyboard.row("оставить заявку на долг", "уведомить об оплате долга")
bank_keyboard.row("посмотреть ваш долг", "выход")


bot.polling()
