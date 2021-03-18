from db import *
from telebot import types
import telebot


BACK = "назад"
OWNER_ID = 287100650
bot = telebot.TeleBot("990303016:AAEQfd5PnZsjgitwo0HvcLVLMQty47JI_WU")

keyboard_user = types.ReplyKeyboardMarkup()
keyboard_user.row("оставить заявку на долг", "уведомить об оплате долга")
keyboard_user.row("посмотреть сумму долга", "изменить имя")
keyboard_back = types.ReplyKeyboardMarkup()
keyboard_back.add("назад")
keyboard_admin = types.ReplyKeyboardMarkup()
keyboard_admin.row("пользователи", "показать профиль")
keyboard_admin.row("ожидающие заявки", "подтвердить заявку")
keyboard_admin.row("общая сумма в долгах")


@bot.message_handler(commands=["start"])
def start_message(message):
    if message.from_user.id == OWNER_ID:
        bot.send_message(message.chat.id, f"С возвращением, НурБанк!")
        return

    user = get_user(message.from_user.id)
    if user:
        bot.send_message(message.chat.id, f"С возвращением в НурБанк, {user['username']}!")
        return

    user_info = {
        'user_id': message.from_user.id,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'username': message.from_user.username,
    }
    user = create_user(user_info)
    bot.send_message(message.chat.id, f"Приветствуем вас в НурБанке, {user['username']}!",
                     reply_markup=keyboard_user)

    bot.send_message(OWNER_ID,
                     f"Новый пользователь Нурбанка: {user['first_name']} '{user['username']}' {user['last_name']}",
                     reply_markup=keyboard_admin)


def validation_check(money_func):
    def wrapper(message):
        value = message.text
        if value == BACK:
            bot.send_message(message.chat.id, "Вы вернулись в меню",
                             reply_markup=keyboard_user)
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
        bot.send_message(message.chat.id, f"У вас слишком много ожидающих заявок. Дождитесь ответа на предыдущие.",
                         reply_markup=keyboard_user)
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
    bot.send_message(message.chat.id, f"Ваша заявка на получение долга в размере {value:,} отправлена на рассмотрение.",
                     reply_markup=keyboard_user)

    user = get_user(message.from_user.id)
    bot.send_message(OWNER_ID,
                     f"{user['first_name']} '{user['username']}' {user['last_name']} запросил(-а) в долг сумму {value:,}",
                     reply_markup=keyboard_admin)


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
                     reply_markup=keyboard_user)

    user = get_user(message.from_user.id)
    bot.send_message(OWNER_ID,
                     f"{user['first_name']} '{user['username']}' {user['last_name']} уменьшил(-а) сумму долга на {value:,}",
                     reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text == "посмотреть сумму долга")
def get_current_debt(message):
    user = get_user(message.from_user.id)
    if not user['debt']:
        bot.send_message(message.chat.id, "У вас нет активных долгов.",
                         reply_markup=keyboard_user)
    else:
        bot.send_message(message.chat.id, f"Сумма долга: {user['debt']:,}.",
                         reply_markup=keyboard_user)

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
        bot.send_message(message.chat.id, "Вы вернулись в меню", reply_markup=keyboard_user)
        return
    user_info = {'username': message.text}
    change_user(message.from_user.id, user_info)
    bot.send_message(message.chat.id, f"Ваше имя изменено на '{message.text}'.",
                     reply_markup=keyboard_user)


@bot.message_handler(content_types=["text"])
def send_text(message):
    bot.send_message(message.chat.id, "Вы неправильно ввели команду.",
                     reply_markup=keyboard_user)


if __name__ == "__main__":
    bot.polling()
