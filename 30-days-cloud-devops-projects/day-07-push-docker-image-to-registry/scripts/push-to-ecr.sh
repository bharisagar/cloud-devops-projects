#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-v1}"
AWS_REGION="${AWS_REGION:-ap-south-1}"
ECR_REPOSITORY="${ECR_REPOSITORY:-day-07-registry-api}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE="${REGISTRY}/${ECR_REPOSITORY}:${TAG}"

aws ecr describe-repositories \
  --repository-names "${ECR_REPOSITORY}" \
  --region "${AWS_REGION}" >/dev/null 2>&1 || \
aws ecr create-repository \
  --repository-name "${ECR_REPOSITORY}" \
  --image-scanning-configuration scanOnPush=true \
  --region "${AWS_REGION}" >/dev/null

aws ecr get-login-password --region "${AWS_REGION}" |
  docker login --username AWS --password-stdin "${REGISTRY}"

echo "Building ${FULL_IMAGE}"
docker build -t "${FULL_IMAGE}" .

echo "Pushing ${FULL_IMAGE}"
docker push "${FULL_IMAGE}"

echo "Published ${FULL_IMAGE}"
