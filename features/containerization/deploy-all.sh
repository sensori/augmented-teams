#!/bin/bash

# Common Deploy All Script
# Orchestrates deployment of all features using repository_dispatch

set -e

echo "🚀 Starting common deployment orchestration..."

# Get the current branch and commit SHA
BRANCH=${1:-$(git rev-parse --abbrev-ref HEAD)}
COMMIT_SHA=${2:-$(git rev-parse HEAD)}

echo "📋 Deployment details:"
echo "  Branch: $BRANCH"
echo "  Commit: $COMMIT_SHA"

# Function to trigger feature deployment
trigger_deployment() {
    local feature_name=$1
    local event_type="deploy-${feature_name}"
    
    echo "🔄 Triggering deployment for $feature_name..."
    
    # Use GitHub CLI to trigger repository dispatch
    gh api repos/:owner/:repo/dispatches \
        -H "Accept: application/vnd.github.v3+json" \
        -f event_type="$event_type" \
        -f client_payload='{"ref":"'$BRANCH'","sha":"'$COMMIT_SHA'"}'
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully triggered $feature_name deployment"
    else
        echo "❌ Failed to trigger $feature_name deployment"
        exit 1
    fi
}

# Deploy features in order
trigger_deployment "git-integration"
trigger_deployment "vector-search"
trigger_deployment "update-gpt-instructions"

echo "🎉 Common deployment orchestration completed!"
echo "📦 All features have been triggered for deployment"
echo "🔗 Check individual feature workflows for detailed status"
