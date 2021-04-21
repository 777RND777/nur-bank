from bank import client
# TODO logger


def get_all_users() -> dict:
    c = client.get("/users")
    return c.get_json()


def get_user(user_id: int) -> dict:
    c = client.get(f"/users/{user_id}")
    return c.get_json()


def create_user(user: dict) -> dict:
    for key, value in user.items():
        if not value:
            user[key] = ""
    c = client.post("/users", json=user)
    return c.get_json()


def change_user(user_id: int, json: dict):
    _ = client.put(f"/users/{user_id}", json=json)


def get_all_applications() -> dict:
    c = client.get(f"/applications")
    return c.get_json()


def get_application(application_id: int) -> dict:
    c = client.get(f"/applications/{application_id}")
    return c.get_json()


def create_application(json: dict) -> dict:
    c = client.post("/applications", json=json)
    return c.get_json()


def change_application(application_id: int, json: dict):
    _ = client.put(f"/applications/{application_id}", json=json)


def get_user_pending_loans(user_id: int) -> int:
    c = client.get(f"/users/{user_id}")
    value = 0
    for application in c.get_json()["applications"]:
        if application["value"] > 0 and not application["answer_date"]:
            value += application["value"]
    return value


def get_user_pending_payments(user_id: int) -> int:
    c = client.get(f"/users/{user_id}")
    value = 0
    for application in c.get_json()["applications"]:
        if application["value"] < 0 and not application["answer_date"]:
            value -= application["value"]
    return value


def get_user_pending_loan_amount(user_id: int) -> int:
    c = client.get(f"/users/{user_id}")
    amount = 0
    for application in c.get_json()["applications"]:
        if application["value"] > 0 and not application["answer_date"]:
            amount += 1
    return amount
