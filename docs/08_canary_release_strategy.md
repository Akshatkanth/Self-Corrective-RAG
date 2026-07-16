# Canary Release Strategy

## Overview
This runbook describes the canary release strategy used across services, which is the traffic-shifting mechanism referenced in the Standard Deployment Procedure.

## What Is a Canary Release
A canary release routes a small percentage of production traffic to the new version while the majority of traffic continues to the stable version. This limits the blast radius of a bad release before it reaches all users.

## How Canary Routing Works
Traffic splitting is handled by the Istio service mesh using weighted routing rules. The canary and stable versions run simultaneously as separate Kubernetes deployments behind the same service.

## Standard Canary Stages
1. 5% traffic to canary, 15-minute soak.
2. 25% traffic to canary, 10-minute soak.
3. 50% traffic to canary, 10-minute soak.
4. 100% traffic to canary (canary becomes the new stable version); old version is scaled down after 30 minutes.

## Automated vs Manual Promotion
Services with mature test coverage and stable metrics history use automated canary analysis (via Flagger), which automatically promotes or rolls back based on the same error rate and latency thresholds defined in the Deployment Procedure runbook. Services without automated analysis configured require a human to manually approve each stage promotion in the CI/CD pipeline UI.

## Aborting a Canary
If canary metrics breach thresholds at any stage, the pipeline automatically routes 100% of traffic back to the stable version and marks the deployment as failed. This is distinct from a full Rollback Procedure, since the stable version was never fully replaced — no rollback command is needed, but the failure should still be investigated before retrying.
