from src.db_interface.models import Users, UsersModelView, WhitelistDomains, WhitelistDomainsModelView, \
    DockerContainers, DockerContainersModelView

from flask_sqlalchemy import SQLAlchemy
from flask_admin import base


def initialize_admin(admin: base.Admin, db: SQLAlchemy):
    admin.add_view(UsersModelView(Users, db.session))
    admin.add_view(WhitelistDomainsModelView(WhitelistDomains, db.session))
    admin.add_view(DockerContainersModelView(DockerContainers, db.session))
