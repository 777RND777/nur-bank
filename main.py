from datetime import datetime
from db_requests import *
from telebot import types
import telebot


BACK = "назад"
WRONG_COMMAND = "Вы неправильно ввели команду."
ADMIN_ID = 287100650
bot = telebot.TeleBot("990303016:AAEQfd5PnZsjgitwo0HvcLVLMQty47JI_WU")

keyboard_user = types.ReplyKeyboardMarkup()
keyboard_user.row("оставить заявку на долг", "уведомить об оплате долга")
keyboard_user.row("посмотреть сумму долга", "изменить имя")
keyboard_back = types.ReplyKeyboardMarkup()
keyboard_back.add(BACK)
keyboard_admin = types.ReplyKeyboardMarkup()
keyboard_admin.row("пользователи", "показать профиль")
keyboard_admin.row("ожидающие заявки", "одобрить заявку")
keyboard_admin.row("общая сумма в долгах", "отклонить заявку")


def admin_verification(admin_func):
    def wrapper(message):
        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.from_user.id, WRONG_COMMAND)
            return
        admin_func()
    return wrapper


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


def get_user_full_name(first_name, username, last_name, **kwargs):
    return f"{first_name} '{username}' {last_name}"


def get_str_application_info(id, value, request_date, **kwargs):
    return f"ID: {id}\n"\
           f"Сумма: {value}\n"\
           f"Дата: {request_date}"


def get_current_time():
    return datetime.now().strftime("%H:%M:%S - %d/%m/%Y")


# USER


@bot.message_handler(func=lambda message: message.text == "оставить заявку на долг")
def make_loan_handler(message):
    value = get_user_pending_loan_amount(message.from_user.id)
    if value == 3:
        bot.send_message(message.chat.id, f"У вас слишком много ожидающих заявок. Дождитесь ответа на предыдущие.",
                         reply_markup=keyboard_user)
    else:
        msg = bot.send_message(message.chat.id, "Какую сумму вы хотите взять в долг?",
                               reply_markup=keyboard_back)
        bot.register_next_step_handler(msg, make_loan_request)


@validation_check
def make_loan_request(message, value):
    application = {
        'user_id': message.from_user.id,
        'value': value,
        "request_date": get_current_time(),
    }
    create_application(application)
    bot.send_message(message.chat.id, f"Ваша заявка на получение долга в размере {value:,} отправлена на рассмотрение.",
                     reply_markup=keyboard_user)

    user = get_user(message.from_user.id)
    bot.send_message(ADMIN_ID, f"{get_user_full_name(**user)} запросил(-а) в долг сумму {value:,}",
                     reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text == "уведомить об оплате долга")
def make_payment_handler(message):
    msg = bot.send_message(message.chat.id, "Какую сумму из вашего долга вы оплатили?",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, make_payment_notification)


