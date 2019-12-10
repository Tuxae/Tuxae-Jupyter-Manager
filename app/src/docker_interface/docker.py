import docker.client

from src.db_interface.secret import DOCKER_REGISTRY_URI


def get_docker_containers(docker_client: docker.client.DockerClient):
    containers = docker_client.containers.list(all=True)
    return [container for container in containers if container.image.tags[0].startswith(DOCKER_REGISTRY_URI)]


def get_docker_images(docker_client: docker.client.DockerClient):
    images = docker_client.images.list()
    return [image for image in images if image.attrs['RepoTags'][0].startswith(DOCKER_REGISTRY_URI)]
