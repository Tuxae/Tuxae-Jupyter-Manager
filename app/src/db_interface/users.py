from hashlib import md5
from random import choice
from string import ascii_uppercase, digits
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from src.db_interface.config import pwd_context
from src.db_interface.models import Users
from src.mail.parser import email_validator, parse_valid_email, EmailException


def create_user(db: SQLAlchemy, email: str, password: str) -> Users:
    password = pwd_context.hash(password.encode())
    if not email_validator(email):
        raise EmailException
    username = parse_valid_email(email)[0]
    kwargs = {
        'username': username,
        'email': email,
        'password': password,
        'logo_url': 'https://2.gravatar.com/avatar/{}?s=400&d=mm'.format(md5(email.encode()).hexdigest()),
        'token': ''.join(choice(ascii_uppercase + digits) for _ in range(30)),
        'token_expiration': datetime.now(),
    }
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()
    return user


def user_exists(email: str) -> bool:
    return Users.query.filter_by(email=email).first() is not None
