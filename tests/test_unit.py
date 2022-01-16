import boto3

from s3_orphan import get_buckets, get_stacks_ids


def test_get_stacks_ids_active_stack(cloudformation_stack):
    """
    GIVEN
    WHEN
    THEN
    """
    stack_ids = get_stacks_ids(aws_region='eu-west-1')
    assert stack_ids
    assert len(stack_ids) == 1


def test_get_stacks_ids_deleted_stack(cloudformation_stack):
    cf = boto3.client('cloudformation')
    cf.delete_stack(StackName='test-orphan-s3-buckets')
    stack_ids = get_stacks_ids(aws_region='eu-west-1', deleted=True)
    assert stack_ids
    assert len(stack_ids) == 1


def test_get_stacks_ids_no_deleted_stack(cloudformation_stack):
    stack_ids = get_stacks_ids(aws_region='eu-west-1', deleted=True)
    assert not stack_ids
    assert len(stack_ids) == 0


def test_get_stacks_ids_logical_resource_id(cloudformation_stack):
    cf = boto3.client('cloudformation')
    resources = cf.describe_stack_resources(StackName='test-orphan-s3-buckets')['StackResources']
    assert resources
    assert len(resources) == 1
    logical_resource_id = resources[0]['LogicalResourceId']
    assert logical_resource_id == 'S3Bucket'


def test_get_buckets_tag_environment(s3_buckets):
    buckets: list = get_buckets(tag_key='Environment', tag_value='123')
    assert not buckets
    assert len(buckets) == 0


def test_get_buckets_tag_project(s3_buckets):
    buckets: list = get_buckets(tag_key='Project', tag_value='test')
    assert buckets
    assert len(buckets) == 2


def test_get_buckets_tag_stage(s3_buckets):
    buckets: list = get_buckets(tag_key='Stage', tag_value='dev')
    assert buckets
    assert len(buckets) == 2