import boto3
import pytest

from s3_orphan import get_buckets, get_stacks_ids, empty_bucket, delete_bucket, \
    get_buckets_without_key_tag, exit_script


def test_get_stacks_ids_active_stack(cloudformation_stack):
    """
    GIVEN Cloud Formation stack
    WHEN get_stacks_ids is called
    THEN One Cloud Formation stack exist
    """
    stack_ids = get_stacks_ids(aws_region='eu-west-1')
    assert stack_ids
    assert len(stack_ids) == 1


def test_get_stacks_ids_deleted_stack(cloudformation_stack):
    """
    GIVEN Deleted Cloud Formation stack
    WHEN get_stacks_ids with 'deleted' flag is called
    THEN One deleted Cloud Formation stack exist
    """
    cf = boto3.client('cloudformation')
    cf.delete_stack(StackName='test-orphan-s3-buckets')
    stack_ids = get_stacks_ids(aws_region='eu-west-1', deleted=True)
    assert stack_ids
    assert len(stack_ids) == 1


def test_get_stacks_ids_no_deleted_stack(cloudformation_stack):
    """
    GIVEN Cloud Formation stack
    WHEN get_stacks_ids with 'deleted' flag is called
    THEN No deleted Cloud Formation stacks exist
    """
    stack_ids = get_stacks_ids(aws_region='eu-west-1', deleted=True)
    assert not stack_ids
    assert len(stack_ids) == 0


def test_get_stacks_ids_logical_resource_id(cloudformation_stack):
    """
    GIVEN Cloud Formation stack
    WHEN check type of resource created by Cloud Formation stack
    THEN Resource created by Cloud Formation stack is S3 bucket
    """
    cf = boto3.client('cloudformation')
    resources = cf.describe_stack_resources(StackName='test-orphan-s3-buckets')['StackResources']
    assert resources
    assert len(resources) == 1
    logical_resource_id = resources[0]['LogicalResourceId']
    assert logical_resource_id == 'S3Bucket'


def test_get_buckets_tag_environment(s3_buckets):
    """
    GIVEN S3 buckets resources
    WHEN get_buckets with specified tag is called
    THEN No S3 buckets with a specified tag exist
    """
    buckets: list = get_buckets(tag_key='Environment', tag_value='123')
    assert not buckets
    assert len(buckets) == 0


def test_get_buckets_tag_project(s3_buckets):
    """
    GIVEN S3 buckets resources
    WHEN get_buckets with specified tag is called
    THEN Two S3 buckets with a specified tag exist
    """
    buckets: list = get_buckets(tag_key='Project', tag_value='test')
    assert buckets
    assert len(buckets) == 2


def test_get_buckets_tag_stage(s3_buckets):
    """
    GIVEN S3 buckets resources
    WHEN get_buckets with specified tag is called
    THEN Two S3 buckets with a specified tag exist
    """
    buckets: list = get_buckets(tag_key='Stage', tag_value='dev')
    assert buckets
    assert len(buckets) == 2


def test_bucket_with_data_bucket_exist(s3_bucket_with_data):
    """
    GIVEN S3 bucket with objects
    WHEN get_buckets is called
    THEN S3 bucket with specified name exist
    """
    buckets: list = get_buckets(tag_key='Project', tag_value='test-objects')
    assert len(buckets) == 1
    assert buckets[0]['name'] == 'test-orphan-project-objects'


def test_bucket_with_data_objects_exist(s3_bucket_with_data):
    """
    GIVEN S3 bucket with objects
    WHEN Checks whether the bucket contains objects
    THEN S3 bucket contains objects
    """
    bucket_name: str = s3_bucket_with_data
    s3 = boto3.client('s3')
    objects = s3.list_objects_v2(Bucket=bucket_name)['Contents']
    assert objects
    assert len(objects) == 2


def test_empty_bucket_with_data(s3_bucket_with_data):
    """
    GIVEN S3 bucket with objects
    WHEN empty_bucket func on specified S3 bucket is called
    THEN All objects in the S3 bucket have been deleted
    """
    bucket_name: str = s3_bucket_with_data
    # Verify that provided S3 bucket contains objects
    s3 = boto3.client('s3')
    objects_before_deletion = s3.list_objects_v2(Bucket=bucket_name)['Contents']
    assert objects_before_deletion
    # Empty the S3 bucket
    empty_bucket(bucket_name=bucket_name)
    response = s3.list_objects_v2(Bucket=bucket_name)
    objects_after_deletion = response.get('Contents', None)
    assert not objects_after_deletion


