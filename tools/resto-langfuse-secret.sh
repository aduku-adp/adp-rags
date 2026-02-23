kubectl -n adp-rags create secret generic resto-langfuse \
  --from-literal=LANGFUSE_PUBLIC_KEY="${LANGFUSE_PUBLIC_KEY}" \
  --from-literal=LANGFUSE_SECRET_KEY="${LANGFUSE_SECRET_KEY}" \
  --from-literal=LANGFUSE_BASE_URL="${LANGFUSE_BASE_URL}" \
  --dry-run=client -o yaml | kubectl apply -f -
