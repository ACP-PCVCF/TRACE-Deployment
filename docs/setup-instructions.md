# TRACE System Setup Instructions

This guide will walk you through setting up the TRACE integration system from scratch. The system consists of multiple microservices that work together to provide a complete tracing and verification platform.

## Prerequisites

Before starting the setup, ensure you have the following tools installed on your system:

- **Docker** - Container runtime for building and running services
- **Minikube** or **Kind** - Local Kubernetes cluster
- **kubectl** - Kubernetes command-line tool
- **Helm** - Kubernetes package manager
- **Git** - Version control system
- **Bash shell** - For running setup scripts

## Initial System Setup

### 1. Clone the Repository

First, clone the integration repository to your local machine:

```bash
git clone https://github.com/ACP-PCVCF/TRACE.git
cd TRACE
```

### 2. Configure Git Subtree Remotes

The TRACE system uses Git subtrees to integrate multiple service repositories. Set up the remote repositories for all services:

```bash
# Add all service repositories as remotes
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

### 3. Start the Cluster and Install Camunda

Choose either Minikube or Kind for your local Kubernetes cluster and run the appropriate setup script:

**For Minikube:**
```bash
chmod +x ./scripts/minikube/setup.sh
./scripts/minikube/setup.sh
```

**For Kind:**
```bash
chmod +x ./scripts/kind/setup.sh
./scripts/kind/setup.sh
```

This script will:
- Start your Kubernetes cluster
- Install Camunda Platform
- Deploy all TRACE services
- Configure necessary networking

### 4. Configure Port Forwarding

After the cluster is running, you need to set up port forwarding to access the services from your local machine.

#### Camunda Gateway (Required for Modeler)

Forward the Zeebe gateway port to connect Camunda Modeler:

```bash
kubectl port-forward svc/camunda-zeebe-gateway 26500:26500 -n proving-system
```

**Important:** Keep this terminal session open while working with Camunda Modeler.

#### Camunda Operate (Process Management)

Forward the Camunda Operate service to view and manage process instances:

```bash
kubectl port-forward svc/camunda-operate 8081:80 -n proving-system
```

Access Camunda Operate at: http://localhost:8081
- Username: `demo`
- Password: `demo`

## BPMN Model Deployment

### 1. Configure Camunda Modeler

In the Camunda Modeler application:

1. Open your BPMN files for e.g.:
   - `origin.bpmn`
   - `tsp.bpmn`
   - `Case_1 Kopie.bpmn`
   - `Case_2 Kopie.bpmn`
   - `Case_3 Kopie.bpmn`

2. Select **Camunda 8 → Self-Managed**

3. Configure connection settings:
   - **Zeebe Gateway Address:** `localhost:26500`
   - **Authentication:** None

### 2. Deploy and Start Processes

1. Click **Deploy Current Diagram** in Camunda Modeler
2. Start the process in Camunda Modeler
3. Monitor progress in Camunda Operate (http://localhost:8081/operate)

## Verification and Monitoring

### Check Service Status

Verify all services are running correctly:

```bash
# Check pods in proving-system namespace
kubectl get pods -n proving-system

# Check pods in verifier-system namespace
kubectl get pods -n verifier-system
```

### Monitor Service Logs

View logs for individual services:

```bash
# Camunda service logs
kubectl logs deployment/camunda-service -n proving-system

# Sensor data service logs
kubectl logs deployment/sensor-data-service -n proving-system

# Proving service logs
kubectl logs deployment/proving-service -n proving-system

# PCF registry service logs
kubectl logs deployment/pcf-registry-service -n proving-system

# Verifier service logs
kubectl logs deployment/verifier-service -n verifier-system
```

## System Architecture Overview

The TRACE system consists of the following main components:

- **Camunda Service** - Workflow orchestration and process management
- **Sensor Data Service** - Handles sensor data collection and processing
- **Sensor Key Registry** - Manages sensor authentication keys
- **Proving Service** - Manages cryptographic proofs and verification
- **Verifier Service** - Independent verification of proofs and claims
- **PCF Registry** - Product Carbon Footprint registry we use to upload and download proofs

## Next Steps

Once your system is set up and running:

1. Explore the Camunda Operate interface to understand process flows
2. Review the individual service documentation for advanced configuration
3. Set up monitoring and logging for production use

For information on updating services and maintaining your installation, see the [Update Instructions](./update-instructions.md) documentation.
