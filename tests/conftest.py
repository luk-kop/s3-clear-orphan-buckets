from pytest import fixture
import os
import json
from pathlib import Path
from typing import List

import boto3
from moto import mock_s3, mock_cloudformation


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
def s3_client(aws_credentials):
    """
    Create mocked S3 service client.
    """
    with mock_s3():
        yield boto3.client('s3')


@fixture
def cf_client(aws_credentials):
    """
    Create mocked CloudFormation client.
    Note: Python packages necessary for CloudFormation mocking: cfn-lint, docker, pyyaml
    """
    with mock_cloudformation():
        yield boto3.client('cloudformation')


def _parse_template(template: str) -> str:
    """
    Parse CloudFormation template - YAML to string.
    """
    with open(template) as template_file:
        template_data = template_file.read()
    return template_data


def _parse_parameters(parameters: str) -> List[dict]:
    """
    Parse CloudFormation template parameters - JSON to list of dicts.
    """
    with open(parameters) as parameter_file:
        parameter_data = json.load(parameter_file)
    return parameter_data


@fixture
def cloudformation_stack(cf_client, s3_client):
    """
    Dummy CloudFormation stack.
    """
    stack_name = 'test-orphan-s3-buckets'
    template_path = Path(__file__).resolve().parents[1].joinpath('cloudformation/templates/bucket.yaml')
    parameters_path = Path(__file__).resolve().parents[1].joinpath('cloudformation/parameters/dummy-bucket-1-dev.json')
    template_data: str = _parse_template(template_path)
    parameter_data: List[dict] = _parse_parameters(parameters_path)
    params = {
        'StackName': stack_name,
        'TemplateBody': template_data,
        'Parameters': parameter_data,
    }
    cf_client.create_stack(**params)
    yield


@fixture
def s3_buckets(s3_client):
    """
    Dummy s3 buckets.
    """
    tags = {
        'project': {
            'Key': 'Project',
            'Value': 'test'
        },
        'stage': {
            'Key': 'Stage',
            'Value': 'dev'
        }
    }
    buckets_data = [
        {
            'name': 'test-orphan-project-stage',
            'tags': [
                tags['project'],
                tags['stage']
            ]
        },
        {
            'name': 'test-orphan-project-no-stage',
            'tags': [
                tags['project'],
            ]
        },
        {
            'name': 'test-orphan-no-project-stage',
            'tags': [
                tags['stage'],
            ]
        },
    ]
    # Deploy 3 S3 buckets
    for bucket_data in buckets_data:
        bucket_name: str = bucket_data['name']
        bucket_tags: list = bucket_data['tags']
        # Create bucket
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': 'eu-west-1'
            }
        )
        # Add tags
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': bucket_tags
            }
        )
    yield


@fixture
def s3_bucket_with_data(s3_client):
    """
    Dummy s3 buckets with objects.
    """
    bucket_name = 'test-orphan-project-objects'
    bucket_tag = {
        'Key': 'Project',
        'Value': 'test-objects'
    },
    # Create bucket
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-1'
        }
    )
    # Add tags
    s3_client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            'TagSet': bucket_tag
        }
    )
    # Add objects to bucket
    object_binary_data = b'The quick brown fox jumps over the lazy dog'
    objects_keys = ['test/object-one', 'test/object-two']
    for object_key in objects_keys:
        s3_client.put_object(
            Body=object_binary_data,
            Bucket=bucket_name,
            Key=object_key
        )
    yield bucket_name


@fixture
def s3_bucket_empty(s3_client):
    """
    Dummy empty s3 buckets.
    """
    bucket_name = 'test-orphan-project-empty'
    bucket_tag = {
        'Key': 'Project',
        'Value': 'test-no-objects'
    },
    # Create bucket
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': 'eu-west-1'
        }
    )
    # Add tags
    s3_client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            'TagSet': bucket_tag
        }
    )
    yield bucket_name
