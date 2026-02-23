kubectl -n airflow create secret generic airflow-aws-creds \
  --from-literal=AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
  --from-literal=AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
  --from-literal=AWS_DEFAULT_REGION="eu-central-1" \
  --dry-run=client -o yaml | kubectl apply -f -
