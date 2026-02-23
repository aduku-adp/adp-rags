#!/usr/bin/env bash
set -euo pipefail

# from repo root
AWS_PROFILE="${AWS_PROFILE:-adp-app-admin}"
AWS_REGION="${AWS_REGION:-eu-central-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-201714515140}"
REPO="${REPO:-resto/production}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
APP_DIR="${APP_DIR:-../resto/app}"
PLATFORMS="${PLATFORMS:-linux/amd64}"
BUILDER_NAME="${BUILDER_NAME:-adp-rags-buildx}"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:${IMAGE_TAG}"

aws --profile "$AWS_PROFILE" ecr get-login-password --region "$AWS_REGION" | \
docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

if ! docker buildx inspect "$BUILDER_NAME" >/dev/null 2>&1; then
  docker buildx create --name "$BUILDER_NAME" --driver docker-container --use
else
  docker buildx use "$BUILDER_NAME"
fi

docker buildx inspect --bootstrap >/dev/null

docker buildx build \
  --platform "$PLATFORMS" \
  -t "$IMAGE_URI" \
  --push \
  "$APP_DIR"
