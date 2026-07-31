#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-dattm24/edge-tts-fastapi}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PLATFORM=${PLATFORM:-linux/amd64,linux/arm64}

echo "Building ${IMAGE_NAME}:${IMAGE_TAG} for ${PLATFORM}"

docker buildx create --name multiarch --use 2>/dev/null || true

docker buildx build \
  "${DOCKER_BUILD_ARGS[@]}" \
  --platform "$PLATFORM" \
  -t "${IMAGE_NAME}:${IMAGE_TAG}" \
  --push .

echo "Done: ${IMAGE_NAME}:${IMAGE_TAG}"
