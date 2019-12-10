from flask_sqlalchemy import SQLAlchemy

from src.db_interface.config import pwd_context
from src.db_interface.models import Users
from src.mail.parser import email_validator, parse_valid_email, EmailException
from src.misc.functions import generate_token, get_logo_url


def create_user(db: SQLAlchemy, email: str, password: str) -> Users:
    password = pwd_context.hash(password.encode())
    if not email_validator(email):
        raise EmailException
    username = parse_valid_email(email)[0]
    logo_url = get_logo_url(email)
    token, token_expiration = generate_token()
    kwargs = {
        'username': username,
        'email': email,
        'password': password,
        'token': token,
        'token_expiration': token_expiration,
        'logo_url': logo_url
    }
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()
    return user


def user_exists(email: str) -> bool:
    return Users.query.filter_by(email=email).first() is not None
