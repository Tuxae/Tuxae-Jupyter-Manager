from typing import List

import docker.models.containers
from flask_sqlalchemy import SQLAlchemy

from src.db_interface.models import DockerContainers, Users


def associate_user_container(db: SQLAlchemy, user: Users, container: docker.models.containers.Container, image: str) \
        -> None:
    kwargs = {
        'id_container': container.id,
        'name': container.name,
        'image': image,
        'id_user': user.id
    }
    docker_container = DockerContainers(**kwargs)
    db.session.add(docker_container)
    db.session.commit()


def docker_image_already_deployed_by_user(db: SQLAlchemy, user: Users, image: str) -> bool:
    q = db.session.query(Users, DockerContainers). \
        filter(Users.id == DockerContainers.id_user). \
        filter(Users.email == user.email). \
        filter(DockerContainers.image == image). \
        all()
    return len(q) == 0


def delete_association_user_container(db: SQLAlchemy, container: docker.models.containers.Container) -> None:
    DockerContainers.query.filter_by(id_container=container.id).delete()
    db.session.commit()


def get_containers_by_user_email(email: str) -> List[DockerContainers]:
    return DockerContainers.query.join(Users, Users.id == DockerContainers.id_user). \
        filter(Users.email == email). \
        all()


def get_container_owner(container_id: str) -> str:
    user = Users.query.join(DockerContainers, DockerContainers.id_user == Users.id). \
        filter(DockerContainers.id_container == container_id). \
        first()
    if user is None:
        return ''
    return user.username
