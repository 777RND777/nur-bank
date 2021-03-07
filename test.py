from bank import client


user = {
    'user_id': 287100650,
    'first_name': 'Nurmukhanbet',
    'last_name': 'Rakhimbayev',
}

# c = client.post("users", json=user)
# print(c.get_json())
# c = client.put("users/287100650", json=user_update)
# print(c.get_json())
# c = client.delete("users/287100650")
# c = client.get("/users")
# print(c.get_json())
#
# exit()

application = {
    'user_id': 287100650,
    'value': 100,
}
c = client.post("/applications", json=application)
print(c.get_json())
# c = client.put("users/287100650", json=user_update)
# print(c.get_json())
c = client.get("/applications")
print(c.get_json())

