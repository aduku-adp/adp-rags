sh ../tools/airflow-aws-creds-secret.sh
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f ../k8s/airflow/values.yaml \
  --version 1.19.0
