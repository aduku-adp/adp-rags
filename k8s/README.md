# Kubernetes Runbook

This folder contains Helm values/manifests for:
- `resto-rag` app stack (`k8s/resto-rag`)
- `langfuse` install values (`k8s/langfuse`)

## Prerequisites

- Kubernetes cluster (Minikube or cloud)
- Helm 3
- `kubectl` configured to the target cluster
- ECR image exists for `resto` (for this repo: `201714515140.dkr.ecr.eu-central-1.amazonaws.com/resto/production`)

## 1) Deploy `resto-rag`

`resto-rag` defaults:
- namespace: `adp-rags`
- Qdrant: `qdrant/qdrant:v1.14.1`
- Ollama: `ollama/ollama:0.15.5`
- model preload hook: enabled
- embeddings hook: enabled
- Langfuse env injection: enabled (expects `resto-langfuse` secret)

### 1.1 Create ECR pull secret

```bash
kubectl create namespace adp-rags --dry-run=client -o yaml | kubectl apply -f -

kubectl -n adp-rags create secret docker-registry ecr-registry \
  --docker-server=201714515140.dkr.ecr.eu-central-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password="$(aws --profile adp-app-admin ecr get-login-password --region eu-central-1)" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 1.2 Create Langfuse secret for `resto` (required if `resto.langfuse.enabled=true`)

```bash
kubectl -n adp-rags create secret generic resto-langfuse \
  --from-literal=LANGFUSE_PUBLIC_KEY='pk-lf-...' \
  --from-literal=LANGFUSE_SECRET_KEY='sk-lf-...' \
  --from-literal=LANGFUSE_BASE_URL='http://langfuse-web.langfuse.svc.cluster.local:3000' \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 1.3 Install/upgrade chart

```bash
helm upgrade --install resto-rag ./k8s/resto-rag \
  -n adp-rags \
  --create-namespace \
  --set 'imagePullSecrets[0].name=ecr-registry' \
  --set resto.image.tag=latest \
  --timeout 45m
```

If you want a faster install (no long-running hooks):

```bash
helm upgrade --install resto-rag ./k8s/resto-rag \
  -n adp-rags \
  --create-namespace \
  --set 'imagePullSecrets[0].name=ecr-registry' \
  --set embeddingsJob.enabled=false \
  --set ollama.preloadModels.enabled=false
```

### 1.4 Access services

```bash
kubectl -n adp-rags port-forward svc/resto 8501:8501
kubectl -n adp-rags port-forward svc/qdrant 6333:6333
kubectl -n adp-rags port-forward svc/ollama 11434:11434
```

- Resto UI: `http://localhost:8501`
- Qdrant collections endpoint: `http://localhost:6333/collections`

## 2) Install monitoring (`kube-prometheus-stack`)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --create-namespace \
  --version 82.2.0
```

If pod/node dashboards miss cAdvisor data, run:

```bash
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --reuse-values \
  --set kubelet.serviceMonitor.cAdvisor=true \
  --set kubelet.serviceMonitor.resource=true \
  --set kubelet.serviceMonitor.probes=true \
  --version 82.2.0
```

Grafana/Prometheus access:

```bash
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80
```

## 3) Install Langfuse

```bash
helm repo add langfuse https://langfuse.github.io/langfuse-k8s
helm repo update

kubectl create namespace langfuse --dry-run=client -o yaml | kubectl apply -f -
kubectl -n langfuse apply -f ./k8s/langfuse/secret.yaml

helm upgrade --install langfuse langfuse/langfuse \
  -n langfuse \
  -f ./k8s/langfuse/values.yaml \
  --version 1.5.20 \
  --wait --timeout 20m
```

## 4) Useful checks

```bash
kubectl -n adp-rags get pods,svc
kubectl -n adp-rags logs deploy/resto-rag-resto --tail=100
kubectl -n adp-rags logs deploy/resto-rag-qdrant --tail=100
kubectl -n adp-rags get jobs

helm -n adp-rags ls
helm -n monitoring ls
helm -n langfuse ls
```

## 5) Minikube resource tips

If the local cluster is slow, restart with more resources (fit to host limits):

```bash
minikube stop
minikube start --cpus=6 --memory=11000 --disk-size=50g
```
