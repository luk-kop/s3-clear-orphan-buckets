import argparse
import json

from s3_orphan import get_buckets


def get_bucket_names(tag_key: str, tag_value: str) -> list:
    """
    Returns the list of S3 bucket names with the relevant tags.
    """
    buckets_data = get_buckets(tag_key=tag_key, tag_value=tag_value)
    if not buckets_data:
        return []
    return [bucket['name'] for bucket in buckets_data]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Displays a list of S3 buckets with the specified tag'
    )
    # Arguments
    parser.add_argument('-k',
                        '--tag-key',
                        type=str,
                        required=True,
                        help='list S3 bucket names with specified tag key')
    parser.add_argument('-v',
                        '--tag-value',
                        type=str,
                        required=True,
                        help='list S3 bucket names with specified tag value')
    # Parse arguments
    args = parser.parse_args()
    tag_key_argument = args.tag_key
    tag_value_argument = args.tag_value

    # Run script's main func
    bucket_names = get_bucket_names(tag_key=tag_key_argument, tag_value=tag_value_argument)
    print(json.dumps(bucket_names))