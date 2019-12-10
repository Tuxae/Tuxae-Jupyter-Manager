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
