"""
Improved wallet.py with automatic Soroban deposit after roundoff payment
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from pydantic import BaseModel
from app.database import SessionLocal
from app.models.user import User
from app.models.wallet import Wallet
from app.utils.dependencies import get_current_user
from app.utils.encryption import decrypt_secret, encrypt_secret
from app.services.stellar_service import (
    generate_stellar_wallet,
    fund_testnet_account,
    atomic_payment_with_roundoff,
    soroban_deposit,  # Import for auto-deposit
)
from app.config import VAULT_PUBLIC_KEY

router = APIRouter()

class PaymentRequest(BaseModel):
    destination: str
    amount: float
    roundoff_option: str = "none"
    
@router.post("/create")
def create_wallet(current_user: str = Depends(get_current_user)):
    """Create a new Stellar wallet for the user"""
    db: Session = SessionLocal()
    
    user = db.query(User).filter(User.email == current_user).first()
    existing = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Wallet already exists")
    
    # Generate new Stellar keypair
    keys = generate_stellar_wallet()
    encrypted = encrypt_secret(keys["secret_key"])
    
    # Save to database
    wallet = Wallet(
        user_id=user.id,
        public_key=keys["public_key"],
        encrypted_secret=encrypted
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    db.close()
    
    return {
        "public_key": keys["public_key"],
        "message": "Wallet created successfully"
    }

@router.post("/fund")
def fund_wallet(
    public_key: str = Query(...),
    current_user: str = Depends(get_current_user)
):
    """Fund wallet with testnet XLM from Friendbot"""
    try:
        result = fund_testnet_account(public_key)
        return {
            "message": "Wallet funded successfully",
            "friendbot_response": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/balance")
def get_balance(current_user: str = Depends(get_current_user)):
    """Get user's wallet balance"""
    db: Session = SessionLocal()
    
    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    
    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    db.close()
    
    return {
        "public_key": wallet.public_key,
        "message": "Check balance on Stellar Explorer"
    }

@router.post("/pay")
def pay(
    payment: PaymentRequest,
    current_user: str = Depends(get_current_user)
):
    db: Session = SessionLocal()

    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")

    decrypted_secret = decrypt_secret(wallet.encrypted_secret)

    merchant_amount = Decimal(str(payment.amount))
    roundoff_amount = Decimal("0")

    if payment.roundoff_option == "invest":
        roundoff_amount = Decimal("3")  # demo logic

    try:
        payment_result = atomic_payment_with_roundoff(
            source_secret=decrypted_secret,
            merchant_destination=payment.destination,
            merchant_amount=merchant_amount,
            vault_destination=VAULT_PUBLIC_KEY,
            roundoff_amount=roundoff_amount
        )

        if not payment_result.get("successful"):
            db.close()
            raise HTTPException(
                status_code=400,
                detail=f"Payment failed: {payment_result.get('error', 'Unknown error')}"
            )

        soroban_result = None
        if roundoff_amount > 0:
            try:
                soroban_result = soroban_deposit(
                    user_secret=decrypted_secret,
                    amount=int(roundoff_amount)
                )
            except Exception as e:
                print(f"Soroban deposit failed: {e}")

        db.close()

        return {
            "successful": True,
            "payment_hash": payment_result["hash"],
            "merchant_amount": float(merchant_amount),
            "roundoff_amount": float(roundoff_amount),
            "total_spent": float(merchant_amount + roundoff_amount),
            "soroban_deposit_hash": soroban_result.get("hash") if soroban_result else None
        }

    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-wallet")
def my_wallet(current_user: str = Depends(get_current_user)):
    """Get current user's wallet info"""
    db: Session = SessionLocal()
    
    user = db.query(User).filter(User.email == current_user).first()
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    
    if not wallet:
        db.close()
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    db.close()
    
    return {
        "public_key": wallet.public_key,
        "created_at": wallet.created_at.isoformat() if wallet.created_at else None
    }