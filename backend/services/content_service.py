content_store = {
    "report1": {
        "title": "APAC Fintech Report",
        "price": 1.0,
        "unlocked_users": []
    },
    "course1": {
        "title": "Crypto Basics Course",
        "price": 1.5,
        "unlocked_users": []
    }
}

def list_content():
    return content_store

def unlock_content(user_id, content_id):
    content_store[content_id]["unlocked_users"].append(user_id)
