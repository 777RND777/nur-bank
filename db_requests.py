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


def update_user(user_id: int, info: dict):
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


def update_application(application_id: int, info: dict):
    _ = client.put(f"/applications/{application_id}", json=info)


def remove_application(application_id: int):
    client.delete(f"/applications/{application_id}")


def get_pending_application(user_id: int) -> dict:
    c = client.get(f"/users/{user_id}")
    for application in c.get_json()['applications']:
        if not application['answer_date']:
            return application
    return {}


def get_pending_value(user_id: int) -> int:
    c = client.get(f"/users/{user_id}")
    for application in c.get_json()['applications']:
        if not application['answer_date']:
            return application['value']
    return 0
