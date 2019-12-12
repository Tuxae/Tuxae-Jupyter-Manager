from flask_admin import base
from flask_sqlalchemy import SQLAlchemy

from src.db_interface.models import Users, UsersModelView, WhitelistDomains, WhitelistDomainsModelView, \
    DockerContainers, DockerContainersModelView, ReportMessage, ReportMessageModelView


def initialize_admin(admin: base.Admin, db: SQLAlchemy):
    admin.add_view(UsersModelView(Users, db.session))
    admin.add_view(WhitelistDomainsModelView(WhitelistDomains, db.session))
    admin.add_view(DockerContainersModelView(DockerContainers, db.session))
    admin.add_view(ReportMessageModelView(ReportMessage, db.session))
