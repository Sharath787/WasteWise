import os
import random

import redis
from dotenv import load_dotenv
from rest_framework.exceptions import ValidationError

load_dotenv()

redis_client_url = os.getenv("REDIS_URL")
if not redis_client_url:
    raise ValueError("REDIS_URL environment variable is not set.")
redis_client = redis.from_url(redis_client_url)

MAX_OTP_ATTEMPTS = 3
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_COOLDOWN_TIME = 30  # 30 seconds


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def send_otp(phone: str, otp: str) -> None:
    method = os.getenv("OTP_DELIVERY_METHOD", "console")

    if method == "console":
        print(f"\n OTP for {phone}: {otp}\n")
    elif method == "email":
        pass  # Phase 4
    elif method == "sms":
        pass  # Phase 4


def can_send_otp(phone: str) -> tuple[bool, str, int]:
    cooldown_key = f"otp_cooldown:{phone}"
    ttl = redis_client.ttl(cooldown_key)

    if ttl > 0:
        return False, f"Please wait {ttl} seconds before requesting a new OTP.", ttl

    return True, "OK", 0


def store_otp(phone: str, otp: str) -> None:
    redis_client.setex(f"otp:{phone}", OTP_EXPIRY_SECONDS, otp)
    redis_client.setex(f"otp_cooldown:{phone}", OTP_COOLDOWN_TIME, "1")


def verify_otp(phone: str, otp: str) -> tuple[bool, str]:
    attempts_key = f"otp_attempts:{phone}"
    attempts = redis_client.get(attempts_key)

    if attempts is not None and int(attempts) >= MAX_OTP_ATTEMPTS:
        redis_client.delete(f"otp:{phone}")
        redis_client.delete(attempts_key)
        raise ValidationError("Maximum attempts exceeded. Please request a new OTP.")

    stored_otp = redis_client.get(f"otp:{phone}")
    stored_otp_str = (
        stored_otp.decode() if isinstance(stored_otp, bytes) else stored_otp
    )

    if stored_otp_str is None:
        raise ValidationError("OTP expired or not found. Please request a new OTP.")

    if stored_otp_str != otp:
        redis_client.incr(attempts_key)
        redis_client.expire(attempts_key, OTP_EXPIRY_SECONDS)
        remaining = MAX_OTP_ATTEMPTS - (int(attempts) + 1 if attempts else 1)
        raise ValidationError(f"Invalid OTP. {remaining} attempts remaining.")

    # Success — clean up
    redis_client.delete(f"otp:{phone}")
    redis_client.delete(attempts_key)
    return True, "OTP verified successfully."
