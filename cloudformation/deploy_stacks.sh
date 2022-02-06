#!/bin/bash


STAGE="dev"
REGION="eu-west-1"

if [[ $# -eq 0 ]]
then
  TAG_KEY="Project"
  TAG_VALUE="find-orphan"
elif [[ $# -eq 2 ]]
then
  TAG_KEY=$1
  TAG_VALUE=$2
else
  echo "usage: $0 [TAG_KEY] [TAG_VALUE]"
  echo "default: TAG_KEY=Project & TAG_VALUE=find-orphan"
  exit 1
fi

buckets=()

for var in 1 2
do
  STACK="dummy-bucket-${var}"
  TEMPLATE="bucket"
  STACK_NAME="${TAG_VALUE}-${STACK}-${STAGE}"

  TEMPLATE_FILE="templates/${TEMPLATE}.yaml"
  PARAM_FILE="parameters/${STACK}-${STAGE}.json"

  deploy="aws cloudformation deploy \
      --template-file ${TEMPLATE_FILE} \
      --stack-name ${STACK_NAME} \
      --no-fail-on-empty-changeset \
      --parameter-overrides file://${PARAM_FILE} \
      --region ${REGION} \
      --tags ${TAG_KEY}=${TAG_VALUE} Stage=${STAGE}"

  echo ">>> Deploying stack: ${STACK_NAME} <<<"
  $deploy

  bucket_name=$(aws cloudformation describe-stacks \
      --output text --stack-name $STACK_NAME \
      --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue")
  echo
  echo "Uploading files to bucket: ${bucket_name}"
  aws s3 sync content/ "s3://${bucket_name}"

  buckets+=("$bucket_name")
  echo
done

# Outputs
echo ">>> Outputs <<<"
echo "Bucket names:"
for bucket in "${buckets[@]}"
do
  echo " - ${bucket}"
done
echo "Tags to use:"
echo " - ${TAG_KEY} = ${TAG_VALUE}"
echo " - Stage = ${STAGE}"