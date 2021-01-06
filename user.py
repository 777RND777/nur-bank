from db import *


class User:
    def __init__(self, id_number, first, last, username, debt, requested, approving):
        self.id = id_number
        self.first = first
        self.last = last
        self.username = username
        self.debt = debt
        self.requested = requested
        self.approving = approving

    def set_username(self, text):
        self.username = text
        change_value(self, "username", self.username)

    def make_request(self, text):
        self.requested += amount_converter(text)
        change_value(self, "requested", self.requested)

    def make_payment(self, text):
        self.approving += amount_converter(text)
        change_value(self, "approving", self.approving)


def amount_converter(amount):
    if amount.endswith("000"):
        return float(amount) / 1000
    return float(amount)


def get_users():
    users = []
    info = get_info()
    for i in info:
        users.append(User(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))
    return users


def get_person(message):
    for user in get_users():
        if user.id == message.from_user.id:
            return user

    person = User(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.last_name,
        message.from_user.username,
        0, 0, 0
    )
    add_user(person)
    return person
