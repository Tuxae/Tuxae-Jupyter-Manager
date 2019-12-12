import multiprocessing
import os
from typing import List, Optional

import docker.client
import docker.errors
import docker.models.containers
import docker.models.images
import werkzeug.local
from flask import flash
from psutil import virtual_memory

from src.db_interface.containers import get_containers_by_user_email
from src.db_interface.models import Users
from src.db_interface.secret import DOCKER_REGISTRY_URI, SERVER_DOMAIN, DEFAULT_ADMIN_EMAIL
from src.misc.functions import sanitize_username, generate_random_number


def get_docker_containers(docker_client: docker.client.DockerClient, user: Users) \
        -> List[docker.models.containers.Container]:
    all_containers = docker_client.containers.list(all=True)
    docker_containers = get_containers_by_user_email(user.email)
    docker_container_ids = [docker_container.id_container for docker_container in docker_containers]
    containers = []
    for container in all_containers:
        if not container.image.tags:
            continue
        if not container.image.tags[0].startswith(DOCKER_REGISTRY_URI):
            continue
        if not user.is_admin and container.id not in docker_container_ids:
            continue
        container.user = lambda: None
        container.user.name = user.username
        containers.append(container)
    return containers


def get_docker_containers_ids(docker_client: docker.client.DockerClient, user: Users) -> List[str]:
    containers = get_docker_containers(docker_client, user)
    return [container.id for container in containers]


def get_docker_images(docker_client: docker.client.DockerClient) -> List[docker.models.images.Image]:
    all_images = docker_client.images.list()
    images = []
    for image in all_images:
        if not image.attrs['RepoTags']:
            continue
        image_name = image.attrs['RepoTags'][0]
        if not image_name.startswith(DOCKER_REGISTRY_URI):
            continue
        images.append(image)
    return images


def check_image(image: str) -> bool:
    return image.startswith(DOCKER_REGISTRY_URI)


def deploy_container(docker_client: docker.client.DockerClient, image: str, current_user: werkzeug.local.LocalProxy) \
        -> Optional[docker.models.containers.Container]:
    cpus = int(multiprocessing.cpu_count() / 2)  # 50% of cpu
    mem = int(virtual_memory().total / 10 ** 6 / 4)  # 25% of total physical memory available (Mega)

    username = sanitize_username(current_user.username)
    random_number = generate_random_number()
    host = f'{username}-{random_number}.{SERVER_DOMAIN}'
    environment = [
        f'VIRTUAL_HOST={host}',
        f'LETSENCRYPT_HOST={host}',
        f'LETSENCRYPT_EMAIL={DEFAULT_ADMIN_EMAIL}'
    ]
    volumes = {}
    if 'datascience-notebook' in image:
        environment += [
            f'VIRTUAL_PORT=8888',
            f'JUPYTER_ENABLE_LAB=yes'
        ]
        path = f'/opt/users/{username}'
        volumes = {
            path:
                {
                    'bind': '/home/jovyan/work',
                    'mode': 'rw'
                }
        }
        if not os.path.isdir(path):
            os.mkdir(path)
        os.chmod(path, 0o777)
    try:
        container = docker_client.containers.run(
            image,
            detach=True,
            environment=environment,
            volumes=volumes,
            cpu_count=cpus,
            mem_limit=f'{mem}m'
        )
        """
        storage_opt={
            'size': '10G'
        }
        TODO: find a way to use storage-opt
        --storage-opt is supported only for overlay over xfs with 'pquota' mount option
        """
        flash(f'Container successfully created.<br>'
              f'Your container service will be available soon:<br>'
              f'<a href="https://{host}">https://{host}</a><br>'
              f'Check logs for more information.', 'success')
        return container
    except docker.errors.ContainerError:
        flash('Container Error', 'error')
    except docker.errors.ImageNotFound:
        flash('Image not found', 'error')
    except docker.errors.APIError as e:
        flash(str(e.explanation), 'error')
