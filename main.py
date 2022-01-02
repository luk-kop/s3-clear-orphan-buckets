import boto3


def get_active_stacks_ids() -> list:
    """
    Return the list of current running CloudFormation stacks ids.
    """
    client = boto3.client('cloudformation')
    response = client.list_stacks(
        StackStatusFilter=[
            'CREATE_IN_PROGRESS',
            'CREATE_COMPLETE'
        ]
    )
    stack_ids = [stack['StackId'] for stack in response['StackSummaries']]
    return stack_ids


def check_stack_status(stack_id: str, active_stacks_ids: list) -> bool:
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


def get_buckets_without_cf_tag(buckets_data: list) -> list:
    """
    Returns list of bucket names without CloudFormation stack-id tag assigned.
    """
    matching_buckets_names = []
    cf_tag_key = 'aws:cloudformation:stack-id'
    for bucket in buckets_data:
        bucket_name = bucket['name']
        bucket_tags = bucket['tags']
        stack_id_tag_present = False
        for tag in bucket_tags:
            if tag['Key'] == cf_tag_key:
                stack_id_tag_present = True
        if not stack_id_tag_present:
            matching_buckets_names.append(bucket_name)
    return matching_buckets_names


if __name__ == '__main__':
    buckets_data = get_buckets(tag_key='Project', tag_value='memes-generator')
    bucket_names = get_buckets_without_cf_tag(buckets_data=buckets_data)
    print(bucket_names)