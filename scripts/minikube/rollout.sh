#!/bin/bash
set -e

NAMESPACE1="proving-system"
NAMESPACE2="verifier-system"

echo "Checking if Minikube is running..."
if ! minikube status | grep -q "Running"; then
  echo "Starting Minikube..."
  minikube start --memory=8192 --cpus=4 --driver=docker
else
  echo "Minikube is already running."
fi

echo "Switching to Minikube Docker context..."
eval "$(minikube docker-env)"

echo "Rebuilding Docker images with latest code..."
docker build -t sensor-data-service:latest ./sensor-data-service 
docker build -t camunda-service:latest ./camunda-service
docker build --platform=linux/amd64 -t proving-service:latest ./proving-service
docker build -t verifier-service:latest ./verifier-service

echo "Applying updated manifests..."
kubectl apply -f ./sensor-data-service/k8s/sensor-data-service.yaml -n $NAMESPACE1
kubectl apply -f ./camunda-service/k8s/camunda-service.yaml -n $NAMESPACE1
kubectl apply -f ./proving-service/k8s/proving-service.yaml -n $NAMESPACE1
kubectl apply -f ./verifier-service/k8s/verifier-service.yaml -n $NAMESPACE2

echo "Triggering rollout restarts..."
kubectl rollout restart deployment/sensor-data-service -n $NAMESPACE1
kubectl rollout restart deployment/camunda-service -n $NAMESPACE1
kubectl rollout restart deployment/proving-service -n $NAMESPACE1
kubectl rollout restart deployment/verifier-service -n $NAMESPACE2

echo "Waiting for updated pods to become ready..."
kubectl rollout status deployment/sensor-data-service -n $NAMESPACE1
kubectl rollout status deployment/camunda-service -n $NAMESPACE1
kubectl rollout status deployment/proving-service -n $NAMESPACE1
kubectl rollout status deployment/verifier-service -n $NAMESPACE2

echo "Rollout complete. Current pods:"
echo "--- $NAMESPACE1 ---"
kubectl get pods -n $NAMESPACE1
echo "--- $NAMESPACE2 ---"
kubectl get pods -n $NAMESPACE2