def test_empty_bucket_no_data(s3_bucket_empty):
    """
    GIVEN S3 bucket with objects
    WHEN empty_bucket func called on empty S3 bucket
    THEN The exception did not occur
    """
    bucket_name: str = s3_bucket_empty
    try:
        empty_bucket(bucket_name=bucket_name)
    except:
        assert False


def test_delete_bucket_with_data(s3_bucket_empty):
    """
    GIVEN S3 bucket with objects
    WHEN delete_bucket func on specified S3 bucket is called
    THEN Specified S3 bucket is deleted
    """
    bucket_name: str = s3_bucket_empty
    s3 = boto3.client('s3')
    # Verify that provided S3 exist
    buckets_names_before_deletion = [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]
    assert buckets_names_before_deletion
    assert bucket_name in buckets_names_before_deletion
    # Delete bucket
    delete_bucket(bucket_name=bucket_name)
    # Verify that provided S3 not exist
    buckets_names_after_deletion = [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]
    assert buckets_names_after_deletion == []


def test_delete_bucket_no_data(s3_bucket_with_data):
    """
    GIVEN S3 bucket without objects
    WHEN delete_bucket func on specified S3 bucket is called
    THEN Specified S3 bucket is deleted
    """
    bucket_name: str = s3_bucket_with_data
    s3 = boto3.client('s3')
    # Verify that provided S3 exist
    buckets_names_before_deletion = [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]
    assert buckets_names_before_deletion
    assert bucket_name in buckets_names_before_deletion
    # Delete bucket
    delete_bucket(bucket_name=bucket_name)
    # Verify that provided S3 not exist
    buckets_names_after_deletion = [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]
    assert buckets_names_after_deletion == []


def test_delete_bucket_bucket_not_exist(s3_resource):
    """
    GIVEN Non-existent S3 bucket
    WHEN delete_bucket func is called on a non-existent S3 bucket
    THEN The exception is raised
    """
    bucket_name = 'bucket-not-exist'
    with pytest.raises(Exception):
        delete_bucket(bucket_name=bucket_name)


def test_get_buckets_without_key_tag_no_bucket_names_returned_empty_buckets_data(s3_buckets):
    """
    GIVEN S3 buckets resources
    WHEN get_buckets_without_key_tag func
    THEN No S3 bucket names are returned
    """
    # No buckets data is returned
    buckets_data = get_buckets(tag_key='Project', tag_value='no-value')
    buckets_names = get_buckets_without_key_tag(buckets_data=buckets_data, tag_key='No-key')
    assert buckets_names == []


def test_get_buckets_without_key_tag_no_bucket_names_returned(s3_buckets):
    """
    GIVEN S3 buckets resources
    WHEN get_buckets_without_key_tag func
    THEN No S3 bucket names are returned
    """
    # Some buckets data is returned
    buckets_data = get_buckets(tag_key='Project', tag_value='test')
    buckets_names = get_buckets_without_key_tag(buckets_data=buckets_data, tag_key='Project')
    assert buckets_names == []


def test_get_buckets_without_key_tag_two_bucket_names_returned(s3_buckets):
    """
    GIVEN S3 buckets resources
    WHEN get_buckets_without_key_tag func
    THEN No S3 bucket names are returned
    """
    # Some buckets data is returned
    buckets_data = get_buckets(tag_key='Project', tag_value='test')
    buckets_names = get_buckets_without_key_tag(buckets_data=buckets_data, tag_key='No-key')
    assert buckets_names
    assert len(buckets_names) == 2
    assert 'test-orphan-project-stage' in buckets_names
    assert 'test-orphan-project-no-stage' in buckets_names


def test_is_action_allowed_false():
    """
    GIVEN exit_script func
    WHEN exit_script func is called
    THEN sys.exit() is called without exit code
    """
    # SystemExit should be raised
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        exit_script()
    assert pytest_wrapped_e.type == SystemExit
    assert not pytest_wrapped_e.value.code
