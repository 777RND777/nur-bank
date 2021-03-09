from db import *
import telebot


bot = telebot.TeleBot("990303016:AAEQfd5PnZsjgitwo0HvcLVLMQty47JI_WU")


@bot.message_handler(commands=["start"])
def start_message(message):
    user_info = {
        'user_id': message.from_user.id,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
    }
    user = add_user(user_info)
    bot.send_message(message.chat.id, f"Приветствуем вас в НурБанке, {user['username']}!",
                     reply_markup=keyboard)


# @bot.message_handler(func=lambda message: message.text.lower() == "изменить имя")
# def set_name(message):
#     make.NAME = True
#     bot.send_message(message.chat.id, "Как вы хотите, чтобы к вам обращались?")
#
#
# def type_name(message):
#     make.NAME = False
#     person.set_username(message.text)
#     bot.send_message(message.chat.id, f"Ваше имя изменено на '{person.username}'.")
#
#
# @bot.message_handler(func=lambda message: message.text.lower() == "оставить заявку на долг")
# def make_loan_request(message):
#     make.REQUEST = True
#     bot.send_message(message.chat.id, "Какую сумму вы хотите взять в долг?")
#
#
# def type_request(message):
#     if check_valid(message):
#         make.REQUEST = False
#         person.make_request(message.text)
#         bot.send_message(message.chat.id, f"Новая сумма вашего долга состовляет: {person.debt}k "
#                                           f"(+{person.requested}k).\n")
#
#
# @bot.message_handler(func=lambda message: message.text.lower() == "уведомить об оплате долга")
# def make_payment_notification(message):
#     make.PAYMENT = True
#     bot.send_message(message.chat.id, f"Какую сумму из вашего долга {person.debt}k вы оплатили?")
#
#
# def type_payment(message):
#     if check_valid(message):
#         make.PAYMENT = False
#         person.make_payment(message.text)
#         bot.send_message(message.chat.id, f"Ваше уведомление об оплате {message.text} k находится на рассмотрении.")
#         return True
#     return False
#
#
# def check_valid(message):
#     if message.text.isdigit():
#         return True
#     bot.send_message(message.chat.id, "Введенное вами значение не является числовым. "
#                                       "Введите сумму, используя только числа.")
#     return False
#
#
# @bot.message_handler(func=lambda message: message.text.lower() == "посмотреть сумму долга")
# def get_current_debt(message):
#     # actually this part is useless because bot will not stop it's run in the future
#     global person
#     if not person.id:
#         person = get_person(message)
#
#     bot.send_message(message.chat.id, f"Сумма вашего долга состовляет: {person.debt}k.")
#     if person.approving > 0.0:
#         bot.send_message(message.chat.id, f"Ожидает подтверждения об оплате сумма: {person.approving}k.")
#     if person.requested > 0.0:
#         bot.send_message(message.chat.id, f"Оставлена заявка на сумму: {person.requested}k.")


@bot.message_handler(content_types=["text"])
def send_text(message):
    # if make.REQUEST:
    #     type_request(message)
    #     bot.send_message(make.OWNER,
    #                      f"{message.from_user.first_name} {message.from_user.last_name} запросил {message.text}k")
    # elif make.PAYMENT:
    #     if type_payment(message):
    #         bot.send_message(make.OWNER,
    #                          f"{message.from_user.first_name} {message.from_user.last_name} оплатил {message.text}k")
    # elif make.NAME:
    #     type_name(message)
    # else:
    #     bot.send_message(message.chat.id, "Вы неправильно ввели команду.")
    print(message)

keyboard = telebot.types.ReplyKeyboardMarkup()
keyboard.row("оставить заявку на долг", "уведомить об оплате долга")
keyboard.row("посмотреть сумму долга", "изменить имя")

bot.polling()
