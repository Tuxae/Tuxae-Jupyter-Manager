import docker.client

from src.db_interface.secret import DOCKER_REGISTRY_URI


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
    images = docker_client.images.list()
    return [image for image in images if image.attrs['RepoTags'][0].startswith(DOCKER_REGISTRY_URI)]


def check_image(image: str) -> bool:
    return image.startswith(DOCKER_REGISTRY_URI)
