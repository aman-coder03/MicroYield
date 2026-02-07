from decimal import Decimal, ROUND_DOWN
from typing import List, Dict, Any
from datetime import datetime

from app.services.stellar_service import (
    soroban_get_total_usdc_principal,
    soroban_get_user_summary,
    soroban_add_yield_admin,
)

# ===== Config =====
ANNUAL_APY = Decimal("0.08")         # 8% annual yield
DAYS_IN_YEAR = Decimal("365")        # used for daily-rate conversion
YIELD_PRECISION = Decimal("0.0000001")  # 7 decimal places (Soroban-friendly display)


def _to_decimal(value: Any) -> Decimal:
    """
    Convert incoming values safely to Decimal.
    - Uses str() to avoid float precision issues.
    """
    try:
        return Decimal(str(value))
    except Exception:
        # Keep behavior simple: treat unparseable values as 0
        return Decimal("0")


def _quantize_down(value: Decimal, precision: Decimal = YIELD_PRECISION) -> Decimal:
    """
    Round DOWN to a fixed precision.
    """
    return value.quantize(precision, rounding=ROUND_DOWN)


def calculate_daily_yield(total_principal: Decimal) -> Decimal:
    """
    Simulate daily yield based on annual APY.

    Logic (unchanged):
      daily_rate = ANNUAL_APY / DAYS_IN_YEAR
      earned = total_principal * daily_rate
      round down to 7 decimals
    """
    total_principal = _to_decimal(total_principal)

    daily_rate = ANNUAL_APY / DAYS_IN_YEAR
    earned = total_principal * daily_rate

    return _quantize_down(earned)


def distribute_daily_yield(users: List[str]) -> Dict[str, Any]:
    """
    Distribute yield proportionally to all users based on their USDC principal.

    Working (unchanged):
    - Fetch total vault principal
    - If 0, return early
    - Compute daily yield on total principal
    - For each user:
        - Get (xlm, principal, yield_amt)
        - Compute share = user_principal / total_principal
        - user_yield = daily_yield * share (rounded down)
        - If > 0: call admin add yield with int(user_yield)
    - Return distribution summary + timestamp
    """

    # --- Step 1: total principal in vault ---
    total_principal_raw = soroban_get_total_usdc_principal()
    total_principal = _to_decimal(total_principal_raw)

    if total_principal == 0:
        return {"message": "No principal in vault"}

    # --- Step 2: compute yield generated today ---
    daily_yield = calculate_daily_yield(total_principal)

    # --- Step 3: distribute across users ---
    distributed_results: List[Dict[str, str]] = []

    for user_public_key in users:
        # Expected return: (xlm, principal, yield_amt)
        xlm, principal, yield_amt = soroban_get_user_summary(user_public_key)

        user_principal = _to_decimal(principal)

        # Skip users with no principal
        if user_principal == 0:
            continue

        share_ratio = user_principal / total_principal

        user_yield = _quantize_down(daily_yield * share_ratio)

        if user_yield > 0:
            # IMPORTANT: keeping your original call behavior unchanged
            soroban_add_yield_admin(user_public_key, int(user_yield))

            distributed_results.append(
                {
                    "user": user_public_key,
                    "yield_added": str(user_yield),
                }
            )

    # --- Step 4: return summary ---
    return {
        "total_principal": str(total_principal),
        "daily_yield_generated": str(daily_yield),
        "distributed_to": distributed_results,
        "timestamp": datetime.utcnow().isoformat(),
    }
