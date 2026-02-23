K8S_DIR=../k8s/resto-rag

sh ../tools/resto-langfuse-secret.sh
helm upgrade --install resto-rag $K8S_DIR \
  --set 'imagePullSecrets[0].name=ecr-registry' \
  --set resto.image.tag=latest
