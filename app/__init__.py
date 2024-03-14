import base64
import logging
import os
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch
from opensearchpy import RequestsHttpConnection
from pydantic import BaseSettings

from app.index.service import CSIndexingService

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

env_name = os.getenv("ACTIVE_ENVIRONMENT")


def get_logger(name) -> logging.Logger:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return logger


class Settings(BaseSettings):
    app_name: str = "ElectricSearch"
    os_host: str
    os_port: int = 443
    os_user_name: str
    os_region: str

    class Config:
        print("Base directory->", BASE_DIR)
        env_file = f"{BASE_DIR}/conf/{env_name}.env"


@lru_cache()
def app_settings():
    return Settings()


settings = app_settings()  # invoke method to cache the configuration.

region = settings.os_region
service = 'es'
credentials = boto3.Session().get_credentials()
# aws_auth = AWS4Auth(refreshable_credentials=credentials, region=region, service=service)
admin_pwd: str


@lru_cache()
def get_secret() -> str:
    secret_name = "OpenSearchAdminPwd"
    region_name = "ap-south-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            return str(base64.b64decode(get_secret_value_response['SecretBinary']))

    # Your code goes here.


os_client = OpenSearch(
    hosts=[settings.os_host],
    http_auth=(settings.os_user_name, get_secret()),
    use_ssl=True,
    verify_certs=True,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
    connection_class=RequestsHttpConnection
)


def get_os_search_service():
    if os_client is None:
        raise RuntimeError("OpenSearch client was not initialized.")
    print(os_client.info())
    return CSIndexingService(os_client=os_client, logger=get_logger(name="app.search.service"))
