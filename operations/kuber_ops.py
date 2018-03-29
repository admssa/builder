from kubernetes import client, config
from coralogger import get_default_logger

log = get_default_logger()


def connect_kubernetes(config_file=''):
    if config_file == '':
        config.load_incluster_config()
    else:
        config.load_kube_config(config_file=config_file)


def create_ingress_object(tag_name, domain):
    rule = client.V1beta1IngressRule(
        host=tag_name + "." + domain,
        http=client.V1beta1HTTPIngressRuleValue(
            paths=[client.V1beta1HTTPIngressPath(
                backend=client.V1beta1IngressBackend(
                    service_name=tag_name,
                    service_port=80
                )

            )])

    )
    spec = client.V1beta1IngressSpec(
        rules=[rule]
    )

    ingress = client.V1beta1Ingress(
        api_version="extensions/v1beta1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name=tag_name),
        spec=spec
    )
    return ingress


def create_secret_object(name, variables_dict):
    secret = client.V1Secret(
        api_version="v1",
        kind="Secret",
        metadata=client.V1ObjectMeta(name=name),
        type="Opaque",
        data=variables_dict)
    return secret


def create_env_list(secret_name):
    envs_list = []
    secret = get_nlu_secret(secret_name, namespace="nlu")
    for k, v in secret.data.items():
        envs_list.append(client.V1EnvVar(
            name=k,
            value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(
                    key=k,
                    name=secret_name))))
    return envs_list


def create_nlu_deployment_object(image_full_name, secret_name, tag_name, mem_allocation):
    memory = str(int(mem_allocation)) + "Mi"
    mcpu = "80m"
    if secret_name is not None:
        env_list = create_env_list(secret_name)
    else:
        env_list = [client.V1EnvVar(name="no-nlu-variables", value="true")]

    resourse = client.V1ResourceRequirements(
        requests={"memory": memory, "cpu": mcpu},
        limits={"memory": memory})
    liveness = client.V1Probe(
        http_get=client.V1HTTPGetAction(
            path="/healthcheck",
            port=5000),
        failure_threshold=3,
        period_seconds=3,
        initial_delay_seconds=7,
        timeout_seconds=2)
    container = client.V1Container(
        name=tag_name,
        image=image_full_name,
        image_pull_policy="IfNotPresent",
        liveness_probe=liveness,
        resources=resourse,
        ports=[client.V1ContainerPort(container_port=5000)],
        env=env_list)
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": tag_name}),
        spec=client.V1PodSpec(containers=[container]))
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=1,
        template=template)
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=tag_name),
        spec=spec)
    return deployment


def create_nlu_hpa_object(hpa_name):
    deployment = client.V1CrossVersionObjectReference(
        api_version="extensions/v1beta1",
        kind="Deployment",
        name=hpa_name)
    spec = client.V1HorizontalPodAutoscalerSpec(
        max_replicas=5,
        min_replicas=2,
        scale_target_ref=deployment,
        target_cpu_utilization_percentage=100)
    hpa = client.V1HorizontalPodAutoscaler(
        api_version="autoscaling/v1",
        kind="HorizontalPodAutoscaler",
        metadata=client.V1ObjectMeta(name=hpa_name),
        spec=spec)
    return hpa


def get_nlu_deployment(deployment_name, namespace):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.read_namespaced_deployment(
        name=deployment_name,
        namespace=namespace)
    return api_response


def create_nlu_deployment(deployment, namespace):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=namespace)
    log.debug("Deployment created %s. status='%s'" % (deployment.metadata.name, str(api_response.status)))
    return api_response


def replace_nlu_deployment(deployment, image_full_name, namespace, tag_name):
    deployment.spec.template.spec.containers[0].image = image_full_name
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.replace_namespaced_deployment(
        name=tag_name,
        namespace=namespace,
        body=deployment)
    log.debug("Deployment updated %s with image %s. status='%s'" % (
        deployment.metadata.name, image_full_name, str(api_response.status)))
    return api_response


def delete_nlu_deployment(tag_name, namespace):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.delete_namespaced_deployment(
        name=tag_name,
        namespace=namespace,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    log.debug("Deployment deleted %s. status='%s'" % (tag_name, str(api_response.status)))
    return api_response


def create_nlu_service_object(tag_name):
    service = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name=tag_name))
    spec = client.V1ServiceSpec(
        selector={"app": tag_name},
        ports=[client.V1ServicePort(protocol="TCP", port=80, target_port=5000)],
        type="ClusterIP")
    service.spec = spec
    return service


def get_nlu_ingress(ingress_name, namespace):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.read_namespaced_ingress(
        name=ingress_name,
        namespace=namespace
    )
    return api_response


def create_nlu_ingress(ingress, namespace):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.create_namespaced_ingress(namespace=namespace, body=ingress)
    log.debug("Ingress created %s. status='%s'" % (ingress.metadata.name, str(api_response.status)))
    return api_response


