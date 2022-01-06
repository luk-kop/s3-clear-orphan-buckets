#!/bin/bash

PROJECT="find-orphan"
STAGE="dev"
REGION="eu-west-1"

for var in 1 2; do
  STACK="dummy-bucket-${var}"
  STACK_NAME="${PROJECT}-${STACK}-${STAGE}"

  delete="aws cloudformation delete-stack \
      --stack-name ${STACK_NAME} \
      --region ${REGION}"

  echo ">>> Deleting stack: ${STACK_NAME} <<<"
  $delete
  echo
done
