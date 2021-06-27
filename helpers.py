from datetime import datetime


def get_user_full_name(first_name: str, nickname: str, last_name: str, **_) -> str:
    return f"{first_name} '{nickname}' {last_name}"


def get_application_info(id: int, value: int, request_date: str, **_) -> str:
    return f"ID: {id}\n"\
           f"Сумма: {value:,}\n"\
           f"Дата: {request_date}"


def get_current_time() -> str:
    return datetime.now().strftime("%H:%M:%S - %d/%m/%Y")


def cut_command(command: str) -> int:
    return int(command[command.index("_") + 1:])


# MESSAGES
WRONG_COMMAND = "Вы неправильно ввели команду."
BACK = "/back - отмена"


# COMMANDS

# USER
USER_COMMANDS = '''
/loan - оставить заявку на долг
/payment - уведомить об оплате долга
/debt - посмотреть сумму долга
/name - изменить имя

/commands - список команд
'''

# ADMIN
ADMIN_COMMANDS = '''
/profiles - пользователи
/debtors - должники
/applications - ожидающие заявки
/count - общая сумма в долгах
/message - отправить сообщение
/remind - разослать напоминания

/commands - список команд
'''
