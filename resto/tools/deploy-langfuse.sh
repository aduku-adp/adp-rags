kubectl apply -f ../../k8s/langfuse/secret.yaml -n langfuse
helm upgrade --install langfuse langfuse/langfuse \
  -n langfuse \
  -f ../../k8s/langfuse/values.yaml \
  --version 1.5.20 \
  --wait --timeout 20m
