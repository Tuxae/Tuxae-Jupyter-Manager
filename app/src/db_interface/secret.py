from random import choice
from string import ascii_uppercase, digits
from os import environ

""" Default """
SECRET_KEY = ''.join(choice(ascii_uppercase + digits) for _ in range(30))
DEFAULT_ADMIN_EMAIL = environ.get('DEFAULT_ADMIN_EMAIL')
DEFAULT_ADMIN_PASSWORD = environ.get('DEFAULT_ADMIN_PASSWORD')

""" Flask Mail """
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465                 
MAIL_USERNAME = environ.get('MAIL_USERNAME')
MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
MAIL_USE_TLS = True 
MAIL_USE_SSL = False
