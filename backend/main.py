from fastapi import FastAPI
from models import create_user, get_user
from services.savings import calculate_spare_change
from services.yield_engine import generate_daily_yield
from services.stellar_service import create_wallet, send_payment
from services.content_service import list_content, unlock_content

app = FastAPI()

@app.post("/login/{user_id}")
def login(user_id: str):
    create_user(user_id)
    public, secret = create_wallet()

    user = get_user(user_id)
    user["public_key"] = public
    user["secret_key"] = secret

    return {"public_key": public}


@app.post("/save/{user_id}")
def save(user_id: str, amount: float):
    user = get_user(user_id)
    spare = calculate_spare_change(amount)
    user["savings"] += spare

    return {
        "saved": spare,
        "total_savings": user["savings"]
    }


@app.post("/invest/{user_id}")
def invest(user_id: str):
    user = get_user(user_id)

    tx_hash = send_payment(
        user["secret_key"],
        user["public_key"],
        "1"
    )

    user["invested"] += user["savings"]
    user["savings"] = 0

    return {
        "tx_hash": tx_hash,
        "invested": user["invested"]
    }


@app.post("/yield/{user_id}")
def yield_gain(user_id: str):
    user = get_user(user_id)
    earned = generate_daily_yield(user["invested"])
    user["invested"] += earned

    return {
        "earned_today": earned,
        "new_balance": user["invested"]
    }


@app.get("/content")
def content():
    return list_content()


@app.post("/purchase/{user_id}/{content_id}")
def purchase(user_id: str, content_id: str):
    user = get_user(user_id)
    price = str(list_content()[content_id]["price"])

    tx_hash = send_payment(
        user["secret_key"],
        user["public_key"],
        price
    )

    unlock_content(user_id, content_id)

    return {
        "message": "Content unlocked",
        "tx_hash": tx_hash
    }
