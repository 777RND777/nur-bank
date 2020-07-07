from openpyxl import load_workbook


class User:
    def __init__(self, number, id_number, first_name, last_name, username, debt, requested, approving):
        self.number = number
        self.id = id_number
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.debt = debt
        self.requested = requested
        self.approving = approving

    def add_to_db(self):
        sheet["A" + str(len(users) + 1)] = self.number
        sheet["B" + str(len(users) + 1)] = self.id
        sheet["C" + str(len(users) + 1)] = self.first_name
        sheet["D" + str(len(users) + 1)] = self.last_name
        sheet["E" + str(len(users) + 1)] = self.username
        sheet["F" + str(len(users) + 1)] = self.debt
        sheet["G" + str(len(users) + 1)] = self.requested
        sheet["H" + str(len(users) + 1)] = self.approving
        wb.save(name)

    def set_username(self, text):
        self.username = text
        sheet["E" + str(self.number+1)].value = self.username
        wb.save(name)

    def make_request(self, text):
        self.requested += amount_converter(text)
        sheet["G" + str(self.number + 1)].value = self.requested
        wb.save(name)

    def make_payment(self, text):
        self.approving += amount_converter(text)
        sheet["H" + str(self.number+1)].value = self.approving
        wb.save(name)


def amount_converter(amount):
    if amount.endswith("000"):
        return float(amount) / 1000
    return float(amount)


name = './DB.xlsx'
wb = load_workbook(name)
sheet = wb.get_sheet_by_name('Sheet1')
users = []
i = 2
while sheet["B" + str(i)].value:
    user = User(
        int(sheet["A" + str(i)].value),
        sheet["B" + str(i)].value,
        sheet["C" + str(i)].value,
        sheet["D" + str(i)].value,
        sheet["E" + str(i)].value,
        sheet["F" + str(i)].value,
        sheet["G" + str(i)].value,
        sheet["H" + str(i)].value
    )
    users.append(user)
    i += 1
