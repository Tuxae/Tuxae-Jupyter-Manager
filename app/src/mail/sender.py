import flask_mail

from src.db_interface.models import Users


def send_register_mail(mail: flask_mail.Mail, new_user: Users) -> None:
    return
