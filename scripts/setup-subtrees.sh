#!/bin/bash
set -e

# Default branch to pull from (can be overridden)
BRANCH="${1:-main}"

echo "Setting up Git Subtrees for Integration Repository"
echo "================================================="
echo "Using branch: $BRANCH"
echo ""

# Define all service repositories (compatible with bash 3.2+)
SERVICES=(
    "sensor-data-service:https://github.com/ACP-PCVCF/sensor-data-service.git"
    "camunda-service:https://github.com/ACP-PCVCF/camunda-service.git"
    "proving-service:https://github.com/ACP-PCVCF/proving-service.git"
    "verifier-service:https://github.com/ACP-PCVCF/verifier.git"
    "pcf-registry:https://github.com/ACP-PCVCF/pcf-registry.git"
    "sensor-key-registry:https://github.com/ACP-PCVCF/sensor-key-registry.git"
)

echo "Step 1: Adding Git Remotes"
echo "--------------------------"
for service_entry in "${SERVICES[@]}"; do
    service="${service_entry%%:*}"
    repo_url="${service_entry#*:}"
    
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
for service_entry in "${SERVICES[@]}"; do
    service="${service_entry%%:*}"
    echo "Fetching all branches for $service..."
    if git fetch "$service" --prune; then
        echo "Fetched all branches for $service"
    else
        echo "Failed to fetch $service"
        exit 1
    fi
done

echo ""
echo "Step 3: Pulling Subtrees"
echo "------------------------"
for service_entry in "${SERVICES[@]}"; do
    service="${service_entry%%:*}"
    echo "Processing subtree for $service (branch: $BRANCH)..."
    
    # Check if subtree directory already exists
    if [ -d "$service" ]; then
        echo "Directory '$service' exists, pulling updates..."
        if git subtree pull --prefix="$service" "$service" "$BRANCH" --squash; then
            echo "Updated subtree for $service from $BRANCH"
        else
            echo "Failed to update subtree for $service"
            echo "  This might happen if the branch doesn't exist or there are conflicts"
        fi
    else
        echo "Directory '$service' doesn't exist, adding new subtree..."
        if git subtree add --prefix="$service" "$service" "$BRANCH" --squash; then
            echo "Added new subtree for $service from $BRANCH"
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
echo "✅ Setup complete! All subtrees have been configured."
echo ""
