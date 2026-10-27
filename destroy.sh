#!/usr/bin/env bash
# Deletes everything this project created. Run after your demo.
set -e
STACK="cloud-quiz"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null || true)}}"
REGION="${REGION:-ap-south-1}"
ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
BUCKET="cloud-quiz-artifacts-${ACCOUNT}-${REGION}"

aws cloudformation delete-stack --stack-name "$STACK" --region "$REGION"
aws cloudformation wait stack-delete-complete --stack-name "$STACK" --region "$REGION"
aws s3 rb "s3://$BUCKET" --force || true
echo "Deleted."
