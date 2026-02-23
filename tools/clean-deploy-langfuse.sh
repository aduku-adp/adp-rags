kubectl delete namespace langfuse
kubectl create namespace langfuse
sh ../tools/langfuse-secret.sh
helm upgrade --install langfuse langfuse/langfuse \
  -n langfuse \
  -f ../k8s/langfuse/values.yaml \
  --version 1.5.20 \
  --wait --timeout 20m
