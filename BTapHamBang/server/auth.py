USERS = {
    "admin": "password123",
    "client": "clientpass"
}

def authenticate(username, password):
    return USERS.get(username) == password