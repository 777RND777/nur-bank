from config import *
from telebot import types
import db_requests as db
import helpers as h
import telebot


bot = telebot.TeleBot(TELEGRAM_TOKEN)


# DECORATORS


def back_check(some_func):
    def wrapper(message: types.Message, *args):
        if message.text == "/back":
            bot.send_message(message.from_user.id,
                             "Вы вернулись в меню")
            return
        some_func(message, *args)
    return wrapper


def has_active_application(application_func):
    def wrapper(message: types.Message):
        if application := db.get_pending_application(message.from_user.id):
            bot.send_message(message.from_user.id,
                             f"У вас уже есть активная заявка. Дождитесь ответа на неё.\n"
                             f"Сумма: {abs(application['value']):,}\n"
                             f"Дата: {application['request_date']}\n"
                             f"Отмена заявки: /cancel")
            return
        application_func(message)
    return wrapper


def user_register_check(user_func):
    def wrapper(message: types.Message):
        user = db.get_user(message.from_user.id)
        if not user:
            register_user(message)
        elif user['username'] != message.from_user.username:
            info = {"username": message.from_user.username}
            db.update_user(message.from_user.id, info)
        user_func(message)
    return wrapper


def user_validation_check(money_func):
    @admin_validation_check
    def wrapper(user_id: int, value: int, is_loan: bool):
        if value < 0:
            msg = bot.send_message(user_id,
                                   "Вы ввели отрицательную сумму.\n"
                                   "Введите сумму больше нуля.\n"
                                   "{h.BACK")
            bot.register_next_step_handler(msg, wrapper, is_loan)
            return
        elif not is_loan:
            user = db.get_user(user_id)
            if user['debt'] < value:
                msg = bot.send_message(user_id,
                                       "Вы указали сумму, превышающую ваш нынешний долг.\n"
                                       "Введите сумму поменьше.\n"
                                       f"Ваш долг: {user['debt']}\n"
                                       f"{h.BACK}")
                bot.register_next_step_handler(msg, wrapper, is_loan)
                return
        money_func(user_id, value, is_loan)
    return wrapper


