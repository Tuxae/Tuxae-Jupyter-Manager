from typing import Optional
from datetime import datetime

from src.db_interface.models import Users


def check_token(token: str) -> Optional[Users]:
    user = Users.query.filter_by(token=token).first()
    if user is None:
        # token is invalid
        return
    if user.token_expiration > datetime.now():
        # token has expired
        return
    return user
