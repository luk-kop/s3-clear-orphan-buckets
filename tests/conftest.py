from pytest import fixture
import os

import boto3
from moto import mock_s3


@fixture
def aws_credentials():
    """
    Mocked AWS Credentials for moto.
    """
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'


@fixture
def s3_resource(aws_credentials):
    """
    Create mocked S3 service resource.
    """
    with mock_s3():
        yield boto3.resource('s3')


@fixture
def ec2_client(aws_credentials):
    """
    Create mocked S3 service client.
    """
    with mock_s3():
        yield boto3.client('s3')