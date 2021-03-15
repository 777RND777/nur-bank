from bank import client
# TODO error log
# TODO maybe move to main


def get_all_users():
    c = client.get("users")
    return c.get_json()


def get_user(user_id: int):
    c = client.get(f"users/{user_id}")
    return c.get_json()


def create_user(user: dict):
    c = client.post("users", json=user)
    return c.get_json()


def change_user(user_id: int, json: dict):
    _ = client.put(f"users/{user_id}", json=json)


def create_application(json: dict):
    _ = client.post("applications", json=json)


def get_user_pending_loans(user_id):
    c = client.get(f"users/{user_id}")
    value = 0
    for application in c.get_json()["applications"]:
        if application["value"] > 0 and not application["approved"]:
            value += application["value"]
    return value


def get_user_pending_payments(user_id):
    c = client.get(f"users/{user_id}")
    value = 0
    for application in c.get_json()["applications"]:
        if application["value"] < 0 and not application["approved"]:
            value -= application["value"]
    return value


def get_user_pending_loan_amount(user_id):
    c = client.get(f"users/{user_id}")
    amount = 0
    for application in c.get_json()["applications"]:
        if application["value"] > 0 and not application["approved"]:
            amount += 1
    return amount
