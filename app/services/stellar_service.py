import requests
from decimal import Decimal, ROUND_DOWN

from stellar_sdk import (
    TransactionBuilder,
    Network,
    Asset,
    Keypair,
    Address,
    SorobanServer,
    scval,
)

from stellar_sdk.server import Server
from stellar_sdk.exceptions import BadRequestError

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
# HELPER FUNCTIONS
# =========================

def is_valid_stellar_address(address: str) -> bool:
    if not address:
        return False
    
    try:
        Keypair.from_public_key(address)
        return True
    except Exception:
        return False


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
    if not is_valid_stellar_address(public_key):
        raise ValueError(f"Invalid Stellar address: {public_key}")
    
    response = requests.get(
        f"https://friendbot.stellar.org?addr={public_key}"
    )
    return response.json()


def send_xlm(source_secret: str, destination: str, amount: Decimal):
    # Validate destination address
    if not is_valid_stellar_address(destination):
        raise ValueError(f"Invalid destination address: {destination}")
    
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
    """
    Execute an atomic payment with optional roundoff to vault
    
    Args:
        source_secret: Secret key of the sender
        merchant_destination: Public key of the merchant
        merchant_amount: Amount to send to merchant
        vault_destination: Public key of the vault
        roundoff_amount: Amount to send to vault as roundoff
    """
    # Validate addresses
    if not is_valid_stellar_address(merchant_destination):
        raise ValueError(f"Invalid merchant destination address: {merchant_destination}")
    
    if roundoff_amount > 0 and not is_valid_stellar_address(vault_destination):
        raise ValueError(f"Invalid vault destination address: {vault_destination}")
    
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
        return {
            "successful": response["successful"],
            "hash": response["hash"],
        }
    except BadRequestError as e:
        # Extract error details
        error_msg = str(e)
        if hasattr(e, 'extras') and e.extras:
            error_msg = e.extras.get('result_codes', {})
        
        return {
            "successful": False,
            "error": error_msg
        }
    except Exception as e:
        return {
            "successful": False,
            "error": str(e)
        }


# =========================
# SOROBAN FUNCTIONS - MATCHING YOUR CONTRACT
# =========================

def soroban_deposit_xlm(user_secret: str, amount: int):
    """
    Call the deposit_xlm function on your Soroban contract
    This deposits XLM savings into the contract
    """
    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    
    keypair = Keypair.from_secret(user_secret)
    source_account = soroban_server.load_account(keypair.public_key)

    # Convert amount to stroops (1 XLM = 10,000,000 stroops)
    amount_stroops = int(amount * 10_000_000)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_invoke_contract_function_op(
            contract_id=SOROBAN_CONTRACT_ID,
            function_name="deposit_xlm",  # Your actual contract function
            parameters=[
                scval.to_address(keypair.public_key),
                scval.to_int128(amount_stroops),
            ],
        )
        .set_timeout(30)
        .build()
    )

    prepared_tx = soroban_server.prepare_transaction(tx)
    prepared_tx.sign(keypair)
    response = soroban_server.send_transaction(prepared_tx)
    print(response.status)

    return {"hash": response.hash, "successful": True}


def soroban_invest_usdc(user_secret: str, amount: int):
    """
    Call the invest_usdc function on your Soroban contract
    This converts XLM savings to USDC principal
    """
    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    
    keypair = Keypair.from_secret(user_secret)
    source_account = soroban_server.load_account(keypair.public_key)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_invoke_contract_function_op(
            contract_id=SOROBAN_CONTRACT_ID,
            function_name="invest_usdc",  # Your actual contract function
            parameters=[
                scval.to_address(keypair.public_key),
                scval.to_int128(amount),
            ],
        )
        .set_timeout(30)
        .build()
    )

    prepared_tx = soroban_server.prepare_transaction(tx)
    prepared_tx.sign(keypair)
    response = soroban_server.send_transaction(prepared_tx)
    print(response.status)

    return {"hash": response.hash, "successful": True}


