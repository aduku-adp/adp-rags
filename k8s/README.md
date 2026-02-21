# Resto RAG Kubernetes

This directory contains a Helm chart translating `resto/docker-compose.yaml` into Kubernetes resources.

## What is included

- `k8s/resto-rag/templates/chroma-*.yaml`: Chroma Deployment, Service, and PVC.
- `k8s/resto-rag/templates/ollama-*.yaml`: Ollama Deployment, Service, and PVC.
- `k8s/resto-rag/templates/resto-*.yaml`: Streamlit app Deployment and Service.
- `k8s/resto-rag/templates/ollama-preload-job.yaml`: Optional Helm hook Job to pull required Ollama models.

## Prerequisites

- Kubernetes cluster with dynamic PVC provisioning.
- Helm 3.
- The `resto` application image must be available in the cluster.

## 1) Build and publish app image

From repository root:

```bash
./build-resto.sh
```

# 2) Confirm the tag exists in ECR
```bash
aws --profile adp-app-admin ecr describe-images \
  --region eu-central-1 \
  --repository-name resto/production \
  --image-ids imageTag=latest
```

# 3) Create/update an image pull secret in your namespace
```bash
kubectl -n adp-rags delete secret ecr-registry --ignore-not-found

kubectl -n adp-rags create secret docker-registry ecr-registry \
  --docker-server=201714515140.dkr.ecr.eu-central-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password="$(aws --profile adp-app-admin ecr get-login-password --region eu-central-1)"
```

## 4) Install chart

```bash
helm upgrade --install resto-rag ./k8s/resto-rag \
  --set 'imagePullSecrets[0].name=ecr-registry' \
  --set resto.image.tag=latest
```

## 5) Test the embedding where created

Port-forward services for testing:

   ```bash
   cd resto/tools
   source adp-rags/bin/activate
   python test_embeddings.py
   ```


## 6) Access the app

Port-forward services for testing:

```bash
kubectl -n adp-rags port-forward svc/resto 8501:8501
kubectl -n adp-rags port-forward svc/chroma 8000:8000
kubectl -n adp-rags port-forward svc/ollama 11434:11434
```


Open http://localhost:8501

## 4) Load embeddings (after model pull)

The chart preloads LLM and embedding models by default (`ollama.preloadModels.enabled=true`).
It also runs a post-install/post-upgrade Helm Job to execute `create_embeddings.py` automatically and populate Chroma.

Disable this behavior if needed:

```bash
helm upgrade --install resto-rag ./k8s/resto-rag \
  --set resto.image.repository=201714515140.dkr.ecr.eu-central-1.amazonaws.com/resto/production \
  --set embeddingsJob.enabled=false
```

## Notes on Helm charts per service

This setup uses a single project-local Helm chart with first-party manifests for all three services, ensuring reproducible deployment even when external service charts are unavailable or differ from your compose behavior.
