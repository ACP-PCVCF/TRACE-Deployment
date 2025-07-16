# Cluster setup instructions

## Initial Setup (run once)
### Prerequisites
- Docker
- Minikube/Kind
- kubectl
- Helm
- Git
- Bash shell

### 1. Clone this repository
```bash
git clone git@github.com:ACP-PCVCF/integration-repo.git
cd integration-repo
```

### 2. Run setup
This will start the cluster and install Camunda (choose Kind or Minikube script folder):
```bash
./scripts/minikube/setup.sh
```
You might need to make the script executable first by using ```chmod +x setup.sh```.

### 3. Configure port forwarding
To connect the Camunda Modeler to Zeebe, forward the gateway port:

```bash
kubectl port-forward svc/camunda-zeebe-gateway 26500:26500 -n proving-system
```
Keep this terminal open while deploying models from the Camunda Modeler.

To view and manage process instances, forward the Camunda Operate service:

```bash
kubectl port-forward svc/camunda-operate 8081:80 -n proving-system
```
Then open your browser at: http://localhost:8081

### 4. Deploy BPMN Models from Camunda Modeler
In the Camunda Modeler:

1. Open your BPMN files (origin.bpmn, tsp.bpmn, Case_1 Kopie.bpmn, Case_2 Kopie.bpmn, Case_3 Kopie.bpmn).

2. Select Camunda 8 → Self-Managed.

3. Use the following connection settings:

- Zeebe Gateway Address: localhost:26500

- Authentication: None

4. Click Deploy Current Diagram.

5. Start process in Camunda Modeler.

6. Check progress in Camunda Operate (http://localhost:8081/operate) using username: demo and password: demo.

   
## Rollout Services (repeatable)
After any changes to your services or code, simply run (choose Kind or Minikube script folder):

```bash
./scripts/minikube/rollout.sh
```
You might need to make the script executable first by using ```chmod +x rollout.sh```.

This script:
- Starts Minikube/Kind (if not running)
- Switches to the correct Docker context
- Builds the Docker images
- Applies the Kubernetes manifests

## Monitor Logs and Status

```bash
kubectl get pods -n proving-system
kubectl get pods -n verifier-system
kubectl logs deployment/camunda-service -n proving-system
kubectl logs deployment/sensor-data-service -n proving-system
kubectl logs deployment/proving-service -n proving-system
kubectl logs deployment/pcf-registry-service -n proving-system
kubectl logs deployment/verifier-service -n verifier-system
```

## PCF-Registry Service

After deployment, you can access the PCF-Registry services:

```bash
# Forward the HTTP API port
kubectl port-forward svc/pcf-registry-service 5002:5002 -n proving-system

# Forward the gRPC port
kubectl port-forward svc/pcf-registry-service 50052:50052 -n proving-system

# Forward MinIO console (if needed)
kubectl port-forward svc/minio-service 9001:9001 -n proving-system
```


## Cleanup
If you want to destroy your cluster, delete all your services/deployments and stop Minikube/Kind, run:

```bash 
./scripts/minikube/cleanup.sh
```
You might need to make the script executable first by using ```chmod +x cleanup.sh```.


## Git Subtrees – How We Use Them
This repository integrates multiple service repositories using Git Subtrees.

Each service (i.e., sensor-data-service, camunda-service, and proving-service) lives in its own dedicated Git repository, but is pulled into this integration repository via subtree under its respective folder.
This allows us to deploy and test all services together without changing how each service is developed.

### Setting up Git Remotes (First-time setup)
Before you can use the subtree commands, you need to add the service repositories as git remotes. Run these commands once after cloning the integration repository:

```bash
# Add all service repositories as remotes
git remote add sensor-data-service https://github.com/ACP-PCVCF/sensor-data-service.git
git remote add camunda-service https://github.com/ACP-PCVCF/camunda-service.git
git remote add proving-service https://github.com/ACP-PCVCF/proving-service.git
git remote add verifier-service https://github.com/ACP-PCVCF/verifier.git
git remote add pcf-registry https://github.com/ACP-PCVCF/pcf-registry.git
```

You can verify your remotes are set up correctly by running:
```bash
git remote -v
```

This should show all the service repositories along with the main `origin` remote.

### Developer Workflow
If you're working on one of the individual services:
1. Keep working in the original service repository as usual.
2. Commit and push your changes to the service's main branch.

### Updating the integration repo
After changes have been pushed to a service repository, someone (usually the integrator) will pull the updates into this integration repository using:
```bash
git fetch sensor-data-service
git subtree pull --prefix=sensor-data-service sensor-data-service main --squash

git fetch camunda-service
git subtree pull --prefix=camunda-service camunda-service main --squash

git fetch proving-service
git subtree pull --prefix=proving-service proving-service main --squash

git fetch verifier-service
git subtree pull --prefix=verifier-service verifier-service main --squash

git fetch pcf-registry
git subtree pull --prefix=pcf-registry pcf-registry main --squash

git fetch sensor-key-registry
git subtree pull --prefix=sensor-key-registry sensor-key-registry main --squash
```
Repeat as needed for the services you want to update.

This keeps the integration repository up to date with the latest service code, and ready for deployment and testing.

### Different branch versions
Additionally, since subtrees reference a specific branch of the original service repository, you can choose which branch to track for each service.

For example, the integration repository may pull from the main branch of sensor-data-service, but from a develop branch of proving-service, depending on your integration or staging needs:

```bash
git subtree pull --prefix=sensor-data-service sensor-data-service main --squash
git subtree pull --prefix=proving-service proving-service develop --squash
```
Please use different branches in this integration repository if you need additional branch combinations that don't involve all main branches.
