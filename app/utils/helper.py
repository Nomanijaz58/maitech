import random
from datetime import datetime, timezone


def generate_otp(length=4) -> str:
    return ''.join(random.choices("0123456789", k=length))


def utc_now():
    return datetime.now(timezone.utc)