def soroban_withdraw_xlm(user_secret: str, amount: int):
    """
    Call the withdraw_xlm function on your Soroban contract
    """
    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    
    keypair = Keypair.from_secret(user_secret)
    source_account = soroban_server.load_account(keypair.public_key)

    tx = (
        TransactionBuilder(
            source_account=source_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100,
        )
        .append_invoke_contract_function_op(
            contract_id=SOROBAN_CONTRACT_ID,
            function_name="withdraw_xlm",  # Your actual contract function
            parameters=[
                scval.to_address(keypair.public_key),
                scval.to_int128(amount),
            ],
        )
        .set_timeout(30)
        .build()
    )

    prepared_tx = soroban_server.prepare_transaction(tx)
    prepared_tx.sign(keypair)
    response = soroban_server.send_transaction(prepared_tx)
    print(response.status)

    return {"hash": response.hash, "successful": True}


def soroban_get_user_summary(user_public_key: str):
    """
    Call get_user_summary on your Soroban contract
    Returns: (xlm_balance, usdc_principal, usdc_yield)
    """
    
    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    
    try:
        source_account = soroban_server.load_account(user_public_key)

        tx = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_invoke_contract_function_op(
                contract_id=SOROBAN_CONTRACT_ID,
                function_name="get_user_summary",  # Your actual contract function
                parameters=[
                    scval.to_address(user_public_key),
                ],
            )
            .set_timeout(30)
            .build()
        )

        simulation = soroban_server.simulate_transaction(tx)

        if simulation.results and len(simulation.results) > 0:
            result = simulation.results[0]
            
            if hasattr(result, 'return_value') and result.return_value:
                from stellar_sdk import xdr as stellar_xdr
                
                sc_val = result.return_value
                
                # The contract returns a tuple (xlm, principal, yield)
                # We need to parse the Vec/Tuple from the return value
                if sc_val.type == stellar_xdr.SCValType.SCV_VEC:
                    vec = scval.from_vec(sc_val)
                    if len(vec) >= 3:
                        xlm_balance = vec[0] if isinstance(vec[0], int) else 0
                        usdc_principal = vec[1] if isinstance(vec[1], int) else 0
                        usdc_yield = vec[2] if isinstance(vec[2], int) else 0
                        
                        # Convert from stroops to XLM
                        xlm_balance = xlm_balance / 10_000_000
                        usdc_principal = usdc_principal / 10_000_000
                        usdc_yield = usdc_yield / 10_000_000
                        
                        return {
                            "xlm_balance": xlm_balance,
                            "usdc_principal": usdc_principal,
                            "usdc_yield": usdc_yield
                        }
            
        # Return zeros if no data found
        return {
            "xlm_balance": 0,
            "usdc_principal": 0,
            "usdc_yield": 0
        }
        
    except Exception as e:
        print(f"Error getting Soroban user summary: {str(e)}")
        return {
            "xlm_balance": 0,
            "usdc_principal": 0,
            "usdc_yield": 0
        }


def soroban_get_total_xlm():
    """
    Get total XLM in the contract
    """
    soroban_server = SorobanServer(SOROBAN_RPC_URL)
    
    try:
        # Use vault account to make the query
        source_account = soroban_server.load_account(VAULT_PUBLIC_KEY)

        tx = (
            TransactionBuilder(
                source_account=source_account,
                network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_invoke_contract_function_op(
                contract_id=SOROBAN_CONTRACT_ID,
                function_name="total_xlm",
                parameters=[],
            )
            .set_timeout(30)
            .build()
        )

        simulation = soroban_server.simulate_transaction(tx)

        if simulation.results and len(simulation.results) > 0:
            result = simulation.results[0]
            
            if hasattr(result, 'return_value') and result.return_value:
                from stellar_sdk import xdr as stellar_xdr
                
                sc_val = result.return_value
                
                if sc_val.type == stellar_xdr.SCValType.SCV_I128:
                    total = scval.from_int128(sc_val)
                    return total / 10_000_000  # Convert stroops to XLM
            
        return 0
        
    except Exception as e:
        print(f"Error getting total XLM: {str(e)}")
        return 0


# Legacy function names for backward compatibility
def soroban_deposit(user_secret: str, amount: int):
    """Alias for deposit_xlm"""
    return soroban_deposit_xlm(user_secret, amount)

def soroban_withdraw(user_secret: str, amount: int):
    """Alias for withdraw_xlm"""
    return soroban_withdraw_xlm(user_secret, amount)

def soroban_get_balance(user_public_key: str):
    """Get XLM balance from user summary"""
    summary = soroban_get_user_summary(user_public_key)
    return summary["xlm_balance"]