from flask import flash, redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin
from flask_login.utils import current_user
from flask_sqlalchemy import SQLAlchemy


from src.db_interface.config import pwd_context
from src.db_interface.secret import DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD

db = SQLAlchemy()


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)
    token_reset = db.Column(db.String(200), unique=False, nullable=True)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class WhitelistDomains(db.Model, UserMixin):
    __tablename__ = 'whiltelist_domains'
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(200), unique=True, nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class UsersModelView(ModelView):
    page_size = 5
    column_searchable_list = ['username']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! Please identify yourself.', 'error')
        return redirect(url_for('login'))


class WhitelistDomainsModelView(ModelView):
    page_size = 5
    column_searchable_list = ['domain']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! Please identify yourself.', 'error')
        return redirect(url_for('login'))


class DefaultModelView(ModelView):
    page_size = 5
    column_searchable_list = ['username']

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! Please identify yourself.', 'error')
        return redirect(url_for('login'))


class MyAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, username, **kwargs):
        flash('Access forbidden ! Please identify yourself.', 'error')
        return redirect(url_for('login'))

    def _handle_view(self, username, *args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not self.is_accessible():
            flash('Access forbidden ! Please identify yourself.', 'error')
            return redirect(url_for('login'))


def create_default_user():
    db.create_all()
    users = Users.query.all()
    if len(users) > 0:
        return
    password = pwd_context.hash(DEFAULT_ADMIN_PASSWORD)
    kwargs = {'username': DEFAULT_ADMIN_USERNAME, 'email': DEFAULT_ADMIN_EMAIL, 'password': password}
    user = Users(**kwargs)
    db.session.add(user)
    db.session.commit()


def initialize_db(app) -> SQLAlchemy:
    app.app_context().push()
    db.init_app(app)
    db.create_all()
    create_default_user()
    return db
