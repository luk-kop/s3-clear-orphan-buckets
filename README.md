# S3 orphan buckets finder

[![Python 3.8.10](https://img.shields.io/badge/python-3.8.10-blue.svg)](https://www.python.org/downloads/release/python-377/)
[![Boto3](https://img.shields.io/badge/Boto3-1.20.26-blue.svg)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
![status](https://github.com/luk-kop/s3-orphan-buckets-finder/actions/workflows/main.yml/badge.svg)


> The **S3 clear orphan buckets** is a simple script that allows you to find and delete S3 buckets that remain after deleting the Cloud Formation stacks with which they were created.
> This situation occurs when `DeletionPolicy` on S3 bucket object in the Cloud Formation template is set to `Retain`.

## Features
- The script only performs actions on S3 buckets with a specific tag (key & value) and after deleting the Cloud Formation stack they were part of. 
- S3 buckets can be **listed** or **deleted**.
- The script must be executed with the following arguments:
  - tag key (`-k` or `--tag-key`);
  - tag value (`-v` or `--tag-value`).
- As a result of invoking the script you will get the S3 bucket names, against which the action was taken (if any).

## Requirements
- Python third party packages: [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- Before using the script, you need to set up default AWS region value and valid authentication credentials for your AWS account (programmatic access) using either the IAM Management Console or the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html) tool.
- The entity running the script should have the appropriate permissions to:
  - create, update & delete Cloud Formation stacks;
  - create, delete & list S3 buckets;
  - put, list & delete objects in S3 buckets.
    
## Installation with venv
The script can be run locally with virtualenv tool. Run following commands in order to create virtual environment and install the required packages.
```bash
$ virtualenv venv
# or
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Running the script
Script usage (detailed help):
```bash
(venv) $ python s3_orphan.py --help
usage: s3_orphan.py [-h] {list,delete} -k TAG_KEY -v TAG_VALUE

The orphan S3 bucket finder

positional arguments:
  {list,delete}         action performed on a found S3 bucket

optional arguments:
  -h, --help            show this help message and exit
  -k TAG_KEY, --tag-key TAG_KEY
                        perform action on S3 buckets with specified tag key
  -v TAG_VALUE, --tag-value TAG_VALUE
                        perform action on S3 buckets with specified tag value
```
You can start the script using one of the following examples:
```bash
# List S3 buckets with tag Key: 'Project' and Value: 'find-orphan' assigned.
python s3_orphan.py list -k Project -v find-orphan
# You should get the similar output:
S3 bucket "find-orphan-dummy-bucket-1-dev-s3bucket-abc12a34fb5c" is orphaned.
S3 bucket "find-orphan-dummy-bucket-2-dev-s3bucket-1ab2cde3456fg" is orphaned.
# or if no action has been taken
Nothing to do...

# Delete S3 buckets with tag Key: 'Project' and Value: 'find-orphan' assigned.
python s3_orphan.py delete -k Project -v find-orphan
# You should get the similar output:
S3 bucket "find-orphan-dummy-bucket-1-dev-s3bucket-abc12a34fb5c" deleted.
S3 bucket "find-orphan-dummy-bucket-2-dev-s3bucket-1ab2cde3456fg" deleted.
# or if no action has been taken
Nothing to do...
```