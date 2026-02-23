# from repo root
AWS_PROFILE=adp-app-admin
AWS_REGION=eu-central-1
AWS_ACCOUNT_ID=201714515140
REPO=resto/production
IMAGE_TAG=latest
APP_DIR=./resto/app

aws --profile $AWS_PROFILE ecr get-login-password --region $AWS_REGION | \
docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

docker build -t resto:$IMAGE_TAG $APP_DIR
docker tag resto:$IMAGE_TAG ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:$IMAGE_TAG
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}:$IMAGE_TAG
