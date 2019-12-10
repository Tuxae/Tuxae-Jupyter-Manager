from flask import flash, redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin
from flask_login.utils import current_user
from flask_sqlalchemy import SQLAlchemy

from src.db_interface.config import pwd_context
from src.db_interface.secret import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from src.mail.parser import email_validator, parse_valid_email, EmailException
from src.misc.functions import generate_token, get_logo_url

db = SQLAlchemy()


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)
    token = db.Column(db.String(200), unique=False, nullable=True)
    token_expiration = db.Column(db.DateTime(), unique=False, nullable=False)
    logo_url = db.Column(db.String(200), unique=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.email}>'

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)


class WhitelistDomains(db.Model, UserMixin):
    __tablename__ = 'whiltelist_domains'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(200), unique=True, nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.domain}>'


class UsersModelView(ModelView):
    page_size = 5
    column_searchable_list = ['username']
    column_exclude_list = ['token', 'token_expiration', 'logo_url']
    form_excluded_columns = ['token', 'token_expiration', 'logo_url']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! You are not an administrator.', 'error')
        return redirect(url_for('index'))


class WhitelistDomainsModelView(ModelView):
    page_size = 5
    column_searchable_list = ['domain']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! You are not an administrator.', 'error')
        return redirect(url_for('index'))


class DefaultModelView(ModelView):
    page_size = 5
    column_searchable_list = ['username']

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! You are not an administrator.', 'error')
        return redirect(url_for('index'))


class MyAdminView(AdminIndexView):

    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! You are not an administrator.', 'error')
        return redirect(url_for('index'))

    def _handle_view(self, username, *args, **kwargs):
        if not self.is_accessible():
            flash('Access forbidden ! You are not an administrator.', 'error')
            return redirect(url_for('index'))


def create_default_user():
    db.create_all()
    users = Users.query.all()
    if len(users) > 0:
        return
    password = pwd_context.hash(DEFAULT_ADMIN_PASSWORD.encode())
    if not email_validator(DEFAULT_ADMIN_EMAIL):
        raise EmailException
    username = parse_valid_email(DEFAULT_ADMIN_EMAIL)[0]
    logo_url = get_logo_url(DEFAULT_ADMIN_EMAIL)
    token, token_expiration = generate_token()
    kwargs = {
        'username': username,
        'email': DEFAULT_ADMIN_EMAIL,
        'password': password,
        'token': token,
        'token_expiration': token_expiration,
        'logo_url': logo_url,
        'is_verified': True,
        'is_admin': True
    }
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()


def initialize_db(app) -> SQLAlchemy:
    app.app_context().push()
    db.init_app(app)
    db.create_all()
    create_default_user()
    return db
