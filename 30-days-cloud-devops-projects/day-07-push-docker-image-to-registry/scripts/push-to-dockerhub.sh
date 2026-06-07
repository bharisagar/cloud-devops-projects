#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-v1}"
IMAGE_NAME="day-07-registry-api"

if [[ -z "${DOCKERHUB_USERNAME:-}" ]]; then
  echo "DOCKERHUB_USERNAME is required."
  echo "Example: export DOCKERHUB_USERNAME=your-dockerhub-username"
  exit 1
fi

FULL_IMAGE="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "Building ${FULL_IMAGE}"
docker build -t "${FULL_IMAGE}" .

echo "Pushing ${FULL_IMAGE}"
docker push "${FULL_IMAGE}"

echo "Published ${FULL_IMAGE}"
