from datetime import datetime


def get_user_full_name(first_name: str, nickname: str, last_name: str, **kwargs) -> str:
    return f"{first_name} '{nickname}' {last_name}"


def get_application_info(id: int, value: int, request_date: str, **kwargs) -> str:
    return f"ID: {id}\n"\
           f"Сумма: {value:,}\n"\
           f"Дата: {request_date}"


def get_current_time() -> str:
    return datetime.now().strftime("%H:%M:%S - %d/%m/%Y")


# KEYBOARD BUTTONS

# USER
REQUEST_LOAN = "оставить заявку на долг"
NOTIFY_PAYMENT = "уведомить об оплате долга"
GET_CURRENT_DEBT = "посмотреть сумму долга"
CHANGE_NICKNAME = "изменить имя"

# ADMIN
SHOW_ALL_PROFILES = "пользователи"
SHOW_PENDING_APPLICATIONS = "ожидающие заявки"
REMIND_ALL_USERS = "напомнить о долге"
COUNT_DEBTS = "общая сумма в долгах"
