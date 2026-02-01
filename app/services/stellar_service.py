import requests
from decimal import Decimal, ROUND_DOWN

from stellar_sdk import (
    TransactionBuilder,
    Network,
    Asset,
    Keypair,
    Address
    )
from stellar_sdk import Contract

from stellar_sdk.server import Server

from app.config import (
    HORIZON_URL,
    ISSUER_SECRET_KEY,
    ISSUER_PUBLIC_KEY,
    VAULT_SECRET_KEY,
    VAULT_PUBLIC_KEY,
    SOROBAN_CONTRACT_ID,
    SOROBAN_RPC_URL,
)

# Horizon server
server = Server(HORIZON_URL)

# =========================
# BASIC WALLET FUNCTIONS
# =========================

def generate_stellar_wallet():
    keypair = Keypair.random()
    return {
        "public_key": keypair.public_key,
        "secret_key": keypair.secret
    }


def fund_testnet_account(public_key: str):
    response = requests.get(
        f"https://friendbot.stellar.org?addr={public_key}"
    )
    return response.json()


def send_xlm(source_secret: str, destination: str, amount: Decimal):
    amount = Decimal(str(amount))

    source_keypair = Keypair.from_secret(source_secret)
    source_account = server.load_account(source_keypair.public_key)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_payment_op(
            destination=destination,
            amount=str(amount.quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)),
            asset=Asset.native(),
        )
        .set_timeout(30)
        .build()
    )

    tx.sign(source_keypair)
    response = server.submit_transaction(tx)

    return {
        "successful": response["successful"],
        "hash": response["hash"],
    }


# =========================
# VAULT TRUSTLINE & MINT
# =========================

def create_vault_trustline():
    vault_keypair = Keypair.from_secret(VAULT_SECRET_KEY)
    source_account = server.load_account(vault_keypair.public_key)

    usdc_asset = Asset("USDC", ISSUER_PUBLIC_KEY)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_change_trust_op(asset=usdc_asset)
        .set_timeout(30)
        .build()
    )

    tx.sign(vault_keypair)
    response = server.submit_transaction(tx)

    return {
        "successful": response["successful"],
        "hash": response["hash"],
    }


def mint_usdc_to_vault(amount: Decimal):
    amount = Decimal(str(amount))

    issuer_keypair = Keypair.from_secret(ISSUER_SECRET_KEY)
    source_account = server.load_account(issuer_keypair.public_key)

    usdc_asset = Asset("USDC", ISSUER_PUBLIC_KEY)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_payment_op(
            destination=VAULT_PUBLIC_KEY,
            amount=str(amount),
            asset=usdc_asset,
        )
        .set_timeout(30)
        .build()
    )

    tx.sign(issuer_keypair)
    response = server.submit_transaction(tx)

    return {
        "successful": response["successful"],
        "hash": response["hash"],
    }


# =========================
# ATOMIC PAYMENT
# =========================

def atomic_payment_with_roundoff(
    source_secret: str,
    merchant_destination: str,
    merchant_amount: Decimal,
    vault_destination: str,
    roundoff_amount: Decimal,
):
    merchant_amount = Decimal(str(merchant_amount))
    roundoff_amount = Decimal(str(roundoff_amount))

    source_keypair = Keypair.from_secret(source_secret)
    source_account = server.load_account(source_keypair.public_key)

    tx_builder = TransactionBuilder(
        source_account=source_account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=100,
    )

    # Merchant payment
    tx_builder.append_payment_op(
        destination=merchant_destination,
        amount=str(merchant_amount.quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)),
        asset=Asset.native(),
    )

    # Vault roundoff
    if roundoff_amount > 0:
        tx_builder.append_payment_op(
            destination=vault_destination,
            amount=str(roundoff_amount.quantize(Decimal("0.0000001"), rounding=ROUND_DOWN)),
            asset=Asset.native(),
        )

    tx = tx_builder.set_timeout(30).build()
    tx.sign(source_keypair)

    try:
        response = server.submit_transaction(tx)
    except Exception as e:
        return {"successful": False, "error": str(e)}

    return {
        "successful": response["successful"],
        "hash": response["hash"],
    }


# =========================
# SOROBAN FUNCTIONS
# =========================

def soroban_deposit(user_secret: str, amount: int):
    from stellar_sdk import Server as SorobanServer

    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    contract_instance = Contract(SOROBAN_CONTRACT_ID)

    keypair = Keypair.from_secret(user_secret)
    source_account = soroban_server.load_account(keypair.public_key)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_operation(
            contract_instance.call(
                "deposit",
                Address.from_account_id(keypair.public_key),
                amount,
            )
        )
        .set_timeout(30)
        .build()
    )

    tx.sign(keypair)
    response = soroban_server.submit_transaction(tx)

    return {"hash": response["hash"], "successful": response["successful"]}


def soroban_withdraw(user_secret: str, amount: int):
    from stellar_sdk import Server as SorobanServer

    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    contract_instance = Contract(SOROBAN_CONTRACT_ID)

    keypair = Keypair.from_secret(user_secret)
    source_account = soroban_server.load_account(keypair.public_key)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_operation(
            contract_instance.call(
                "withdraw",
                Address.from_account_id(keypair.public_key),
                amount,
            )
        )
        .set_timeout(30)
        .build()
    )

    tx.sign(keypair)
    response = soroban_server.submit_transaction(tx)

    return {"hash": response["hash"], "successful": response["successful"]}


def soroban_get_balance(user_public_key: str):
    from stellar_sdk import Server as SorobanServer

    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    contract_instance = Contract(SOROBAN_CONTRACT_ID)

    source_account = soroban_server.load_account(user_public_key)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_operation(
            contract_instance.call(
                "get_balance",
                Address.from_account_id(user_public_key),
            )
        )
        .set_timeout(30)
        .build()
    )

    simulation = soroban_server.simulate_transaction(tx)

    return simulation.result
