K8S_DIR=./k8s/resto-rag

kubectl delete namespace adp-rags # if you need to recreate everything
kubectl create namespace adp-rags
kubectl -n adp-rags delete secret ecr-registry --ignore-not-found

kubectl -n adp-rags create secret docker-registry ecr-registry \
  --docker-server=201714515140.dkr.ecr.eu-central-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password="$(aws --profile adp-app-admin ecr get-login-password --region eu-central-1)"

kubectl apply -f ./k8s/resto-rag/secret.yaml -n adp-rags
helm upgrade --install resto-rag $K8S_DIR \
  --set 'imagePullSecrets[0].name=ecr-registry' \
  --set resto.image.tag=latest
