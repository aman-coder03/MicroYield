users = {}

def create_user(user_id: str):
    users[user_id] = {
        "savings": 0.0,
        "invested": 0.0,
        "public_key": None,
        "secret_key": None
    }

def get_user(user_id: str):
    return users.get(user_id)
