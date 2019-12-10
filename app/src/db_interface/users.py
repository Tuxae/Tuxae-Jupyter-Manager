from hashlib import md5

from flask_sqlalchemy import SQLAlchemy

from src.db_interface.config import pwd_context
from src.db_interface.models import Users
from src.mail.parser import email_validator, parse_valid_email, EmailException
from src.misc.functions import generate_token


def create_user(db: SQLAlchemy, email: str, password: str) -> Users:
    password = pwd_context.hash(password.encode())
    if not email_validator(email):
        raise EmailException
    username = parse_valid_email(email)[0]
    token, token_expiration = generate_token()
    kwargs = {
        'username': username,
        'email': email,
        'password': password,
        'logo_url': 'https://2.gravatar.com/avatar/{}?s=400&d=mm'.format(md5(email.encode()).hexdigest()),
        'token': token,
        'token_expiration': token_expiration
    }
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()
    return user


def user_exists(email: str) -> bool:
    return Users.query.filter_by(email=email).first() is not None
