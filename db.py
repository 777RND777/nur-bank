import sqlite3


def create_table():
    c.execute("""CREATE TABLE users (
                 id integer,
                 first text,
                 last text,
                 username text,
                 debt double,
                 requested double,
                 approving double
                 )""")
    with conn:
        c.execute("INSERT INTO users VALUES (:id, :first, :last, :username, :debt, :requested, :approving)",
                  {'id': 830667168, 'first': "first1", 'last': "last1", 'username': "username1",
                   'debt': 265, 'requested': 0, 'approving': 0})
        c.execute("INSERT INTO users VALUES (:id, :first, :last, :username, :debt, :requested, :approving)",
                  {'id': 294728712, 'first': "first2", 'last': "last2", 'username': "username2",
                   'debt': 50, 'requested': 0, 'approving': 0})


def add_user(user):
    with conn:
        c.execute("INSERT INTO users VALUES (:id, :first, :last, :username, :debt, :requested, :approving)",
                  {'id': user.id, 'first': user.first, 'last': user.last, 'username': user.username,
                   'debt': user.debt, 'requested': user.requested, 'approving': user.approving})


def get_info():
    with conn:
        c.execute("SELECT * FROM users")
        return c.fetchall()


def change_value(user, prop, value):
    with conn:
        c.execute(f"""UPDATE users SET {prop} = :value
                      WHERE id = :id""",
                  {'id': user.id, 'value': value})


def accept_request(user):
    with conn:
        c.execute("""UPDATE users SET debt = :debt, requested = :requested
                     WHERE id = :id""",
                  {'id': user.id, 'debt': user.debt + user.requested, 'requested': 0.0})


def approve_payment(user):
    with conn:
        c.execute("""UPDATE users SET debt = :approving, approving = :approving
                     WHERE id = :id""",
                  {'id': user.id, 'debt': user.debt - user.approving, 'approving': 0.0})


name = 'users.db'
conn = sqlite3.connect(name, check_same_thread=False)
c = conn.cursor()
