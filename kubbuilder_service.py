import constants
import base64
import operations.cloud_ops as cloud_ops
import operations.simple_ops as simple_ops
import operations.docker_ops as docker_ops
import operations.kuber_ops as kuber_ops
import time
import socket

from coralogger import get_default_logger

log = get_default_logger()


def run(executor_location, host_path):
    tag = ('-'.join(host_path)).lower()
    path = constants.LOCAL_PATH + "/" + tag

    download_unzip(executor_location, tag)
    mem_allocation = get_memory_reservation(path, constants.MALLOCATION_FILES)

    time_tag = build_send_registry(tag)

    deploy_to_kubernetes(tag, time_tag, mem_allocation)

    result = executor_status_running(tag, constants.NAMESPACE)

    return {'success': result, 'response': str(tag + "." + constants.DOMAIN)}


def download_unzip(executor_location, tag):
    simple_ops.check_clean_path(constants.LOCAL_PATH, tag)

    full_file_path = cloud_ops.download_file(
        executor_location,
        constants.CLOUD_USER,
        constants.CLOUD_PASSWORD,
        constants.LOCAL_PATH,
        tag)

    simple_ops.unzip_file(
        constants.LOCAL_PATH,
        full_file_path,
        tag)


def build_send_registry(tag):
    time_tag = tag + "-" + str(int(time.time()))
    full_tag = constants.DOCKER_REPO + ":" + time_tag
    code_path = constants.LOCAL_PATH + "/" + tag

    docker_ops.image_build(
        full_tag,
        code_path
    )

    registry_token = cloud_ops.get_registry_token(
        constants.CLOUD_USER,
        constants.CLOUD_PASSWORD,
        constants.DOCKER_REPO)

    docker_ops.push_image(
        time_tag,
        'AWS',
        registry_token,
        constants.DOCKER_REPO)
    return time_tag


def deploy_to_kubernetes(tag, time_tag, mem_allocation):
    image_full_name = constants.DOCKER_REPO + ":" + time_tag
    if constants.INCLUSTER == 'true':
        kuber_ops.connect_kubernetes()
    else:
        kuber_ops.connect_kubernetes(constants.KUBER_CONFIG)

    service = kuber_ops.create_nlu_service_object(tag)
    hpa = kuber_ops.create_nlu_hpa_object(tag)
    ingress = kuber_ops.create_ingress_object(tag, constants.DOMAIN)

    if secret_exist(constants.NLU_SECRET_NAME, constants.NAMESPACE):
        deployment = kuber_ops.create_nlu_deployment_object(
            image_full_name,
            constants.NLU_SECRET_NAME,
            tag,
            mem_allocation)
    else:
        deployment = kuber_ops.create_nlu_deployment_object(
            image_full_name,
            None,
            tag,
            mem_allocation)

    if service_exist(tag, constants.NAMESPACE):
        kuber_ops.patch_nlu_service(service, constants.NAMESPACE)
    else:
        kuber_ops.create_nlu_service(service, constants.NAMESPACE)

    if deployment_exist(tag, constants.NAMESPACE):
        kuber_ops.replace_nlu_deployment(deployment, image_full_name, constants.NAMESPACE, tag)
    else:
        kuber_ops.create_nlu_deployment(deployment, constants.NAMESPACE)

    if hpa_exist(tag, constants.NAMESPACE):
        kuber_ops.replace_nlu_hpa(hpa, constants.NAMESPACE)
    else:
        kuber_ops.create_nlu_hpa(hpa, constants.NAMESPACE)

    if ingress_exist(tag, constants.NAMESPACE):
        kuber_ops.replace_nlu_ingress(ingress, constants.NAMESPACE)
    else:
        kuber_ops.create_nlu_ingress(ingress, constants.NAMESPACE)


def deployment_exist(name, namespace):
    result = True
    try:
        kuber_ops.get_nlu_deployment(name, namespace)
    except Exception as e:
        log.debug("Deployment %s doesn't exist. Exception: %s" % (name, e))
        result = False
    return result


def service_exist(name, namespace):
    result = True
    try:
        kuber_ops.get_nlu_service(name, namespace)
    except Exception as e:
        log.debug("Service %s doesn't exist. Exception: %s" % (name, e))
        result = False
    return result


def hpa_exist(name, namespace):
    result = True
    try:
        kuber_ops.get_nlu_hpa(name, namespace)
    except Exception as e:
        log.debug("HPA %s doesn't exist. Exception: %s" % (name, e))
        result = False
    return result


def ingress_exist(name, namespace):
    result = True
    try:
        kuber_ops.get_nlu_ingress(name, namespace)
    except Exception as e:
        log.debug("Ingress %s doesn't exist. Exception: %s" % (name, e))
        result = False
    return result


def secret_exist(name, namespace):
    result = True
    try:
        kuber_ops.get_nlu_secret(name, namespace)
    except Exception as e:
        log.debug("Secret %s doesn't exist. Exception: %s" % (name, e))
        result = False
    return result


def to_base64(string):
    return base64.b64encode(string.encode('utf-8')).decode("utf-8")


def dict_to_base64(variables_dict):
    for key, value in variables_dict.items():
        variables_dict[key] = to_base64(value)
    return variables_dict


def create_secret(secret_name, variables_dict):
    secret = kuber_ops.create_secret_object(secret_name, dict_to_base64(variables_dict))
    kuber_ops.create_secret(secret)


def update_secret(secret_name, variables_dict):
    secret = kuber_ops.get_nlu_secret(secret_name)
    secret.data.update(dict_to_base64(variables_dict))
    kuber_ops.update_secret(secret)


def run_secret(variables_dict):
    kuber_ops.connect_kubernetes(constants.KUBER_CONFIG)
    secret_name = constants.NLU_SECRET_NAME

    if secret_exist(secret_name):
        update_secret(secret_name, variables_dict)
    else:
        create_secret(secret_name, variables_dict)

    return {'success': True}


def executor_status_running(tag, namespace):
    attempts = range(0, 60)
    fqdn = tag + "." + constants.DOMAIN
    delay = 10

    for attempt in attempts:
        available_replicas_count = int(kuber_ops.get_deployment_status(namespace, tag).status.available_replicas or 0)
        if executor_available(available_replicas_count, fqdn):
            log.debug("Deployment %s created" % str(tag))
            return True
        log.debug("Attempt: %s. Deployment %s isn't ready, sleeping for %s & trying again" % (
            str(attempt),
            str(tag),
            str(delay)))
        time.sleep(delay)

    log.debug("Deployment %s wasn't created" % str(tag))
    return False


def executor_available(available_replicas_count, fqdn):
    if available_replicas_count >= 2 or hostname_resolves(fqdn):
        return True
    else:
        return False


def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False


def get_memory_reservation(path, files_list):
    training_data_size = simple_ops.get_training_data_size(path, files_list)
    memory = (constants.MALLOCATION_COEFICIENT * training_data_size + constants.MALLOCATION_CONSTANT) * constants.MALLOCATION_ALLOWANCE
    return memory
