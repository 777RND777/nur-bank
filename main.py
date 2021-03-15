from db import *
from telebot import types
import telebot


BACK = "назад"
bot = telebot.TeleBot("990303016:AAEQfd5PnZsjgitwo0HvcLVLMQty47JI_WU")


@bot.message_handler(commands=["start"])
def start_message(message):
    user = get_user(message.from_user.id)
    if user:
        bot.send_message(message.chat.id, f"С возвращением в НурБанк, {user['username']}!")
        return

    user_info = {
        'user_id': message.from_user.id,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
    }
    user = create_user(user_info)
    bot.send_message(message.chat.id, f"Приветствуем вас в НурБанке, {user['username']}!",
                     reply_markup=keyboard)


def validation_check(money_func):
    def wrapper(message):
        value = message.text
        if value == BACK:
            bot.send_message(message.chat.id, "Вы вернулись в меню", reply_markup=keyboard)
            return
        elif value.endswith("к") or value.endswith("k"):
            value = value[:-1] + "000"
        elif len(value) < 4 or not value.endswith("000"):
            value = value + "000"
        try:
            value = int(value)
            money_func(message, value)
        except ValueError:
            msg = bot.send_message(message.chat.id,
                                   "Вы неправильно ввели сумму.\n"
                                   "Правильные примеры: '5000' / '5' / '5к'.",
                                   reply_markup=keyboard_back)
            bot.register_next_step_handler(msg, wrapper)
    return wrapper


@bot.message_handler(func=lambda message: message.text == "оставить заявку на долг")
def make_loan_request(message):
    value = get_user_pending_loan_amount(message.from_user.id)
    if value == 3:
        bot.send_message(message.chat.id, f"У вас слишком много ожидающих заявок. Дождитесь ответа на предыдущие.")
    else:
        msg = bot.send_message(message.chat.id, "Какую сумму вы хотите взять в долг?",
                               reply_markup=keyboard_back)
        bot.register_next_step_handler(msg, loan_info)


@validation_check
def loan_info(message, value):
    application = {
        'user_id': message.from_user.id,
        'value': value,
    }
    create_application(application)
    bot.send_message(message.chat.id,
                     f"Ваша заявка на получение долга в размере {value:,} отправлена на рассмотрение.",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "уведомить об оплате долга")
def make_payment_notification(message):
    msg = bot.send_message(message.chat.id, "Какую сумму из вашего долга вы оплатили?",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, payment_info)


@validation_check
def payment_info(message, value):
    application = {
        'user_id': message.from_user.id,
        'value': -value,
    }
    create_application(application)
    bot.send_message(message.chat.id,
                     f"Ваше уведомление о совершении оплаты в размере {value:,} находится на проверке.",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "посмотреть сумму долга")
def get_current_debt(message):
    user = get_user(message.from_user.id)
    if not user['debt']:
        bot.send_message(message.chat.id, "У вас нет активных долгов.",
                         reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, f"Сумма долга: {user['debt']:,}.",
                         reply_markup=keyboard)

    value = get_user_pending_loans(message.from_user.id)
    if value > 0:
        bot.send_message(message.chat.id, f"Сумма в долг на рассмотрении: {value:,}.")

    value = get_user_pending_payments(message.from_user.id)
    if value > 0:
        bot.send_message(message.chat.id, f"Оплаченная сумма на рассмотрении: {value:,}.")


@bot.message_handler(func=lambda message: message.text == "изменить имя")
def change_username(message):
    msg = bot.send_message(message.chat.id, "Как вы хотите, чтобы к вам обращались?\n"
                                            f"Имя '{BACK}' не разрешено. Вы будете отправлены назад.",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, type_username)


def type_username(message):
    if message.text == BACK:
        bot.send_message(message.chat.id, "Вы вернулись в меню", reply_markup=keyboard)
        return
    user_info = {'username': message.text}
    change_user(message.from_user.id, user_info)
    bot.send_message(message.chat.id, f"Ваше имя изменено на '{message.text}'.",
                     reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def send_text(message):
    bot.send_message(message.chat.id, "Вы неправильно ввели команду.",
                     reply_markup=keyboard)


if __name__ == "__main__":
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("оставить заявку на долг", "уведомить об оплате долга")
    keyboard.row("посмотреть сумму долга", "изменить имя")
    keyboard_back = types.ReplyKeyboardMarkup()
    keyboard_back.add("назад")
    bot.polling()
