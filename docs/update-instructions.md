# TRACE System Update Instructions

This guide covers how to update services, deploy changes, and maintain your TRACE integration system after the initial setup.

## Overview

The TRACE system uses Git subtrees to integrate multiple service repositories. This allows individual services to be developed independently while maintaining a unified deployment and testing environment.

## Service Update Workflow

### For Service Developers

If you're working on an individual service:

1. **Work in the original service repository** - Continue your normal development workflow
2. **Commit and push changes** to the service's main branch (or appropriate feature branch)
3. **Notify the integrator** when changes are ready to be pulled into the integration repository

### For Integration Maintainers

When service changes need to be integrated:

#### 1. Update Individual Services

Pull the latest changes from specific service repositories:

```bash
# Sensor Data Service
git fetch sensor-data-service
git subtree pull --prefix=sensor-data-service sensor-data-service main --squash

# Sensor Key Registry
git fetch sensor-key-registry
git subtree pull --prefix=sensor-key-registry sensor-key-registry main --squash

# Camunda Service
git fetch camunda-service
git subtree pull --prefix=camunda-service camunda-service main --squash

# Proving Service
git fetch proving-service
git subtree pull --prefix=proving-service proving-service main --squash

# Verifier Service
git fetch verifier-service
git subtree pull --prefix=verifier-service verifier-service main --squash

# PCF Registry
git fetch pcf-registry
git subtree pull --prefix=pcf-registry pcf-registry main --squash
```

#### 2. Update All Services at Once

For convenience, you can update all services using the provided script:

```bash
chmod +x ./scripts/setup-subtrees.sh
./scripts/setup-subtrees.sh
```

## Deploying Updates

### Quick Rollout

After updating service code, deploy the changes to your cluster:

**For Minikube:**
```bash
chmod +x ./scripts/minikube/rollout.sh
./scripts/minikube/rollout.sh
```

**For Kind:**
```bash
chmod +x ./scripts/kind/rollout.sh
./scripts/kind/rollout.sh
```

The rollout script performs the following actions:
- Starts Minikube/Kind (if not running)
- Switches to the correct Docker context
- Builds the Docker images for all services
- Applies the Kubernetes manifests
- Updates running deployments

### Manual Update Process

If you prefer more control over the update process:

#### 1. Ensure Cluster is Running

```bash
# For Minikube
minikube status

# For Kind
kind get clusters
```

#### 2. Switch Docker Context

```bash
# For Minikube
eval $(minikube docker-env)

# For Kind
docker context use default
```

#### 3. Build Updated Images

```bash
# Build all service images
docker build -t camunda-service:latest ./camunda-service
docker build -t sensor-data-service:latest ./sensor-data-service
docker build -t proving-service:latest ./proving-service
docker build -t pcf-registry:latest ./pcf-registry
docker build -t verifier-service:latest ./verifier-service
docker build -t sensor-key-registry:latest ./sensor-key-registry
```

#### 4. Apply Kubernetes Manifests

```bash
# Apply service configurations
kubectl apply -f camunda-service/k8s/
kubectl apply -f sensor-data-service/k8s/
kubectl apply -f proving-service/k8s/
kubectl apply -f pcf-registry/pcf-deployment-charts/
kubectl apply -f verifier-service/k8s/
kubectl apply -f sensor-key-registry/k8s/
kubectl apply -f kafka-service/
```

#### 5. Restart Deployments (if needed)

Force restart of deployments to use new images:

```bash
kubectl rollout restart deployment/camunda-service -n proving-system
kubectl rollout restart deployment/sensor-data-service -n proving-system
kubectl rollout restart deployment/proving-service -n proving-system
kubectl rollout restart deployment/pcf-registry-service -n proving-system
kubectl rollout restart deployment/verifier-service -n verifier-system
kubectl rollout restart deployment/sensor-key-registry -n proving-system
```

## Working with Different Branches

### Using Different Service Branches

You can integrate different branches from service repositories based on your needs:

```bash
# Example: Use main branch for sensor-data-service but develop branch for proving-service
git subtree pull --prefix=sensor-data-service sensor-data-service main --squash
git subtree pull --prefix=proving-service proving-service develop --squash
```

### Creating Integration Branches

For complex integration scenarios, create dedicated branches in the integration repository:

```bash
# Create a new integration branch
git checkout -b feature/new-integration

# Pull specific service branches
git subtree pull --prefix=proving-service proving-service feature/new-proving-logic --squash
git subtree pull --prefix=verifier-service verifier-service feature/enhanced-verification --squash

# Test and validate
./scripts/minikube/rollout.sh

# Merge when ready
git checkout main
git merge feature/new-integration
```

## Monitoring Updates

### Check Deployment Status

Monitor the update process:

```bash
# Watch deployment rollouts
kubectl rollout status deployment/camunda-service -n proving-system
kubectl rollout status deployment/sensor-data-service -n proving-system
kubectl rollout status deployment/proving-service -n proving-system
kubectl rollout status deployment/pcf-registry-service -n proving-system
kubectl rollout status deployment/verifier-service -n verifier-system

# Check pod status
kubectl get pods -n proving-system
kubectl get pods -n verifier-system
```

### Verify Service Health

After updates, verify services are working correctly:

```bash
# Check service logs for errors
kubectl logs deployment/camunda-service -n proving-system --tail=50
kubectl logs deployment/sensor-data-service -n proving-system --tail=50
kubectl logs deployment/proving-service -n proving-system --tail=50
kubectl logs deployment/pcf-registry-service -n proving-system --tail=50
kubectl logs deployment/verifier-service -n verifier-system --tail=50

# Test service endpoints (if port-forwarding is active)
curl -f http://localhost:5002/health  # PCF Registry health check
```

## Rollback Procedures

### Rolling Back to Previous Version

If an update causes issues, you can rollback deployments:

```bash
# Rollback specific deployments
kubectl rollout undo deployment/camunda-service -n proving-system
kubectl rollout undo deployment/sensor-data-service -n proving-system
kubectl rollout undo deployment/proving-service -n proving-system
kubectl rollout undo deployment/pcf-registry-service -n proving-system
kubectl rollout undo deployment/verifier-service -n verifier-system
```

### Git-level Rollback

For more comprehensive rollbacks, use Git:

```bash
# View recent commits
git log --oneline -10

# Revert to a previous commit
git revert <commit-hash>

# Or reset to a previous state (destructive)
git reset --hard <commit-hash>

# Redeploy after Git rollback
./scripts/minikube/rollout.sh
```

For initial setup instructions, see the [Setup Instructions](./setup-instructions.md) documentation.
