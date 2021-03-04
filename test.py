from server import client


user = {
    'user_id': 287100650,
    'first_name': 'Nurmukhanbet',
    'last_name': 'Rakhimbayev',
}
update = {
    "requested": 0,
}


# c = client.post("users", json=user)
# print(c.get_json())
c = client.put("users/1", json=update)
print(c.get_json())
# c = client.delete("users/1")


c = client.get("users")
print(c.get_json())
