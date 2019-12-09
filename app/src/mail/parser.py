import re
from typing import List


class EmailException:
    pass


def email_validator(email: str) -> bool:
    return re.match(r'^.+@([?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?))$', email) is not None


def parse_valid_email(email: str) -> List[str]:
    return email.split('@')
