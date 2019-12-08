from passlib.context import CryptContext

from src.db_interface.secret import SECRET_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, \
    MAIL_USE_TLS, MAIL_USE_SSL

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """ Default SQLALCHEMY_DATABASE_URI """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/database.db'
    SQLALCHEMY_ECHO = True
    LANGUAGES = ['fr']
    SECRET_KEY = SECRET_KEY

    FLASK_ADMIN_SWATCH = 'cerulean'
    #  FLASK_ADMIN_SWATCH = 'darkly'

    MAIL_SERVER = MAIL_SERVER
    MAIL_PORT = MAIL_PORT
    MAIL_USERNAME = MAIL_USERNAME
    MAIL_PASSWORD = MAIL_PASSWORD
    MAIL_USE_TLS = MAIL_USE_TLS
    MAIL_USE_SSL = MAIL_USE_SSL
