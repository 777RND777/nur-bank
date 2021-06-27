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
BACK = "назад"
WRONG_COMMAND = "Вы неправильно ввели команду."


# KEYBOARD BUTTONS

# USER
LOAN_APPLICATION = "оставить заявку на долг"
PAYMENT_APPLICATION = "уведомить об оплате долга"
GET_CURRENT_DEBT = "посмотреть сумму долга"
CHANGE_NICKNAME = "изменить имя"

# ADMIN
ADMIN_COMMANDS = '''
/profiles - пользователи
/applications - ожидающие заявки
/remind - напомнить о долге
/count - общая сумма в долгах

/commands - список команд
'''
