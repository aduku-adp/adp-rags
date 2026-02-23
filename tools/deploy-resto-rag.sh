K8S_DIR=./k8s/resto-rag

kubectl apply -f ./k8s/resto-rag/secret.yaml -n adp-rags
helm upgrade --install resto-rag $K8S_DIR \
  --set 'imagePullSecrets[0].name=ecr-registry' \
  --set resto.image.tag=latest
