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
