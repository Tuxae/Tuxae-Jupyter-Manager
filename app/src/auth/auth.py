from typing import Optional

from src.db_interface.models import Users


def is_fake_login_form(form) -> bool:
    return 'email' not in form or 'password' not in form


def get_admin_user(form) -> Optional[Users]:
    email, password = form['email'], form['password']
    #  password = pwd_context.hash(password)
    kwargs = dict(email=email)
    user = Users.query.filter_by(**kwargs).first()
    if user is None or not user.check_password(password):
        return
    return user
