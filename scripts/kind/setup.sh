#!/bin/bash
set -e

NAMESPACE="proving-system"
KIND_CLUSTER_NAME="kind"

echo "Checking if kind cluster '$KIND_CLUSTER_NAME' exists..."
if ! kind get clusters | grep -q "^$KIND_CLUSTER_NAME$"; then
  echo "Creating kind cluster '$KIND_CLUSTER_NAME'..."
  kind create cluster --name $KIND_CLUSTER_NAME
else
  echo "Kind cluster '$KIND_CLUSTER_NAME' already exists."
fi

echo "Checking if Camunda Helm repo is added..."
if ! helm repo list | grep -q camunda; then
  echo "Adding Camunda Helm repo..."
  helm repo add camunda https://helm.camunda.io
else
  echo "Camunda Helm repo already added."
fi

echo "Checking if Bitnami Helm repo is added..."
if ! helm repo list | grep -q bitnami; then
  echo "Adding Bitnami Helm repo..."
  helm repo add bitnami https://charts.bitnami.com/bitnami
else
  echo "Bitnami Helm repo already added."
fi

echo "Updating Helm repos..."
helm repo update

echo "Checking if Camunda is already installed..."
if ! helm list -n $NAMESPACE | grep -q camunda; then
  echo "Installing Camunda in namespace $NAMESPACE..."
  helm install camunda camunda/camunda-platform \
    -n $NAMESPACE --create-namespace \
    -f ./camunda-platform/camunda-platform-core-kind-values.yaml
else
  echo "Camunda is already installed in $NAMESPACE."
fi

echo "Waiting for Camunda pods to be created..."
until kubectl get pods -n $NAMESPACE 2>/dev/null | grep -q "camunda"; do
  echo "Still waiting for Camunda pods..."
  sleep 2
done

echo "Waiting for all Camunda pods to be ready..."
if ! kubectl wait --for=condition=ready pod --all -n $NAMESPACE --timeout=400s; then
  echo "ERROR: Timeout waiting for Camunda pods to become ready"
  exit 1
fi

echo "Checking if Kafka is already installed..."
if ! helm list -n $NAMESPACE | grep -q kafka; then
  echo "Installing Kafka in namespace $NAMESPACE..."
  helm install kafka bitnami/kafka \
    --namespace $NAMESPACE \
    --create-namespace \
    -f kafka-service/kafka-values.yaml
else
  echo "Kafka is already installed in $NAMESPACE."
fi

echo "Waiting for Kafka pods to be ready..."
if ! kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=kafka -n $NAMESPACE --timeout=300s; then
  echo "ERROR: Timeout waiting for Kafka pods to become ready"
  exit 1
fi

echo "Execute Kafka topics job..."
kubectl apply -f kafka-service/kafka-topic-job.yaml

echo "Waiting for Kafka topics job to be done..."
if ! kubectl wait --for=condition=complete job/create-kafka-topics -n $NAMESPACE --timeout=120s; then
  echo "ERROR: Timeout waiting for Kafka topics job to complete"
  exit 1
fi

echo "Building Docker images..."
docker build -t sensor-data-service:latest ./sensor-data-service 
docker build -t camunda-service:latest ./camunda-service
docker build --platform=linux/amd64 -t proving-service:latest ./proving-service

echo "Loading Docker images into kind cluster..."
kind load docker-image sensor-data-service:latest --name $KIND_CLUSTER_NAME
kind load docker-image camunda-service:latest --name $KIND_CLUSTER_NAME
kind load docker-image proving-service:latest --name $KIND_CLUSTER_NAME

echo "Deploying services to Kubernetes..."
kubectl apply -f ./sensor-data-service/k8s/sensor-data-service.yaml -n $NAMESPACE
kubectl apply -f ./camunda-service/k8s/camunda-service.yaml -n $NAMESPACE
kubectl apply -f ./proving-service/k8s/proving-service.yaml -n $NAMESPACE

echo "All services deployed successfully to namespace '$NAMESPACE'."
kubectl get pods -n $NAMESPACE
