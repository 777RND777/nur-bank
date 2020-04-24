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

    def set_username(self, text):
        self.username = text
        sheet["E" + str(self.number+1)].value = self.username
        wb.save('./DB.xlsx')

    def make_request(self, text):
        self.requested += amount_converter(text)
        sheet["G" + str(self.number + 1)].value = self.requested
        wb.save('./DB.xlsx')

    def make_payment(self, text):
        self.approving += amount_converter(text)
        sheet["G" + str(self.number+1)].value = self.approving
        wb.save('./DB.xlsx')


def amount_converter(amount):
    if amount.endswith("000"):
        return float(amount) / 1000
    return float(amount)


wb = load_workbook('./DB.xlsx')
sheet = wb.get_sheet_by_name('Sheet1')
users = []
i = 2
while sheet["B" + str(i)].value:
    user = User(
        sheet["A" + str(i)].value,
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
