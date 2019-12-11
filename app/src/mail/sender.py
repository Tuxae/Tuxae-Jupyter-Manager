import flask_mail

from src.db_interface.models import Users
from src.db_interface.secret import EXTERNAL_URI, MAIL_USERNAME


def send_register_mail(mail: flask_mail.Mail, user: Users) -> None:
    html = f'''Hello {user.username},<br>
<br>
You just signed up for an account!<br>
Please confirm your ownership of this email address by clicking the link below:<br>
<a href="{EXTERNAL_URI}/verify?token={user.token}">{EXTERNAL_URI}/verify?token={user.token}</a><br>
<br>
Not expecting this email?<br>
If you received this by mistake or weren't expecting it, please disregard this email.<br>
<br>
'''
    subject = 'Verify your Tuxae Jupyter Manager account'
    mail.send_message(subject, sender=MAIL_USERNAME, recipients=[user.email], html=html)


def send_forgot_password_mail(mail: flask_mail.Mail, user: Users) -> None:
    html = f'''Hello {user.username},<br>
<br>
You just ask to reset your password from your account!<br>
You can use the link below:<br>
<a href="{EXTERNAL_URI}/reset-password?token={user.token}">{EXTERNAL_URI}/reset-password?token={user.token}</a><br>
<br>
Not expecting this email?<br>
If you received this by mistake or weren't expecting it, please disregard this email.<br>
<br>
'''
    subject = 'Reset your password from your Tuxae Jupyter Manager account'
    mail.send_message(subject, sender=MAIL_USERNAME, recipients=[user.email], html=html)
