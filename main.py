from db import *
import telebot


bot = telebot.TeleBot("990303016:AAEQfd5PnZsjgitwo0HvcLVLMQty47JI_WU")
person = User(0, "user_name", 0, 0)
setting_request = False
setting_payment = False
setting_name = False


@bot.message_handler(commands=["start"])
def start_message(message):
    global person
    for user in users:
        if user.id == message.from_user.id:
            person = user
            break
    else:
        person = User(message.from_user.id, message.from_user.first_name, 0, 0)
    bot.send_message(message.chat.id, "Приветствуем вас в НурБанке, " + person.name + "!", reply_markup=bank_keyboard)


@bot.message_handler(commands=["request"])
def create_request(message):
    global setting_request
    setting_request = True
    bot.send_message(message.chat.id, "Какую сумму вы хотите взять в долг?")


def type_request(message):
    global setting_request
    setting_request = False
    person.debt += amount_converter(message.text)
    bot.send_message(message.chat.id, "Новая сумма вашего долга состовляет: " + str(person.debt) + "k")


@bot.message_handler(commands=["payment"])
def payment_notification(message):
    global setting_payment
    setting_payment = True
    bot.send_message(message.chat.id, "Какую сумму из вашего долга " + str(person.debt) + "k вы оплатили?")


def type_payment(message):
    global setting_payment
    setting_payment = False
    person.wait += amount_converter(message.text)
    bot.send_message(message.chat.id, "Ваше уведомление о внесении " + message.text + "k рассматривается.")


def amount_converter(amount):
    if amount.endswith("000"):
        return float(amount) / 1000
    return float(amount)


@bot.message_handler(commands=["debt"])
def get_current_debt(message):
    wait = ""
    if person.wait > 0.0:
        wait = " (-" + str(person.wait) + "k на рассмотрении)"
    bot.send_message(message.chat.id, "Ваш долг состовляет: " + str(person.debt) + "k" + wait)


@bot.message_handler(commands=["set_name"])
def set_name(message):
    global setting_name
    setting_name = True
    bot.send_message(message.chat.id, "Как вас зовут?")


def type_name(message):
    global setting_name
    setting_name = False
    person.name = message.text
    bot.send_message(message.chat.id, "Ваше имя изменено на '" + person.name + "'. Что вы хотите сделать?")


@bot.message_handler(content_types=["text"])
def send_text(message):
    global setting_request, setting_payment, setting_name
    if setting_request:
        type_request(message)
    elif setting_payment:
        type_payment(message)
    elif setting_name:
        type_name(message)
    else:
        if message.text.lower() == "оставить заявку на долг":
            create_request(message)
        elif message.text.lower() == "уведомить об оплате долга":
            payment_notification(message)
        elif message.text.lower() == "посмотреть сумму долга":
            get_current_debt(message)
        elif message.text.lower() == "изменить ваше имя":
            set_name(message)


bank_keyboard = telebot.types.ReplyKeyboardMarkup()
bank_keyboard.row("оставить заявку на долг", "уведомить об оплате долга")
bank_keyboard.row("посмотреть сумму долга", "изменить ваше имя")


bot.polling()
