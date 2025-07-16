#!/bin/bash
set -e

echo "Setting up Git Subtrees for Integration Repository"
echo "================================================="

# Define all service repositories
declare -A SERVICES
SERVICES[sensor-data-service]="https://github.com/ACP-PCVCF/sensor-data-service.git"
SERVICES[camunda-service]="https://github.com/ACP-PCVCF/camunda-service.git"
SERVICES[proving-service]="https://github.com/ACP-PCVCF/proving-service.git"
SERVICES[verifier-service]="https://github.com/ACP-PCVCF/verifier.git"
SERVICES[pcf-registry]="https://github.com/ACP-PCVCF/pcf-registry.git"
SERVICES[sensor-key-registry]="https://github.com/ACP-PCVCF/sensor-key-registry.git"

echo "Step 1: Adding Git Remotes"
echo "--------------------------"
for service in "${!SERVICES[@]}"; do
    repo_url="${SERVICES[$service]}"
    
    # Check if remote already exists
    if git remote get-url "$service" >/dev/null 2>&1; then
        echo "Remote '$service' already exists"
    else
        echo "Adding remote '$service' -> $repo_url"
        git remote add "$service" "$repo_url"
        echo "Added remote '$service'"
    fi
done

echo ""
echo "Step 2: Fetching All Remotes"
echo "-----------------------------"
for service in "${!SERVICES[@]}"; do
    echo "Fetching $service..."
    if git fetch "$service"; then
        echo "Fetched $service"
    else
        echo "Failed to fetch $service"
        exit 1
    fi
done

echo ""
echo "Step 3: Pulling Subtrees"
echo "------------------------"
for service in "${!SERVICES[@]}"; do
    echo "Pulling subtree for $service..."
    
    # Check if subtree directory already exists
    if [ -d "$service" ]; then
        echo "Directory '$service' exists, pulling updates..."
        if git subtree pull --prefix="$service" "$service" main --squash; then
            echo "Updated subtree for $service"
        else
            echo "Failed to update subtree for $service"
            echo "This might be expected if it's not a subtree yet"
        fi
    else
        echo "Directory '$service' doesn't exist, adding new subtree..."
        if git subtree add --prefix="$service" "$service" main --squash; then
            echo "Added new subtree for $service"
        else
            echo "Failed to add subtree for $service"
            exit 1
        fi
    fi
done

echo ""
echo "Step 4: Verification"
echo "-------------------"
echo "Current remotes:"
git remote -v

echo ""
echo "Current directories:"
ls -la | grep "^d" | grep -E "(sensor-data-service|camunda-service|proving-service|verifier-service|pcf-registry|sensor-key-registry)"

echo ""
echo "Setup complete! All subtrees have been configured."
echo ""
echo "To update subtrees in the future, you can run individual commands:"
echo "git fetch <service-name>"
echo "git subtree pull --prefix=<service-name> <service-name> main --squash"
echo ""
echo "Or run this script again to update all subtrees at once."
