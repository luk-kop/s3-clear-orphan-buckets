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

for var in 1 2; do
  STACK="dummy-bucket-${var}"
  STACK_NAME="${TAG_VALUE}-${STACK}-${STAGE}"

  delete="aws cloudformation delete-stack \
      --stack-name ${STACK_NAME} \
      --region ${REGION}"

  echo ">>> Deleting stack: ${STACK_NAME} <<<"
  $delete
  echo
done
