from datetime import datetime, timedelta
from hashlib import md5
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Tuple


def generate_token() -> Tuple[str, datetime]:
    token = ''.join(choice(ascii_lowercase, ascii_uppercase + digits) for _ in range(40))
    token_expiration = datetime.now() + timedelta(minutes=10)
    return token, token_expiration


def get_logo_url(email: str) -> str:
    return 'https://2.gravatar.com/avatar/{}?s=400&d=mm'.format(md5(email.encode()).hexdigest())
