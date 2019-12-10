from src.mail.parser import parse_valid_email
from src.db_interface.models import WhitelistDomains


def check_whitelist_domain(email: str) -> bool:
    domain = parse_valid_email(email)[1]
    return WhitelistDomains.query.filter_by(domain=domain).first() is not None
