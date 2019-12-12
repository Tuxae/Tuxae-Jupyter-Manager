from datetime import datetime, timedelta
from hashlib import md5
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Tuple


def generate_token() -> Tuple[str, datetime]:
    token = ''.join(choice(ascii_lowercase + ascii_uppercase + digits) for _ in range(40))
    token_expiration = datetime.now() + timedelta(minutes=10)
    return token, token_expiration


def get_logo_url(email: str) -> str:
    return 'https://2.gravatar.com/avatar/{}?s=400&d=mm'.format(md5(email.encode()).hexdigest())


def sanitize_username(username: str) -> str:
    return username.replace('.', '')


def sanitize_email(email: str) -> str:
    for char in ['.', '@', '-', '_']:
        email = email.replace(char, '')
    return email


def generate_random_number() -> int:
    number = ''.join(choice(digits) for _ in range(6))
    return int(number)