def admin_verification(admin_func):
    def wrapper(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            send_text(message)
            return
        admin_func(message)
    return wrapper


def admin_validation_check(money_func):
    @back_check
    def wrapper(message: types.Message, *args):
        value = message.text
        if value.endswith("к") or value.endswith("k"):
            value = value[:-1] + "000"
        elif len(value) < 4 or not value.endswith("000"):
            value = value + "000"
        try:
            value = int(value)
        except ValueError:
            msg = bot.send_message(message.from_user.id,
                                   "Вы неправильно ввели сумму.\n"
                                   "Попробуйте еще раз.\n"
                                   "Правильные примеры: '5000' / '5' / '5к'.\n"
                                   "{h.BACK")
            bot.register_next_step_handler(msg, wrapper, *args)
            return
        if value > 5000000:
            msg = bot.send_message(message.from_user.id,
                                   "Вы указали слишком большую сумму.\n"
                                   "Введите сумму поменьше.\n"
                                   "{h.BACK")
            bot.register_next_step_handler(msg, wrapper, *args)
            return
        elif not value:  # value = 0
            msg = bot.send_message(message.from_user.id,
                                   "Вы ввели нулевую сумму.\n"
                                   "Введите сумму больше нуля.\n"
                                   "{h.BACK")
            bot.register_next_step_handler(msg, wrapper, *args)
            return
        money_func(message.from_user.id, value, *args)
    return wrapper


def admin_user_id_check(user_func):
    def wrapper(message: types.Message):
        user_id = h.cut_command(message.text)
        user = db.get_user(user_id)
        if not user:
            bot.send_message(ADMIN_ID,
                             "Нет пользователя с таким ID.")
            return
        user_func(user)
    return wrapper


def admin_application_id_check(application_func):
    def wrapper(message: types.Message):
        application_id = h.cut_command(message.text)
        application = db.get_application(application_id)
        if not application:
            bot.send_message(ADMIN_ID,
                             "Нет заявки с таким ID.")
            return
        if application['answer_date']:
            bot.send_message(ADMIN_ID,
                             "Вы уже ответили на данную заявку.")
            return
        application_func(application)
    return wrapper


# USER


@bot.message_handler(commands=["loan"])
@user_register_check
@has_active_application
def loan_application(message: types.Message):
    msg = bot.send_message(message.from_user.id,
                           "Какую сумму вы хотите взять в долг?\n"
                           "{h.BACK")
    bot.register_next_step_handler(msg, make_request, True)


@bot.message_handler(commands=["payment"])
@user_register_check
@has_active_application
def payment_application(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user['debt']:
        bot.send_message(message.from_user.id,
                         "У вас нет активных долгов.")
        return
    msg = bot.send_message(message.from_user.id,
                           "Какую сумму из вашего долга вы оплатили?\n"
                           "{h.BACK")
    bot.register_next_step_handler(msg, make_request, False)


@user_validation_check
def make_request(user_id: int, value: int, is_loan: bool):
    if is_loan:
        message_to_user = f"Ваша заявка на получение долга в размере {value:,} отправлена на рассмотрение."
        message_to_admin = "запросил(-а) в долг сумму"
    else:
        message_to_user = f"Ваше уведомление о совершении оплаты в размере {value:,} находится на проверке."
        message_to_admin = "уменьшил(-а) сумму долга на"
        value = -value

    info = {
        "user_id": user_id,
        "value": value,
        "request_date": h.get_current_time(),
        "is_admin": False,
    }
    application = db.create_application(info)
    bot.send_message(user_id,
                     f"{message_to_user}\n"
                     f"Отмена заявки: /cancel")

    user = db.get_user(user_id)
    bot.send_message(ADMIN_ID,
                     f"{h.get_user_full_name(**user)} {message_to_admin} {abs(value):,}\n"
                     f"Одобрить:  /approve_{application['id']}\n"
                     f"Отклонить: /decline_{application['id']}")


@bot.message_handler(commands=["cancel"])
@user_register_check
def cancel_application(message: types.Message):
    application = db.get_pending_application(message.from_user.id)
    if not application:
        bot.send_message(message.from_user.id,
                         "У вас сейчас нет активной заявки.\n"
                         "Заявку, на которую уже ответили, нельзя отменить.")
        return
    db.remove_application(application['id'])
    bot.send_message(application['user_id'],
                     f"Заявка была отменена.")


@bot.message_handler(commands=["debt"])
@user_register_check
def get_current_debt(message: types.Message):
    user = db.get_user(message.from_user.id)
    if not user['debt']:
        bot.send_message(message.from_user.id,
                         "У вас нет активных долгов.")
    else:
        bot.send_message(message.from_user.id,
                         f"Сумма долга: {user['debt']:,}.")

    value = db.get_pending_value(message.from_user.id)
    if value:
        application_status = "Сумма в долг" if value > 0 else "Оплаченная сумма"
        bot.send_message(message.from_user.id,
                         f"{application_status} на рассмотрении: {abs(value):,}.")


@bot.message_handler(commands=["name"])
@user_register_check
def change_nickname_handler(message: types.Message):
    msg = bot.send_message(message.from_user.id,
                           "Как вы хотите, чтобы к вам обращались?\n"
                           f"{h.BACK}")
    bot.register_next_step_handler(msg, change_nickname)


@back_check
def change_nickname(message: types.Message):
    info = {"nickname": message.text}
    db.update_user(message.from_user.id, info)
    bot.send_message(message.from_user.id,
                     f"Ваше имя изменено на '{message.text}'.")


# ADMIN


@bot.message_handler(commands=["profiles"])
@admin_verification
def show_all_profiles(*_):
    users = db.get_all_users()
    profiles = ""
    for user in users:
        profiles += f"Имя: {h.get_user_full_name(**user)}\n"\
                    f"Профиль: /profile_{user['id']}\n\n"
    if not profiles:
        profiles = "На данный момент в базе данных нет пользователей."
    bot.send_message(ADMIN_ID,
                     profiles)


@bot.message_handler(commands=["applications"])
@admin_verification
def show_pending_applications(*_):
    users = db.get_all_users()
    pending_applications = ""
    for user in users:
        for application in user['applications']:
            if not application['answer_date']:
                pending_applications += f"Заявитель: {h.get_user_full_name(**user)}\n"\
                                        f"{h.get_application_info(**application)}\n" \
                                        f"Одобрить:  /approve_{application['id']}\n" \
                                        f"Отклонить: /decline_{application['id']}\n\n"
    if not pending_applications:
        pending_applications = "На данный момент в базе данных нет ожидающих заявок."
    bot.send_message(ADMIN_ID,
                     pending_applications)


@bot.message_handler(commands=["remind"])
@admin_verification
def remind_all_users(*_):
    for user in db.get_all_users():
        send_remind(**user)
    bot.send_message(ADMIN_ID,
                     "Напоминания было отправлены")


@bot.message_handler(commands=["count"])
@admin_verification
def count_debts(*_):
    value = 0
    for user in db.get_all_users():
        value += user['debt']
    bot.send_message(ADMIN_ID,
                     f"Общая сумма в долгах: {value:,}.")


@bot.message_handler(func=lambda message: message.text.startswith("/profile_"))
@admin_verification
@admin_user_id_check
def show_profile(user: dict):
    bot.send_message(ADMIN_ID,
                     f"@{user['username']}\n"
                     f"Имя: {h.get_user_full_name(**user)}\n"
                     f"ID: {user['id']}\n"
                     f"Долг: {user['debt']:,}\n"
                     f"Изменить долг: /debt_{user['id']}\n"
                     f"Напомнить: /remind_{user['id']}\n"
                     f"Заявки: /app_{user['id']}")


@bot.message_handler(func=lambda message: message.text.startswith("/debt_"))
@admin_verification
@admin_user_id_check
def change_debt_handler(user: dict):
    msg = bot.send_message(ADMIN_ID,
                           f"На какую сумму вы хотите изменить долг {h.get_user_full_name(**user)}?\n"
                           f"Его нынешний долг составляет {user['debt']:,}\n"
                           f"{h.BACK}")
    bot.register_next_step_handler(msg, change_debt, user)


@admin_validation_check
def change_debt(_: types.Message, value: int, user: dict):
    new_value = user['debt'] + value
    action = "увеличен" if value > 0 else "уменьшен"
    current_time = h.get_current_time()

    info = {
        "user_id": user['id'],
        "value": value,
        "request_date": current_time,
        "answer_date": current_time,
        "approved": True,
        "is_admin": True,
    }
    _ = db.create_application(info)
    bot.send_message(ADMIN_ID,
                     f"Долг пользователя {h.get_user_full_name(**user)} был {action} на {abs(value):,}.\n"
                     f"Его нынешний долг составляет {new_value:,}")

    info = {"debt": new_value}
    db.update_user(user['id'], info)
    bot.send_message(user['id'],
                     f"Ваш долг был {action} администратором на {abs(value):,}.\n"
                     f"Новая сумма вашего долга составляет {new_value:,}")


@bot.message_handler(func=lambda message: message.text.startswith("/app_"))
@admin_verification
@admin_user_id_check
def show_last_applications(user: dict):
    application_history = ""
    count = 0
    for application in user['applications'][::-1]:
        if count == 3:
            break
        if application['approved']:
            application_history += f"{h.get_application_info(**application)}\n\n"
            count += 1
    if not application_history:
        application_history = f"Пользователь не оставлял заявки."

    bot.send_message(ADMIN_ID,
                     f"Последние заявки {h.get_user_full_name(**user)}:\n"
                     f"{application_history}")


@bot.message_handler(func=lambda message: message.text.startswith("/approve_"))
@admin_verification
@admin_application_id_check
def approve_application(application: dict):
    info = {
        "answer_date": h.get_current_time(),
        "approved": True,
    }
    db.update_application(application['id'], info)
    bot.send_message(ADMIN_ID,
                     f"Вы одобрили заявку.")

    user = db.get_user(application['user_id'])
    info = {"debt": user['debt'] + application['value']}
    db.update_user(user['id'], info)
    action = "получение" if application['value'] > 0 else "погашение"
    bot.send_message(user['id'],
                     f"Ваша заявка на {action} суммы в размере {abs(application['value']):,} одобрена.\n"
                     f"Ваш общий долг составляет {user['debt'] + application['value']:,}.")


@bot.message_handler(func=lambda message: message.text.startswith("/decline_"))
@admin_verification
@admin_application_id_check
def decline_application(application: dict):
    info = {"answer_date": h.get_current_time()}
    db.update_application(application['id'], info)
    bot.send_message(ADMIN_ID,
                     f"Вы отклонили заявку.")

    user = db.get_user(application['user_id'])
    action = "получение" if application['value'] > 0 else "погашение"
    bot.send_message(user['id'],
                     f"Ваша заявка на {action} суммы в размере {abs(application['value']):,} отклонена.\n"
                     f"Ваш общий долг составляет {user['debt']:,}.")


@bot.message_handler(func=lambda message: message.text.startswith("/remind_"))
@admin_verification
@admin_user_id_check
def remind_user(user: dict):
    send_remind(**user)
    bot.send_message(ADMIN_ID,
                     "Напоминание было отправлено")


def send_remind(id: int, debt: int, **_):
    if debt:
        bot.send_message(id,
                         f"Напоминание о долге!\n"
                         f"Ваш общий долг состовляет {debt:,}.")


# COMMON


@bot.message_handler(commands=["start"])
def start_message(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.from_user.id,
                         f"С возвращением, НурБанк!")
        show_commands(message)
        return

    user = db.get_user(message.from_user.id)
    if user:
        bot.send_message(message.from_user.id,
                         f"С возвращением в НурБанк, {user['nickname']}!")
        show_commands(message)
        return

    register_user(message)
    bot.send_message(message.from_user.id,
                     f"Приветствуем вас в НурБанке, {message.from_user.username}!")
    show_commands(message)


@bot.message_handler(commands=["commands"])
def show_commands(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.from_user.id,
                         h.ADMIN_COMMANDS)
        return
    bot.send_message(message.from_user.id,
                     h.USER_COMMANDS)


def register_user(message: types.Message):
    info = {
        "id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
    }
    user = db.create_user(info)
    bot.send_message(ADMIN_ID,
                     f"Новый пользователь Нурбанка: {h.get_user_full_name(**user)}"
                     f"Просмотр профиля: /profile_{message.from_user.id}")


@bot.message_handler(content_types=["text"])
def send_text(message: types.Message):
    bot.send_message(message.from_user.id,
                     h.WRONG_COMMAND)


if __name__ == "__main__":
    bot.polling()
