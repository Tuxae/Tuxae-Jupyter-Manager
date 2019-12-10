from typing import Optional

from src.db_interface.models import Users


def check_token(token: str) -> Optional[Users]:
    return Users.query.filter_by(token=token).first()
