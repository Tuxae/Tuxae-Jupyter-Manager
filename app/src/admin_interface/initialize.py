from src.db_interface.models import Users, UsersModelView

from flask_sqlalchemy import SQLAlchemy
from flask_admin import base


def initialize_admin(admin: base.Admin, db: SQLAlchemy):
    admin.add_view(UsersModelView(Users, db.session))
