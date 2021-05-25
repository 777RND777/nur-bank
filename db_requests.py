from bank import client
from random import randint
# TODO logger


def get_all_users() -> dict:
    c = client.get("/users")
    return c.get_json()


def get_user(user_id: int) -> dict:
    c = client.get(f"/users/{user_id}")
    return c.get_json()


def create_user(info: dict) -> dict:
    for key, value in info.items():
        if not value:
            info[key] = ""
    c = client.post("/users", json=info)
    return c.get_json()


def change_user(user_id: int, info: dict):
    _ = client.put(f"/users/{user_id}", json=info)


def get_all_applications() -> dict:
    c = client.get(f"/applications")
    return c.get_json()


def get_application(application_id: int) -> dict:
    c = client.get(f"/applications/{application_id}")
    return c.get_json()


def create_application(info: dict) -> dict:
    info['id'] = randint(100000000, 999999999)
    while get_application(info['id']):  # do while there is an application with the same id
        info['id'] = randint(100000000, 999999999)
    c = client.post("/applications", json=info)
    return c.get_json()


def change_application(application_id: int, info: dict):
    _ = client.put(f"/applications/{application_id}", json=info)


def get_user_pending_loans(user_id: int) -> int:
    c = client.get(f"/users/{user_id}")
    value = 0
    for application in c.get_json()['applications']:
        if application['value'] > 0 and not application['answer_date']:
            value += application['value']
    return value


def get_user_pending_payments(user_id: int) -> int:
    c = client.get(f"/users/{user_id}")
    value = 0
    for application in c.get_json()['applications']:
        if application['value'] < 0 and not application['answer_date']:
            value -= application['value']
    return value


def get_user_pending_loan_amount(user_id: int) -> int:
    c = client.get(f"/users/{user_id}")
    amount = 0
    for application in c.get_json()['applications']:
        if application['value'] > 0 and not application['answer_date']:
            amount += 1
    return amount
