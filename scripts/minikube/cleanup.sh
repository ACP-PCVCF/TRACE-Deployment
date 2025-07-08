#!/bin/bash

set -e

NAMESPACE1="proving-system"
NAMESPACE2="verifier-system"

echo "Uninstalling Helm releases..."
helm uninstall camunda -n $NAMESPACE1 || echo "Helm release 'camunda' not found or already removed."
helm uninstall kafka -n $NAMESPACE1 || echo "Helm release 'kafka' not found or already removed."
helm uninstall pcf-registry -n $NAMESPACE1 || echo "Helm release 'pcf-registry' not found or already removed."

echo "Deleting service deployments..."
kubectl delete deployment proofing-service sensor-data-service camunda-service pcf-registry-service -n $NAMESPACE1 --ignore-not-found
kubectl delete deployment verifier-service -n $NAMESPACE2 --ignore-not-found

echo "Deleting services..."
kubectl delete service proofing-service sensor-data-service camunda-service pcf-registry-service -n $NAMESPACE1 --ignore-not-found
kubectl delete service verifier-service -n $NAMESPACE2 --ignore-not-found

echo "Deleting configmaps, secrets and PVCs in $NAMESPACE1..."
kubectl delete configmap --all -n $NAMESPACE1 --ignore-not-found
kubectl delete secret --all -n $NAMESPACE1 --ignore-not-found
kubectl delete pvc --all -n $NAMESPACE1 --ignore-not-found

echo "Deleting configmaps, secrets and PVCs in $NAMESPACE2..."
kubectl delete configmap --all -n $NAMESPACE2 --ignore-not-found
kubectl delete secret --all -n $NAMESPACE2 --ignore-not-found
kubectl delete pvc --all -n $NAMESPACE2 --ignore-not-found

echo "Deleting jobs..."
kubectl delete job --all -n $NAMESPACE1 --ignore-not-found
kubectl delete job --all -n $NAMESPACE2 --ignore-not-found

echo "Deleting namespaces..."
kubectl delete namespace $NAMESPACE1 --ignore-not-found
kubectl delete namespace $NAMESPACE2 --ignore-not-found

echo "Stopping Minikube..."
minikube stop

echo "Deleting Minikube cluster..."
minikube delete

echo "Cleanup completed."
