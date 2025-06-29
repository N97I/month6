from django.core.cache import cache
import random

def store_verification_code(email):
    code = str(random.randint(100000, 999999))
    cache.set(f"verify:{email}", code, timeout=300)  # 5 минут
    return code