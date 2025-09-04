#!/bin/bash

# Deploy updates to Lambda function
# Usage: ./deploy.sh [version]

# Check if version is provided
VERSION=${1:-"latest"}
IMAGE_NAME="letterboxdimage"
ECR_REPO="600627345650.dkr.ecr.us-east-1.amazonaws.com/${IMAGE_NAME}"
LAMBDA_FUNCTION_NAME="letterboxd-scraper"

echo "Building Docker image with version: ${VERSION}"
docker build -f Dockerfile.lambda.v2 -t ${IMAGE_NAME}:${VERSION} .

echo "Tagging image for ECR"
docker tag ${IMAGE_NAME}:${VERSION} ${ECR_REPO}:${VERSION}

echo "Logging into ECR"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 600627345650.dkr.ecr.us-east-1.amazonaws.com

echo "Pushing image to ECR"
docker push ${ECR_REPO}:${VERSION}

echo "Updating Lambda function"
aws lambda update-function-code \
  --function-name ${LAMBDA_FUNCTION_NAME} \
  --image-uri ${ECR_REPO}:${VERSION}

echo "Testing Lambda function"
aws lambda invoke --function-name ${LAMBDA_FUNCTION_NAME} --payload '{}' response.json

echo "Response:"
cat response.json
