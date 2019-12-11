import docker.client
import docker.errors
import werkzeug.local
from flask import flash
import multiprocessing
from psutil import virtual_memory


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
        volumes = {
            f'/mnt/{username}':
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
    except docker.errors.ContainerError:
        flash('Container Error', 'error')
    except docker.errors.ImageNotFound:
        flash('Image not found', 'error')
    except docker.errors.APIError as e:
        flash(str(e.explanation), 'error')
