from config import APY

def generate_daily_yield(invested: float):
    daily = invested * (APY / 365)
    return round(daily, 4)
