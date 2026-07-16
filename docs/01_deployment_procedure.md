# Standard Deployment Procedure

## Overview
This runbook describes the standard process for deploying a new release of the `payments-api` service to production. Deployments are performed via the CI/CD pipeline (GitHub Actions) and follow a canary-first strategy.

## Prerequisites
- Release branch has passed all CI checks (unit tests, integration tests, security scan).
- Change has been approved by at least one other engineer via pull request review.
- On-call engineer has been notified in the #deploys Slack channel.
- Deployment window is outside of peak traffic hours (avoid 9am-11am and 5pm-7pm UTC).

## Steps
1. Merge the release branch into `main`. This triggers the build pipeline automatically.
2. The pipeline builds a new Docker image and pushes it to the internal container registry with a tag matching the git commit SHA.
3. The image is deployed to the canary environment first, receiving 5% of production traffic.
4. Monitor the canary for 15 minutes. Check error rate, p99 latency, and CPU/memory usage on the Grafana "Payments Service Overview" dashboard.
5. If canary metrics are healthy (error rate under 0.5%, no latency regression), proceed to full rollout.
6. Full rollout is performed in three stages: 25% -> 50% -> 100% of traffic, with a 10-minute soak time between each stage.
7. After 100% rollout, monitor for an additional 30 minutes before considering the deployment complete.
8. Post a summary in #deploys including the version deployed, deployment time, and any anomalies observed.

## Rollback Trigger Conditions
If at any stage the error rate exceeds 2% or p99 latency increases by more than 50% compared to baseline, halt the rollout immediately and refer to the Rollback Procedure runbook.

## Notes
Deployments to the `payments-api` service require two-person approval due to its criticality. Other internal services (e.g., `notification-service`) only require one approver.
