from math import ceil
from config import ROUNDING_BASE

def calculate_spare_change(amount: float):
    rounded = ceil(amount / ROUNDING_BASE) * ROUNDING_BASE
    return round(rounded - amount, 2)