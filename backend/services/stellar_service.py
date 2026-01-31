from stellar_sdk import Server, Keypair, TransactionBuilder, Asset
import requests
from config import STELLAR_HORIZON, NETWORK_PASSPHRASE

server = Server(STELLAR_HORIZON)

def create_wallet():
    pair = Keypair.random()
    public_key = pair.public_key
    secret_key = pair.secret

    requests.get(f"https://friendbot.stellar.org?addr={public_key}")

    return public_key, secret_key


def send_payment(secret_key: str, destination: str, amount: str):
    source_keypair = Keypair.from_secret(secret_key)
    source_account = server.load_account(source_keypair.public_key)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=100
        )
        .append_payment_op(
            destination=destination,
            amount=amount,
            asset=Asset.native()
        )
        .set_timeout(30)
        .build()
    )

    tx.sign(source_keypair)
    response = server.submit_transaction(tx)

    return response["hash"]