def delete_nlu_ingress(ingress_name, namespace):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.delete_namespaced_ingress(name=ingress_name, namespace=namespace)
    log.debug("Service deleted %s. status='%s'" % (ingress_name, str(api_response.status)))
    return api_response


def replace_nlu_ingress(ingress, namespace):
    api_instance = client.ExtensionsV1beta1Api()
    api_response = api_instance.replace_namespaced_ingress(
        name=ingress.metadata.name,
        namespace=namespace,
        body=ingress)
    log.debug("ingress %s replaced. status='%s'" % (ingress.metadata.name, str(api_response.status)))
    return api_response


def get_nlu_service(service_name, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.read_namespaced_service(
        name=service_name,
        namespace=namespace)
    return api_response


def create_nlu_service(service, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.create_namespaced_service(
        namespace=namespace,
        body=service)
    log.debug("Service created %s. status='%s'" % (service.metadata.name, str(api_response.status)))
    return api_response


def delete_nlu_service(service_name, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.delete_namespaced_service(
        name=service_name,
        namespace=namespace)
    log.debug("Service deleted %s. status='%s'" % (service_name, str(api_response.status)))
    return api_response


def patch_nlu_service(service, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.patch_namespaced_service(
        name=service.metadata.name,
        namespace=namespace,
        body=service)
    log.debug("Service patched %s. status='%s'" % (service.metadata.name, str(api_response.status)))
    return api_response


def replace_nlu_service(service, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.replace_namespaced_service(
        name=service.metadata.name,
        namespace=namespace,
        body=service)
    log.debug("Service replaced %s. status='%s'" % (service.metadata.name, str(api_response.status)))
    return api_response


def get_nlu_hpa(hpa_name, namespace):
    api_instance = client.AutoscalingV1Api()
    api_response = api_instance.read_namespaced_horizontal_pod_autoscaler(
        name=hpa_name,
        namespace=namespace)
    return api_response


def create_nlu_hpa(hpa, namespace):
    api_instance = client.AutoscalingV1Api()
    api_response = api_instance.create_namespaced_horizontal_pod_autoscaler(
        body=hpa,
        namespace=namespace)
    log.debug("Horizontal pod autoscaler created %s. status='%s'" % (hpa.metadata.name, str(api_response.status)))
    return api_response


def delete_nlu_hpa(hpa_name, namespace):
    api_instance = client.AutoscalingV1Api()
    api_response = api_instance.delete_namespaced_horizontal_pod_autoscaler(
        name=hpa_name,
        namespace=namespace)
    log.debug("Horizontal pod autoscaler deleted %s. status='%s'" % (hpa_name, str(api_response.status)))
    return api_response


def replace_nlu_hpa(hpa, namespace):
    api_instance = client.AutoscalingV1Api()
    api_response = api_instance.replace_namespaced_horizontal_pod_autoscaler(
        name=hpa.metadata.name,
        namespace=namespace,
        body=hpa)
    log.debug("Horizontal pod autoscaler replaced %s. status='%s'" % (hpa.metadata.name, str(api_response.status)))
    return api_response


def create_secret(secret, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.create_namespaced_secret(
        namespace=namespace,
        body=secret)
    log.debug("Secret created %s. status='%s'" % (secret.metadata.name, str(api_response.metadata.name)))
    return api_response


def delete_secret(secret_name, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.delete_namespaced_secret(
        namespace=namespace,
        name=secret_name)
    log.debug("Secret deleted %s. status='%s'" % (secret_name, str(api_response.metadata.name)))
    return api_response


def update_secret(secret, namespace):
    api_instance = client.CoreV1Api()
    api_response = api_instance.patch_namespaced_secret(
        namespace=namespace,
        name=secret.metadata.name,
        body=secret)
    log.debug("Secret updated %s. status='%s'" % (secret.metadata.name, str(api_response.data)))
    return api_response


def get_nlu_secret(secret_name, namespace):
    api_instance = client.CoreV1Api()
    secret = api_instance.read_namespaced_secret(name=secret_name, namespace=namespace)
    return secret


def gat_hpa_list(namespace):
    api_instance = client.AutoscalingV1Api()
    hpa_list = api_instance.list_namespaced_horizontal_pod_autoscaler(namespace=namespace)
    return hpa_list


def get_services_list(namespace):
    api_instance = client.CoreV1Api()
    services_list = api_instance.list_namespaced_service(namespace=namespace)
    return services_list


def get_deployments_list(namespace):
    api_instance = client.ExtensionsV1beta1Api()
    deployments_list = api_instance.list_namespaced_deployment(namespace=namespace)
    return deployments_list


def get_secrets_list(namespace):
    api_instance = client.CoreV1Api()
    secrets_list = api_instance.list_namespaced_secret(namespace=namespace)
    return secrets_list


def get_deployment_status(namespace, deployment_name):
    api_instance = client.AppsV1beta1Api()
    deploy_status = api_instance.read_namespaced_deployment_status(name=deployment_name,
                                                                   namespace=namespace)
    return deploy_status
