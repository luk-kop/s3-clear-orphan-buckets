import argparse
import sys

import boto3

from constants import STACK_ACTIVE_STATUSES


def get_stacks_ids(aws_region: str, deleted: bool = False) -> list:
    """
    Return the list of current active or deleted CloudFormation stacks ids (ARNs).
    Note: Deleted stacks are keep in CloudFormation history for 90 days.
    """
    if deleted:
        stack_statuses: list = ['DELETE_COMPLETE']
    else:
        stack_statuses: list = STACK_ACTIVE_STATUSES
    client = boto3.client('cloudformation', region_name=aws_region)
    response = client.list_stacks(
        StackStatusFilter=stack_statuses
    )
    stack_ids = [stack['StackId'] for stack in response['StackSummaries']]
    return stack_ids


def check_stack_status(stack_id: str, active_stacks_ids: list) -> bool:
    """
    Check whether provided CloudFormation stack id is active.
    """
    return stack_id in active_stacks_ids


def get_buckets(tag_key: str, tag_value: str) -> list:
    """
    Return list of buckets data with specified tag key & value.
    """
    matching_buckets = []
    client = boto3.client('s3')
    buckets = client.list_buckets()['Buckets']
    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            tags = client.get_bucket_tagging(Bucket=bucket_name)['TagSet']
        except client.exceptions.ClientError:
            continue
        for tag in tags:
            if tag['Key'] == tag_key and tag['Value'] == tag_value:
                bucket_data = {
                    'name': bucket_name,
                    'tags': tags
                }
                matching_buckets.append(bucket_data)
    return matching_buckets


def empty_bucket(bucket_name: str) -> None:
    """
    Empty S3 bucket - also with versioning enabled.
    """
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(bucket_name)
    bucket_versioning = s3.BucketVersioning(bucket_name)
    if bucket_versioning.status == 'Enabled':
        s3_bucket.object_versions.delete()
    else:
        s3_bucket.objects.all().delete()


def delete_bucket(bucket_name: str) -> None:
    """
    Delete S3 bucket with provided name.
    """
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(bucket_name)
    # Empty bucket before deletion
    empty_bucket(bucket_name=bucket_name)
    s3_bucket.delete()
    print(f'S3 bucket "{bucket_name}" deleted.')


def get_buckets_without_key_tag(buckets_data: list, tag_key: str) -> list:
    """
    Returns list of bucket names without specified tag key assigned.
    """
    matching_buckets_names = []
    for bucket in buckets_data:
        bucket_name = bucket['name']
        bucket_tags = bucket['tags']
        stack_id_tag_present = False
        for tag in bucket_tags:
            if tag['Key'] == tag_key:
                stack_id_tag_present = True
        if not stack_id_tag_present:
            matching_buckets_names.append(bucket_name)
    return matching_buckets_names


def exit_script() -> None:
    """
    exit the script if there is no relevant data.
    """
    print('Nothing to do...')
    sys.exit()


def main(action: str, tag_key: str, tag_value: str) -> None:
    """
    Script's main func.
    """
    buckets_data = get_buckets(tag_key=tag_key, tag_value=tag_value)
    if not buckets_data:
        exit_script()
    # CloudFormation stack-id tag key (system tag)
    cf_tag_key = 'aws:cloudformation:stack-id'
    bucket_names = get_buckets_without_key_tag(buckets_data=buckets_data, tag_key=cf_tag_key)
    if not bucket_names:
        exit_script()
    for bucket_name in bucket_names:
        if action == 'delete':
            delete_bucket(bucket_name=bucket_name)
        else:
            print(f'S3 bucket "{bucket_name}" is orphaned.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='The orphan S3 bucket finder',
        usage='s3_orphan.py [-h] {list,delete} -k TAG_KEY -v TAG_VALUE'
    )
    # Positional argument
    parser.add_argument('action',
                        choices=['list', 'delete'],
                        help='action performed on a found S3 bucket')
    parser.add_argument('-k',
                        '--tag-key',
                        type=str,
                        required=True,
                        help='perform action on S3 buckets with specified tag key')
    parser.add_argument('-v',
                        '--tag-value',
                        type=str,
                        required=True,
                        help='perform action on S3 buckets with specified tag value')
    # Parse arguments
    args = parser.parse_args()
    action_argument = args.action
    tag_key_argument = args.tag_key
    tag_value_argument = args.tag_value

    # Run script's main func
    main(action=action_argument, tag_key=tag_key_argument, tag_value=tag_value_argument)