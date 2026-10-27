#!/usr/bin/env bash
# Deploys the whole app with the AWS CLI only (works in AWS CloudShell).
# Usage: ./deploy.sh
set -e
STACK="cloud-quiz"
REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null || true)}}"
REGION="${REGION:-ap-south-1}"
ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
BUCKET="cloud-quiz-artifacts-${ACCOUNT}-${REGION}"

# Bucket used only to upload the Lambda code
if ! aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null; then
  if [ "$REGION" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "$BUCKET" --region "$REGION"
  else
    aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
      --create-bucket-configuration LocationConstraint="$REGION"
  fi
fi

aws cloudformation package --template-file template.yaml \
  --s3-bucket "$BUCKET" --output-template-file packaged.yaml --region "$REGION"

aws cloudformation deploy --template-file packaged.yaml \
  --stack-name "$STACK" --capabilities CAPABILITY_IAM --region "$REGION"

echo
aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='QuizUrl'].OutputValue" --output text
