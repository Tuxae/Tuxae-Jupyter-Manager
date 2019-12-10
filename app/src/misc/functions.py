from typing import Tuple
from random import choice
from string import ascii_lowercase, ascii_uppercase, digits
from datetime import datetime, timedelta


def generate_token() -> Tuple[str, datetime]:
    token = ''.join(choice(ascii_lowercase, ascii_uppercase + digits) for _ in range(40))
    token_expiration = datetime.now() + timedelta(minutes=10)
    return token, token_expiration
