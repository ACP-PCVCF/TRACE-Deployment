# TRACE System Update Instructions

This guide covers how to update services, deploy changes, and maintain your TRACE integration system after the initial setup.

## Overview

The TRACE system uses Git subtrees to integrate multiple service repositories. This allows individual services to be developed independently while maintaining a unified deployment and testing environment.

## Docker Registry Integration

All service repositories are configured with CI/CD pipelines that automatically build and push Docker images to the GitHub Container Registry (`ghcr.io/acp-pcvcf/`) whenever changes are committed to the main branch. This means:

- **Automatic Updates**: When developers push changes to any service repository, new Docker images are automatically built and published
- **Always Latest**: The `:latest` tag always contains the most recent version of each service
- **No Local Building**: The integration repository pulls pre-built images instead of building locally, ensuring consistency and faster deployments
- **Immediate Availability**: Updated images are available for deployment as soon as the CI/CD pipeline completes

Available images:
- `ghcr.io/acp-pcvcf/sensor-data-service:latest`
- `ghcr.io/acp-pcvcf/camunda-service:latest`
- `ghcr.io/acp-pcvcf/proving-service:latest`
- `ghcr.io/acp-pcvcf/verifier:latest`
- `ghcr.io/acp-pcvcf/pcf-registry:latest`
- `ghcr.io/acp-pcvcf/sensor-key-registry:latest`

## Service Update Workflow

### For Service Developers

If you're working on an individual service:

1. **Work in the original service repository** - Continue your normal development workflow
2. **Commit and push changes** to the service's main branch (or appropriate feature branch)
3. **Automatic Docker registry update** - CI/CD pipelines automatically build and push updated Docker images to `ghcr.io/acp-pcvcf/` registry
4. **Notify the integrator** when changes are ready to be pulled into the integration repository

### For Integration Maintainers

When service changes need to be integrated:

#### 1. Configure Git Subtree Remotes (First-time only)

If you haven't already set up the Git remotes for the service repositories, configure them first:

```bash
git remote add sensor-data-service https://github.com/ACP-PCVCF/sensor-data-service.git
git remote add sensor-key-registry https://github.com/ACP-PCVCF/sensor-key-registry.git
git remote add camunda-service https://github.com/ACP-PCVCF/camunda-service.git
git remote add proving-service https://github.com/ACP-PCVCF/proving-service.git
git remote add verifier-service https://github.com/ACP-PCVCF/verifier.git
git remote add pcf-registry https://github.com/ACP-PCVCF/pcf-registry.git
```

Verify the remotes are configured correctly:
```bash
git remote -v
```

#### 2. Update Individual Services

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

#### 3. Update All Services at Once

For convenience, you can update all services using the provided script:

```bash
chmod +x ./scripts/setup-subtrees.sh
./scripts/setup-subtrees.sh
```


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

#### 3. Pull Updated Images

```bash
# Pull all service images from registry
# Note: These images are automatically updated when changes are pushed to service repositories
docker pull ghcr.io/acp-pcvcf/sensor-data-service:latest
docker pull ghcr.io/acp-pcvcf/camunda-service:latest
docker pull ghcr.io/acp-pcvcf/proving-service:latest
docker pull ghcr.io/acp-pcvcf/verifier:latest
docker pull ghcr.io/acp-pcvcf/pcf-registry:latest
docker pull ghcr.io/acp-pcvcf/sensor-key-registry:latest
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
kubectl rollout restart deployment/sensor-key-registry -n verifier-system
```

## Pushing Changes Back to Services

### Push Service Changes to Original Repositories

If you've made changes to service files within the integration repository, you can push them back to their original repositories:

```bash
# Push changes from specific services back to their repositories
git subtree push --prefix=sensor-data-service sensor-data-service main
git subtree push --prefix=sensor-key-registry sensor-key-registry main
git subtree push --prefix=camunda-service camunda-service main
git subtree push --prefix=proving-service proving-service main
git subtree push --prefix=verifier-service verifier-service main
git subtree push --prefix=pcf-registry pcf-registry main
```

**Note**: If the remote repository has new commits, you may need to pull first:
```bash
git subtree pull --prefix=<service-name> <service-name> main --squash
git subtree push --prefix=<service-name> <service-name> main
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
./scripts/minikube/setup.sh

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
kubectl rollout status deployment/sensor-key-registry -n verifier-system

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
kubectl logs deployment/sensor-key-registry -n verifier-system --tail=50

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
kubectl rollout undo deployment/sensor-key-registry -n verifier-system
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
./scripts/minikube/setup.sh
```

For initial setup instructions, see the [Setup Instructions](./setup-instructions.md) documentation.
