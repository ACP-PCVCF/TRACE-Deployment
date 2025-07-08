#!/bin/bash
set -e

NAMESPACE1="proving-system"
NAMESPACE2="verifier-system"
KIND_CLUSTER_NAME="kind"

echo "Checking if kind cluster '$KIND_CLUSTER_NAME' exists..."
if ! kind get clusters | grep -q "^$KIND_CLUSTER_NAME$"; then
  echo "Creating kind cluster '$KIND_CLUSTER_NAME'..."
  kind create cluster --name $KIND_CLUSTER_NAME
else
  echo "Kind cluster '$KIND_CLUSTER_NAME' already exists."
fi

echo "Rebuilding Docker images with latest code..."
docker build -t sensor-data-service:latest ./sensor-data-service 
docker build -t camunda-service:latest ./camunda-service
docker build --platform=linux/amd64 -t proving-service:latest ./proving-service
docker build -t verifier-service:latest ./verifier-service
docker build -t pcf-registry:latest ./pcf-registry

echo "Loading Docker images into kind cluster..."
kind load docker-image sensor-data-service:latest --name $KIND_CLUSTER_NAME
kind load docker-image camunda-service:latest --name $KIND_CLUSTER_NAME
kind load docker-image proving-service:latest --name $KIND_CLUSTER_NAME
kind load docker-image verifier-service:latest --name $KIND_CLUSTER_NAME
kind load docker-image pcf-registry:latest --name $KIND_CLUSTER_NAME

echo "Applying updated manifests..."
kubectl apply -f ./sensor-data-service/k8s/sensor-data-service.yaml -n $NAMESPACE1
kubectl apply -f ./camunda-service/k8s/camunda-service.yaml -n $NAMESPACE1
kubectl apply -f ./proving-service/k8s/proving-service.yaml -n $NAMESPACE1
kubectl apply -f ./verifier-service/k8s/verifier-service.yaml -n $NAMESPACE2

echo "Upgrading PCF-Registry..."
helm upgrade pcf-registry ./pcf-registry/pcf-deployment-charts -n $NAMESPACE1

echo "Triggering rollout restarts..."
kubectl rollout restart deployment/sensor-data-service -n $NAMESPACE1
kubectl rollout restart deployment/camunda-service -n $NAMESPACE1
kubectl rollout restart deployment/proving-service -n $NAMESPACE1
kubectl rollout restart deployment/pcf-registry-service -n $NAMESPACE1
kubectl rollout restart deployment/verifier-service -n $NAMESPACE2
