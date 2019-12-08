import random
import string
from urllib.parse import urlparse, urljoin

from config.config import mail, pwd_context
from config.secrets_use import MAIL_USERNAME
from config.tables import Users
from flask import flash, request
from flask_login.utils import current_user
from flask_mail import Message


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def is_admin(app, db, form, token_reset=None):
    if 'username' not in form:
        return None, False
    if 'password' not in form:
        return None, False
    username, password = form['username'], form['password']
    password = pwd_context.hash(password)
    if token_reset is None:
        kwargs = dict(name=username, password=password)
    else:
        kwargs = dict(name=username, token_reset=token_reset,
                      password_reset=password)
    req = db.session.query(Users).filter_by(**kwargs).first()
    if token_reset is not None:
        req.password = password
        req.token_reset = ''
        req.password_reset = ''
        db.session.commit()
        return req, True
    if req is not None:
        return req, True

    """ First connexion """
    kwargs = dict(name=username)
    req = db.session.query(Users).filter_by(**kwargs).first()
    if req is not None:
        req.password = password
        db.session.commit()
        return req, True
    else:
        return None, False


def is_password_verified(db, password):
    password = pwd_context.hash(password)
    kwargs = dict(name=current_user.name, password=password)
    req = db.session.query(Users).filter_by(**kwargs).first()
    return req is not None


def update_password(app, db, form):
    checks = [(field in form.keys()) for field in ['password', 'previous_password']]
    if False in checks:
        flash('An error occurred while trying to update your password.', 'error')
        return False
    if not is_password_verified(db, form['previous_password']):
        flash('Wrong previous password.', 'error')
        return False
    kwargs = dict(name=current_user.name)
    req = db.session.query(Users).filter_by(**kwargs).first()
    if req is not None:
        req.password = pwd_context.hash(password)
        db.session.commit()
        flash('Your password has been updated successfully.', 'success')
        return True
    else:
        flash('An error occurred while trying to update your password.', 'error')
        return False


def add_admin(db, form):
    checks = [(field in form.keys()) for field in ['name', 'email', 'password']]
    if False in checks:
        return False
    kwargs = {'name': form['name']}
    user = db.session.query(Users).filter_by(**kwargs).first()
    if user is not None:
        return False
    kwargs = {'email': form['email']}
    user = db.session.query(Users).filter_by(**kwargs).first()
    if user is not None:
        return False
    kwargs = {'name': form['name'], 'email': form['email'],
              'password': pwd_context.hash(form['password'])}
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()
    return True


def get_user(field, form, db):
    try:
        kwargs = {field: form['forgot']}
        return db.session.query(Users).filter_by(**kwargs).first()
    except Exception as exception:
        return None


def send_email_reset_password(app, db, form):
    fields = ['name', 'email']
    options = [get_user(field, form, db) for field in fields]
    if options == [None] * len(options):
        return False, None
    option = [i for i in options if i != None][0]

    email = option.email
    new_password = ''.join(random.choice(string.ascii_letters) for i in range(25))
    token = ''.join(random.choice(string.ascii_letters) for i in range(25))
    new_password_hash = pwd_context.hash(new_password)

    option.token_reset = token
    option.password_reset = new_password_hash
    db.session.commit()

    url = "https://cassiopee.hackademint.org"
    subject = "Cassiopee HackademINT: Forgot Your Password?"
    body = ("Hello {0},\nYou asked for a password reset on {2}.\nIf you did "
            "not asked for "
            "it just ignore this message.\nIf you really want to reset it, you "
            "can login at {2}/login/{3} with the following password: {1}\nThe "
            "password will be updated with this new value only if you connect "
            "to this link with your new password, otherwise, it does not "
            "change your settings.\n\n---- Powered by Flask ----\n"
            ".".format(option.name, new_password, url, token))
    msg = Message(subject=subject, body=body, sender=MAIL_USERNAME, recipients=[email])
    mail.send(msg)
    return True, email


def update_email(app, db, form):
    checks = [(field in form.keys()) for field in ['email']]
    if False in checks:
        flash('An error occurred while trying to update your email.', 'error')
        return False
    kwargs = dict(name=current_user.name)
    req = db.session.query(Users).filter_by(**kwargs).first()
    if req is not None:
        req.email = form['email']
        db.session.commit()
        flash('Your email has been updated successfully.', 'success')
        return True
    else:
        flash('An error occurred while trying to update your email.', 'error')
        return False
