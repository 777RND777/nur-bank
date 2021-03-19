from bank import client
# TODO logger


def get_all_users():
    c = client.get("/users")
    return c.get_json()


def get_user(user_id):
    c = client.get(f"/users/{user_id}")
    return c.get_json()


def create_user(user):
    for key, value in user.items():
        if not value:
            user[key] = ""
    c = client.post("/users", json=user)
    return c.get_json()


def change_user(user_id, json):
    _ = client.put(f"/users/{user_id}", json=json)


def get_all_applications():
    c = client.get(f"/applications")
    return c.get_json()


def get_application(application_id):
    c = client.get(f"/applications/{application_id}")
    return c.get_json()


def create_application(json):
    _ = client.post("/applications", json=json)


def change_application(application_id, json):
    _ = client.put(f"/applications/{application_id}", json=json)


def get_user_pending_loans(user_id):
    c = client.get(f"/users/{user_id}")
    value = 0
    for application in c.get_json()["applications"]:
        if application["value"] > 0 and not application["answer_date"]:
            value += application["value"]
    return value


def get_user_pending_payments(user_id):
    c = client.get(f"/users/{user_id}")
    value = 0
    for application in c.get_json()["applications"]:
        if application["value"] < 0 and not application["answer_date"]:
            value -= application["value"]
    return value


def get_user_pending_loan_amount(user_id):
    c = client.get(f"/users/{user_id}")
    amount = 0
    for application in c.get_json()["applications"]:
        if application["value"] > 0 and not application["answer_date"]:
            amount += 1
    return amount
