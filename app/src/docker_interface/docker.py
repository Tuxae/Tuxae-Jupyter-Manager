import docker.client
import docker.errors
import werkzeug.local
from flask import flash

from src.db_interface.secret import DOCKER_REGISTRY_URI, SERVER_DOMAIN, DEFAULT_ADMIN_EMAIL
from src.misc.functions import sanitize_username, generate_random_number


def get_docker_containers(docker_client: docker.client.DockerClient):
    all_containers = docker_client.containers.list(all=True)
    containers = []
    for container in all_containers:
        if not container.image.tags:
            continue
        if not container.image.tags[0].startswith(DOCKER_REGISTRY_URI):
            continue
        containers.append(container)
    return containers


def get_docker_images(docker_client: docker.client.DockerClient):
    all_images = docker_client.images.list()
    images = []
    for image in all_images:
        if not image.attrs['RepoTags']:
            continue
        if not image.attrs['RepoTags'][0].startswith(DOCKER_REGISTRY_URI):
            continue
        images.append(image)
    return images


def check_image(image: str) -> bool:
    return image.startswith(DOCKER_REGISTRY_URI)


def deploy_container(docker_client: docker.client.DockerClient, image: str, current_user: werkzeug.local.LocalProxy) \
        -> None:
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
        volumes = {
            f'/home/{username}':
                {
                    'bind': '/home/jovyan/work',
                    'mode': 'rw'
                }
        }
    try:
        docker_client.containers.run(
            image,
            detach=True,
            environment=environment,
            volumes=volumes
        )
        flash('Container successfully created', 'success')
    except docker.errors.ContainerError:
        flash('Container Error', 'error')
    except docker.errors.ImageNotFound:
        flash('Image not found', 'error')
    except docker.errors.APIError as e:
        flash(str(e.explanation), 'error')
