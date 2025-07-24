#!/bin/bash
set -e

NAMESPACE1="proving-system"
NAMESPACE2="verifier-system"

echo "=== TRACE Helm Cleanup Script for Minikube ==="

# Configure kubectl to use minikube context
echo "Setting kubectl context to minikube..."
kubectl config use-context minikube

echo "Uninstalling Helm releases..."

# Uninstall microservices
echo "Uninstalling Verifier Service..."
helm uninstall verifier-service -n $NAMESPACE2 2>/dev/null || echo "verifier-service not found"

echo "Uninstalling Sensor Key Registry..."
helm uninstall sensor-key-registry -n $NAMESPACE2 2>/dev/null || echo "sensor-key-registry not found"

echo "Uninstalling Proving Service..."
helm uninstall proving-service -n $NAMESPACE1 2>/dev/null || echo "proving-service not found"

echo "Uninstalling Camunda Service..."
helm uninstall camunda-service -n $NAMESPACE1 2>/dev/null || echo "camunda-service not found"

echo "Uninstalling Sensor Data Service..."
helm uninstall sensor-data-service -n $NAMESPACE1 2>/dev/null || echo "sensor-data-service not found"

echo "Uninstalling PCF Registry..."
helm uninstall pcf-registry -n $NAMESPACE1 2>/dev/null || echo "pcf-registry not found"

echo "Uninstalling Kafka..."
helm uninstall kafka -n $NAMESPACE1 2>/dev/null || echo "kafka not found"

echo "Uninstalling Camunda Platform..."
helm uninstall camunda -n $NAMESPACE1 2>/dev/null || echo "camunda not found"

echo "Deleting namespaces..."
kubectl delete namespace $NAMESPACE1 2>/dev/null || echo "namespace $NAMESPACE1 not found"
kubectl delete namespace $NAMESPACE2 2>/dev/null || echo "namespace $NAMESPACE2 not found"

echo "Stopping minikube..."
minikube stop

echo "=== Cleanup Complete ==="
echo "Minikube has been stopped. To completely remove minikube:"
echo "  minikube delete"
