from bank import client
# TODO error log
# TODO answer message
# TODO move to main


def get_all_users():
    c = client.get("users")
    return c.get_json()


def get_user(user_id: int):
    c = client.get(f"users/{user_id}")
    return c.get_json()


def add_user(user):
    c = client.post("users", json=user)
    return c.get_json()


def change_user(user_id: int, json: dict):
    c = client.put(f"users/{user_id}", json=json)
    return c.get_json()
