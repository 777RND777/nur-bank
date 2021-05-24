from datetime import datetime


def get_user_full_name(first_name: str, username: str, last_name: str, **kwargs) -> str:
    return f"{first_name} '{username}' {last_name}"


def get_application_info(id: int, value: int, request_date: str, **kwargs) -> str:
    return f"ID: {id}\n"\
           f"Сумма: {value:,}\n"\
           f"Дата: {request_date}"


def get_current_time() -> str:
    return datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
