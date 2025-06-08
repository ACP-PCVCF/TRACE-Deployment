#!/bin/bash

set -e

NAMESPACE="proving-system"
KIND_CLUSTER_NAME="kind"

echo "Uninstalling Helm releases..."
helm uninstall camunda -n $NAMESPACE || echo "Helm release 'camunda' not found or already removed."
helm uninstall kafka -n $NAMESPACE || echo "Helm release 'kafka' not found or already removed."

echo "Deleting service deployments..."
kubectl delete deployment proving-service sensor-data-service camunda-service -n $NAMESPACE --ignore-not-found

echo "Deleting services..."
kubectl delete service proving-service sensor-data-service camunda-service -n $NAMESPACE --ignore-not-found

echo "Deleting configmaps, secrets and PVCs in $NAMESPACE..."
kubectl delete configmap --all -n $NAMESPACE --ignore-not-found
kubectl delete secret --all -n $NAMESPACE --ignore-not-found
kubectl delete pvc --all -n $NAMESPACE --ignore-not-found

echo "Deleting jobs..."
kubectl delete job --all -n $NAMESPACE --ignore-not-found

echo "Deleting namespace $NAMESPACE..."
kubectl delete namespace $NAMESPACE --ignore-not-found

echo "Deleting kind cluster '$KIND_CLUSTER_NAME'..."
kind delete cluster --name $KIND_CLUSTER_NAME || echo "Kind cluster '$KIND_CLUSTER_NAME' not found or already deleted."

echo "Cleanup completed."
