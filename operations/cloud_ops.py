from urllib.parse import urlparse
import boto3
import base64


def download_file(url, cloud_user, cloud_password, local_path, tag):
    parsed_url = urlparse(url)
    path = parsed_url.path.split("/")
    bucket_name = path[1]

    key_name = parsed_url.path[len(path[1])+2:]
    full_path = local_path+"/"+tag+"/"+path[-1]
    session = boto3.Session(
        aws_access_key_id=cloud_user,
        aws_secret_access_key=cloud_password,
        region_name='us-west-2')
    s3_client = session.resource('s3')
    s3_client.Bucket(bucket_name).download_file(key_name,full_path)

    return full_path


def get_registry_token(cloud_user,cloud_password,registry):
    session = boto3.Session(
        aws_access_key_id=cloud_user,
        aws_secret_access_key=cloud_password,
        region_name='us-west-2')
    ecr_client = session.client(
        service_name='ecr',
        region_name='us-west-2')

    response = ecr_client.get_authorization_token(registryIds=[registry.split(".")[0]])
    token = (base64.b64decode(response['authorizationData'][0]['authorizationToken'])).decode("utf-8").split(":")[1]

    return token



