# Configuration Management

## Overview
This runbook describes how application configuration (non-secret) is managed across environments.

## Storage
Configuration is stored as Kubernetes ConfigMaps, defined declaratively in the `k8s-config` repository as YAML, organized by environment (`staging/`, `production/`) and service.

## Changing Configuration
1. Open a PR against the relevant environment/service YAML file in `k8s-config`.
2. Get review from at least one engineer on the owning team.
3. Merge triggers a sync via ArgoCD, which applies the change to the cluster automatically within a few minutes.
4. For changes that require a pod restart to take effect (most non-hot-reloadable config), ArgoCD's sync will trigger a rolling restart automatically if the ConfigMap is mounted as an environment variable; if mounted as a file, some services require a manual `kubectl rollout restart`.

## Environment-Specific Overrides
Each service has a base config plus environment-specific overlays (using Kustomize), so common values are defined once and only environment differences need to be specified per environment.

## Feature Flags
Feature flags are managed separately via LaunchDarkly, not through ConfigMaps, since they need to be toggled at runtime without a deployment. See the team wiki's LaunchDarkly guide for flag creation and targeting rules.

## Auditing
All changes to `k8s-config` are tracked via git history, and ArgoCD additionally logs every sync event with a diff, viewable in the ArgoCD UI for audit purposes.
