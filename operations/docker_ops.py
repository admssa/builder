import docker
from coralogger import get_default_logger

log = get_default_logger()


def remove_old_images():
    client = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
    all_images = client.images.list()
    for i in all_images:
        if i.tags != ['python:3.5-jessie']:
            log.debug("image %s removed" % str(i.tags) )
            client.images.remove(i.short_id.split(":")[-1], force=True)
        else:
            log.debug("No images to remove")


def image_build(full_tag, code_path):
    client = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
    response = client.images.build(
        path=code_path,
        dockerfile=code_path + "/Dockerfile.nlu",
        tag=full_tag)
    log.debug("Docker image build, response: %s" % response)


def push_image(tag_name, repo_user, repo_password, docker_repo):
    client = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
    client.login(
        username=repo_user,
        password=repo_password,
        registry=docker_repo,
        email=None,
        reauth=True)

    client.images.push(
        repository=docker_repo,
        tag=tag_name)
    log.debug("Image %s:%s pushed successful" % (docker_repo, tag_name))
    return tag_name
