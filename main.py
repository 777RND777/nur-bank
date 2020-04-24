from db import users, User
import telebot
import consts as make


bot = telebot.TeleBot("990303016:AAEQfd5PnZsjgitwo0HvcLVLMQty47JI_WU")
person = User(0, 0, "first_name", "last_name", "user_name", 0, 0, 0)


@bot.message_handler(commands=["start"])
def start_message(message):
    global person
    for user in users:
        if user.id == message.from_user.id:
            person = user
            break
    else:
        person = User(
            0,
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            0, 0, 0
        )
    bot.send_message(message.chat.id, "Приветствуем вас в НурБанке, " + person.username + "!",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text.lower() == "изменить имя")
def set_name(message):
    make.NAME = True
    bot.send_message(message.chat.id, "Как вы хотите, чтобы к вам обращались?")


def type_name(message):
    make.NAME = False
    person.set_username(message.text)
    bot.send_message(message.chat.id, "Ваше имя изменено на '" + person.username + "'.")


@bot.message_handler(func=lambda message: message.text.lower() == "оставить заявку на долг")
def make_loan_request(message):
    make.REQUEST = True
    bot.send_message(message.chat.id, "Какую сумму вы хотите взять в долг?")


def type_request(message):
    make.REQUEST = False
    person.make_request(message.text)
    bot.send_message(message.chat.id, "Новая сумма вашего долга состовляет: " + str(person.debt) + "k (+ " +
                     str(person.requested) + "k).\n")


@bot.message_handler(func=lambda message: message.text.lower() == "уведомить об оплате долга")
def make_payment_notification(message):
    make.PAYMENT = True
    bot.send_message(message.chat.id, "Какую сумму из вашего долга " + str(person.debt) + "k вы оплатили?")


def type_payment(message):
    make.PAYMENT = False
    person.make_payment(message.text)
    bot.send_message(message.chat.id, "Ваше уведомление о внесении " + message.text + "k рассматривается.")


@bot.message_handler(func=lambda message: message.text.lower() == "посмотреть сумму долга")
def get_current_debt(message):
    bot.send_message(message.chat.id, "Ваш долг состовляет: " + str(person.debt) + "k.")
    if person.approving > 0.0:
        bot.send_message(message.chat.id, "Ожидает подтверждения об оплате сумма: " + str(person.approving) + "k.")
    if person.requested > 0.0:
        bot.send_message(message.chat.id, "Оставлена заявка в долг на сумму: " + str(person.requested) + "k.")


@bot.message_handler(content_types=["text"])
def send_text(message):
    if make.REQUEST:
        type_request(message)
    elif make.PAYMENT:
        type_payment(message)
    elif make.NAME:
        type_name(message)
    else:
        bot.send_message(message.chat.id, "Вы неправильно ввели команду.")


keyboard = telebot.types.ReplyKeyboardMarkup()
keyboard.row("оставить заявку на долг", "уведомить об оплате долга")
keyboard.row("посмотреть сумму долга", "изменить имя")


bot.polling()
