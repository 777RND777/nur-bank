from config import *
from db_requests import *
from helpers import *
from telebot import types
import telebot


bot = telebot.TeleBot(TELEGRAM_TOKEN)

keyboard_user = types.ReplyKeyboardMarkup()
keyboard_user.row("оставить заявку на долг", "уведомить об оплате долга")
keyboard_user.row("посмотреть сумму долга", "изменить имя")
keyboard_back = types.ReplyKeyboardMarkup()
keyboard_back.add(BACK)
keyboard_admin = types.ReplyKeyboardMarkup()
keyboard_admin.row("пользователи", "ожидающие заявки")
keyboard_admin.row("напомнить о долге", "общая сумма в долгах")


# DECORATORS


def admin_verification(admin_func):
    def wrapper(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            bot.send_message(message.from_user.id,
                             WRONG_COMMAND,
                             reply_markup=keyboard_admin)
            return
        admin_func(message)
    return wrapper


def back_check(some_func):
    def wrapper(message: types.Message, *args):
        if message.text == BACK:
            bot.send_message(message.chat.id,
                             "Вы вернулись в меню",
                             reply_markup=keyboard_user)
            return
        some_func(message, *args)
    return wrapper


def validation_check(money_func):
    @back_check
    def wrapper(message: types.Message, is_loan: bool):
        value = message.text
        if value.endswith("к") or value.endswith("k"):
            value = value[:-1] + "000"
        elif len(value) < 4 or not value.endswith("000"):
            value = value + "000"
        try:
            value = int(value)
        except ValueError:
            msg = bot.send_message(message.chat.id,
                                   "Вы неправильно ввели сумму.\n"
                                   "Попробуйте еще раз.\n"
                                   "Правильные примеры: '5000' / '5' / '5к'.",
                                   reply_markup=keyboard_back)
            bot.register_next_step_handler(msg, wrapper, is_loan)
            return
        if value > 5000000:
            msg = bot.send_message(message.chat.id,
                                   "Вы указали слишком большую сумму.\n"
                                   "Введите сумму поменьше.",
                                   reply_markup=keyboard_back)
            bot.register_next_step_handler(msg, wrapper, is_loan)
            return
        elif not value:  # value = 0
            msg = bot.send_message(message.chat.id,
                                   "Вы ввели нулевую сумму.\n"
                                   "Введите сумму больше нуля.",
                                   reply_markup=keyboard_back)
            bot.register_next_step_handler(msg, wrapper, is_loan)
            return
        elif value < 0:
            msg = bot.send_message(message.chat.id,
                                   "Вы ввели отрицательную сумму.\n"
                                   "Введите сумму больше нуля.",
                                   reply_markup=keyboard_back)
            bot.register_next_step_handler(msg, wrapper, is_loan)
            return
        money_func(message, value, is_loan)
    return wrapper


def user_check(user_func):
    def wrapper(message: types.Message):
        user_id = int(message.text[9:])
        user = get_user(user_id)
        if not user:
            bot.send_message(ADMIN_ID,
                             "Нет пользователя с таким ID.",
                             reply_markup=keyboard_admin)
            return
        user_func(user)
    return wrapper


def application_check(application_func):
    def wrapper(message: types.Message):
        application_id = int(message.text[9:])
        application = get_application(application_id)
        if not application:
            bot.send_message(ADMIN_ID,
                             "Нет заявки с таким ID.",
                             reply_markup=keyboard_admin)
            return
        if application['answer_date']:
            bot.send_message(ADMIN_ID,
                             "Вы уже ответили на данную заявку.",
                             reply_markup=keyboard_admin)
            return
        application_func(application)
    return wrapper


def user_register_check(user_func):
    def wrapper(message: types.Message):
        user = get_user(message.from_user.id)
        if not user:
            register_user(message)
        user_func(message)
    return wrapper


# USER


@bot.message_handler(func=lambda message: message.text == "оставить заявку на долг")
@user_register_check
def request_loan(message: types.Message):
    value = get_user_pending_loan_amount(message.from_user.id)
    if value == 3:
        bot.send_message(message.chat.id,
                         f"У вас слишком много ожидающих заявок. Дождитесь ответа на предыдущие.",
                         reply_markup=keyboard_user)
    else:
        msg = bot.send_message(message.chat.id,
                               "Какую сумму вы хотите взять в долг?",
                               reply_markup=keyboard_back)
        bot.register_next_step_handler(msg, make_request, True)


@bot.message_handler(func=lambda message: message.text == "уведомить об оплате долга")
@user_register_check
def notify_payment(message: types.Message):
    msg = bot.send_message(message.chat.id,
                           "Какую сумму из вашего долга вы оплатили?",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, make_request, False)


@validation_check
def make_request(message: types.Message, value: int, is_loan: bool):
    if is_loan:
        message_to_user = f"Ваша заявка на получение долга в размере {value:,} отправлена на рассмотрение."
        message_to_admin = "запросил(-а) в долг сумму"
    else:
        message_to_user = f"Ваше уведомление о совершении оплаты в размере {value:,} находится на проверке."
        message_to_admin = "уменьшил(-а) сумму долга на"
        value = -value

    application = {
        "user_id": message.from_user.id,
        "value": value,
        "request_date": get_current_time(),
    }
    application = create_application(application)
    bot.send_message(message.chat.id,
                     message_to_user,
                     reply_markup=keyboard_user)

    user = get_user(message.from_user.id)
    bot.send_message(ADMIN_ID,
                     f"{get_user_full_name(**user)} {message_to_admin} {value:,}\n"
                     f"Одобрить:  /approve_{application['id']}\n"
                     f"Отклонить: /decline_{application['id']}",
                     reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text == "посмотреть сумму долга")
@user_register_check
def get_current_debt(message: types.Message):
    user = get_user(message.from_user.id)
    if not user['debt']:
        bot.send_message(message.chat.id,
                         "У вас нет активных долгов.",
                         reply_markup=keyboard_user)
    else:
        bot.send_message(message.chat.id,
                         f"Сумма долга: {user['debt']:,}.",
                         reply_markup=keyboard_user)

    value = get_user_pending_loans(message.from_user.id)
    if value > 0:
        bot.send_message(message.chat.id,
                         f"Сумма в долг на рассмотрении: {value:,}.",
                         reply_markup=keyboard_user)

    value = get_user_pending_payments(message.from_user.id)
    if value > 0:
        bot.send_message(message.chat.id,
                         f"Оплаченная сумма на рассмотрении: {value:,}.",
                         reply_markup=keyboard_user)


@bot.message_handler(func=lambda message: message.text == "изменить имя")
@user_register_check
def change_username_handler(message: types.Message):
    msg = bot.send_message(message.chat.id,
                           "Как вы хотите, чтобы к вам обращались?\n"
                           f"Имя '{BACK}' не разрешено. Вы будете отправлены назад.",
                           reply_markup=keyboard_back)
    bot.register_next_step_handler(msg, change_username)


@back_check
def change_username(message: types.Message):
    info = {"username": message.text}
    change_user(message.from_user.id, info)
    bot.send_message(message.chat.id,
                     f"Ваше имя изменено на '{message.text}'.",
                     reply_markup=keyboard_user)


# ADMIN


@bot.message_handler(func=lambda message: message.text == "пользователи")
@admin_verification
def show_all_profiles(*args):
    users = get_all_users()
    if not users:
        bot.send_message(ADMIN_ID,
                         "На данный момент в базе данных нет пользователей.",
                         reply_markup=keyboard_admin)
        return
    for user in get_all_users():
        bot.send_message(ADMIN_ID,
                         f"Имя: {get_user_full_name(**user)}\n"
                         f"Профиль: /profile_{user['id']}",
                         reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text.startswith("/profile_"))
@admin_verification
@user_check
def show_profile(user: dict):
    application_history = ""
    for i, application in enumerate(user['applications'][::-1]):
        application_history += f"\n{get_application_info(**application)}\n"
        if i == 4:
            break
    bot.send_message(ADMIN_ID,
                     f"Имя: {get_user_full_name(**user)}\n"
                     f"ID: {user['id']}\n"
                     f"Долг: {user['debt']}\n"
                     f"Напомнить: /remind__{user['id']}\n\n"
                     f"Последние обращения: {application_history}",
                     reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text == "ожидающие заявки")
@admin_verification
def show_pending_applications(*args):
    users = get_all_users()
    found = False
    for user in users:
        for application in user['applications']:
            if not application['answer_date']:
                bot.send_message(ADMIN_ID,
                                 f"Заявитель: {get_user_full_name(**user)}\n"
                                 f"{get_application_info(**application)}\n"
                                 f"Одобрить:  /approve_{application['id']}\n"
                                 f"Отклонить: /decline_{application['id']}",
                                 reply_markup=keyboard_admin)
                found = True
    if not found:
        bot.send_message(ADMIN_ID,
                         "На данный момент в базе данных нет ожидающих заявок.",
                         reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text.startswith("/approve_"))
@admin_verification
@application_check
def approve_application(application: dict):
    info = {
        "approved": True,
        "answer_date": get_current_time(),
    }
    change_application(application['id'], info)
    bot.send_message(ADMIN_ID,
                     f"Вы одобрили заявку.",
                     reply_markup=keyboard_admin)

    user = get_user(application['user_id'])
    info = {"debt": user['debt'] + application['value']}
    change_user(user['id'], info)
    action = "получение" if application['value'] > 0 else "погашение"
    bot.send_message(user['id'],
                     f"Ваша заявка на {action} суммы в размере {abs(application['value']):,} одобрена.\n"
                     f"Ваш общий долг составляет {user['debt'] + application['value']:,}.",
                     reply_markup=keyboard_user)


@bot.message_handler(func=lambda message: message.text.startswith("/decline_"))
@admin_verification
@application_check
def decline_application(application: dict):
    info = {"answer_date": get_current_time()}
    change_application(application['id'], info)
    bot.send_message(ADMIN_ID,
                     f"Вы отклонили заявку.",
                     reply_markup=keyboard_admin)

    user = get_user(application['id'])
    action = "получение" if application['value'] > 0 else "погашение"
    bot.send_message(user['id'],
                     f"Ваша заявка на {action} суммы в размере {abs(application['value']):,} отклонена.\n"
                     f"Ваш общий долг составляет {user['debt']:,}.",
                     reply_markup=keyboard_user)


@bot.message_handler(func=lambda message: message.text == "напомнить о долге")
@admin_verification
def remind_all_users(*args):
    for user in get_all_users():
        send_remind(**user)
    bot.send_message(ADMIN_ID,
                     "Напоминания было отправлены",
                     reply_markup=keyboard_admin)


@bot.message_handler(func=lambda message: message.text.startswith("/remind__"))
@admin_verification
@user_check
def remind_user(user: dict):
    send_remind(**user)
    bot.send_message(ADMIN_ID,
                     "Напоминание было отправлено",
                     reply_markup=keyboard_admin)


def send_remind(user_id: int, debt: int, **kwargs):
    if debt > 0:
        bot.send_message(user_id,
                         f"Напоминание о долге!\n"
                         f"Ваш общий долг состовляет {debt:,}.",
                         reply_markup=keyboard_user)


@bot.message_handler(func=lambda message: message.text == "общая сумма в долгах")
@admin_verification
def count_debts(*args):
    value = 0
    for user in get_all_users():
        value += user['debt']
    bot.send_message(ADMIN_ID,
                     f"Общая сумма в долгах: {value:,}.",
                     reply_markup=keyboard_admin)


# COMMON


@bot.message_handler(commands=["start"])
def start_message(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id,
                         f"С возвращением, НурБанк!",
                         reply_markup=keyboard_admin)
        return

    user = get_user(message.from_user.id)
    if user:
        bot.send_message(message.chat.id,
                         f"С возвращением в НурБанк, {user['username']}!",
                         reply_markup=keyboard_user)
        return

    register_user(message)
    bot.send_message(message.chat.id,
                     f"Приветствуем вас в НурБанке, {message.from_user.username}!",
                     reply_markup=keyboard_user)


def register_user(message: types.Message):
    user_info = {
        "id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
    }
    user = create_user(user_info)
    bot.send_message(ADMIN_ID,
                     f"Новый пользователь Нурбанка: {get_user_full_name(**user)}",
                     reply_markup=keyboard_admin)


@bot.message_handler(content_types=["text"])
def send_text(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(ADMIN_ID,
                         WRONG_COMMAND,
                         reply_markup=keyboard_admin)
    else:
        bot.send_message(message.chat.id,
                         WRONG_COMMAND,
                         reply_markup=keyboard_user)


if __name__ == "__main__":
    bot.polling()
