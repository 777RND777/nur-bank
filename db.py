from openpyxl import load_workbook


class User:
    def __init__(self, id_number, first_name, last_name, username, debt, check, approve):
        self.id = id_number
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.debt = debt
        self.check = check
        self.approve = approve


wb = load_workbook('./DB.xlsx')
sheet = wb.get_sheet_by_name('Sheet1')
users = []
i = 2
while sheet["B" + str(i)].value:
    user = User(
        sheet["B" + str(i)].value,
        sheet["C" + str(i)].value,
        sheet["D" + str(i)].value,
        sheet["E" + str(i)].value,
        sheet["F" + str(i)].value,
        sheet["G" + str(i)].value,
        sheet["H" + str(i)].value,
    )
    users.append(user)
    i += 1