@validation_check
def make_payment_notification(message, value):
    application = {
        'user_id': message.from_user.id,
        'value': -value,
        "request_date": get_current_time(),
    }
    create_application(application)
    bot.send_message(message.chat.id,
                     f"Ваше уведомление о совершении оплаты в размере {value:,} находится на проверке.",
                     reply_markup=keyboard_user)

    user = get_user(message.from_user.id)
    bot.send_message(ADMIN_ID, f"{get_user_full_name(**user)} уменьшил(-а) сумму долга на {value:,}",
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
def change_username_handler(message):
    msg = bot.send_message(message.chat.id, "Как вы хотите, чтобы к вам обращались?\n"
                                            f"Имя '{BACK}' не разрешено. Вы будете отправлены назад.",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, change_username)


def change_username(message):
    if message.text == BACK:
        bot.send_message(message.chat.id, "Вы вернулись в меню", reply_markup=keyboard_user)
        return
    info = {'username': message.text}
    change_user(message.from_user.id, info)
    bot.send_message(message.chat.id, f"Ваше имя изменено на '{message.text}'.",
                     reply_markup=keyboard_user)


# ADMIN


@bot.message_handler(func=lambda message: message.text == "пользователи")
@admin_verification
def show_all_profiles():
    users = get_all_users()
    if not users:
        bot.send_message(ADMIN_ID, "На данный момент в базе данных нет пользователей.",
                         reply_markup=keyboard_admin)
        return
    for user in get_all_users():
        info = f"Имя: {get_user_full_name(**user)}\n" \
               f"ID: {user['user_id']}"
        bot.send_message(ADMIN_ID, info,
                         reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text == "показать профиль")
@admin_verification
def show_profile_handler():
    msg = bot.send_message(ADMIN_ID, "Введите ID пользователя.",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, show_profile)


def show_profile(message):
    if message.text == BACK:
        bot.send_message(ADMIN_ID, "Вы вернулись в меню",
                         reply_markup=keyboard_admin)
        return
    try:
        user_id = int(message.text)
    except ValueError:
        bot.send_message(ADMIN_ID, "Нет пользователя с таким ID.",
                         reply_markup=keyboard_admin)
        return

    user = get_user(user_id)
    if not user:
        bot.send_message(ADMIN_ID, "Нет пользователя с таким ID.",
                         reply_markup=keyboard_admin)
        return
    application_history = ""
    for application in user["applications"]:
        application_history += f"\n{get_str_application_info(**application)}\n"
    bot.send_message(ADMIN_ID,
                     f"ID: {user['user_id']}\n"
                     f"Имя: {get_user_full_name(**user)}\n"
                     f"Долг: {user['debt']}\n\n"
                     f"История обращений: {application_history}",
                     reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text == "ожидающие заявки")
@admin_verification
def show_pending_applications():
    users = get_all_users()
    amount = 0
    for user in users:
        for application in user["applications"]:
            if not application["answer_date"]:
                bot.send_message(ADMIN_ID,
                                 f"Заявитель: {get_user_full_name(**user)}\n"
                                 f"{get_str_application_info(**application)}",
                                 reply_markup=keyboard_admin)
    if not amount:
        bot.send_message(ADMIN_ID, "На данный момент в базе данных нет ожидающих заявок.",
                         reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text == "одобрить заявку")
@admin_verification
def approve_application_handler():
    msg = bot.send_message(ADMIN_ID, "Введите ID одобренной заявки.",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, approve_application)


def approve_application(message):
    if message.text == BACK:
        bot.send_message(ADMIN_ID, "Вы вернулись в меню",
                         reply_markup=keyboard_admin)
        return
    try:
        application_id = int(message.text)
    except ValueError:
        bot.send_message(ADMIN_ID, "Нет заявки с таким ID.",
                         reply_markup=keyboard_admin)
        return

    application = get_application(application_id)
    if not application:
        bot.send_message(ADMIN_ID, "Нет заявки с таким ID.",
                         reply_markup=keyboard_admin)
        return
    if application["answer_date"]:
        bot.send_message(ADMIN_ID, "Вы уже ответили на данную заявку.",
                         reply_markup=keyboard_admin)
        return

    info = {
        'approved': True,
        "answer_date": get_current_time(),
    }
    change_application(info, info)
    bot.send_message(ADMIN_ID, f"Вы одобрили заявку.",
                     reply_markup=keyboard_admin)

    user = get_user(application["user_id"])
    info = {"debt": user["debt"] + application["value"]}
    change_user(user["user_id"], info)
    bot.send_message(user["user_id"],
                     f"Ваша заявка на получение суммы в размере {application['value']:,} одобрена.\n"
                     f"Ваш общий долг составляет {user['debt']:,}.",
                     reply_markup=keyboard_user)


@bot.message_handler(func=lambda message: message.text == "отклонить заявку")
@admin_verification
def decline_application_handler():
    msg = bot.send_message(ADMIN_ID, "Введите ID отклоненной заявки.",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, decline_application)


def decline_application(message):
    if message.text == BACK:
        bot.send_message(ADMIN_ID, "Вы вернулись в меню",
                         reply_markup=keyboard_admin)
        return
    try:
        application_id = int(message.text)
    except ValueError:
        bot.send_message(ADMIN_ID, "Нет заявки с таким ID.",
                         reply_markup=keyboard_admin)
        return

    application = get_application(application_id)
    if not application:
        bot.send_message(ADMIN_ID, "Нет заявки с таким ID.",
                         reply_markup=keyboard_admin)
        return
    if application["answer_date"]:
        bot.send_message(ADMIN_ID, "Вы уже ответили на данную заявку.",
                         reply_markup=keyboard_admin)
        return

    info = {"answer_date": get_current_time()}
    change_application(info, info)
    bot.send_message(ADMIN_ID, f"Вы отклонили заявку.",
                     reply_markup=keyboard_admin)

    user = get_user(application["user_id"])
    bot.send_message(user["user_id"],
                     f"Ваша заявка на получение суммы в размере {application['value']:,} отклонена.\n"
                     f"Ваш общий долг составляет {user['debt']:,}.",
                     reply_markup=keyboard_user)


@bot.message_handler(func=lambda message: message.text == "общая сумма в долгах")
@admin_verification
def count_all_debts():
    value = 0
    for user in get_all_users():
        value += user["debt"]
    bot.send_message(ADMIN_ID, f"{value:,}",
                     reply_markup=keyboard_admin)


# COMMON


@bot.message_handler(commands=["start"])
def start_message(message):
    if message.from_user.id == ADMIN_ID:
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

    bot.send_message(ADMIN_ID,
                     f"Новый пользователь Нурбанка: {get_user_full_name(**user)}",
                     reply_markup=keyboard_admin)


@bot.message_handler(content_types=["text"])
def send_text(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(ADMIN_ID, WRONG_COMMAND,
                         reply_markup=keyboard_admin)
    else:
        bot.send_message(message.chat.id, WRONG_COMMAND,
                         reply_markup=keyboard_user)


if __name__ == "__main__":
    bot.polling()
