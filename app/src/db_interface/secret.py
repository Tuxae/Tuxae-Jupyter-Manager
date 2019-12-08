from random import choice
from string import ascii_uppercase, digits

""" Default """
SECRET_KEY = ''.join(choice(ascii_uppercase + digits) for _ in range(30))
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_EMAIL = 'mail@example.com'
DEFAULT_ADMIN_PASSWORD = 'password'

""" Flask Mail """
MAIL_SERVER = 'smtp.gmail.com'   
MAIL_PORT = 465                 
MAIL_USERNAME = 'username@gmail.com'
MAIL_PASSWORD = 'password'     
MAIL_USE_TLS = True 
MAIL_USE_SSL = False
