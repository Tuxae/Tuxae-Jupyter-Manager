from datetime import datetime
from typing import Optional

from src.db_interface.models import Users


def check_token(token: str) -> Optional[Users]:
    user = Users.query.filter_by(token=token).first()
    if user is None:
        # token is invalid
        return
    if datetime.now() > user.token_expiration:
        # token has expired
        return
    return user
