# Rollback Procedure

## Overview
This runbook describes how to roll back a production deployment when a release introduces errors, performance regressions, or unexpected behavior. Rollbacks should be fast and low-risk; this is not the place to debug root cause.

## When to Roll Back
- Error rate exceeds 2% sustained for more than 3 minutes.
- p99 latency increases by more than 50% compared to pre-deploy baseline.
- Any SEV1 or SEV2 incident is directly attributed to a recent deployment.
- A deploying engineer or on-call engineer judges the release unsafe, even without hard metric breaches.

## Steps
1. Identify the last known-good image tag from the deployment history in the CI/CD dashboard (look for the tag deployed before the current one).
2. Run the rollback command: `kubectl rollout undo deployment/<service-name> -n production`.
3. Alternatively, use the pipeline's "Rollback to previous version" button, which redeploys the last known-good image tag automatically.
4. Monitor the rollout status: `kubectl rollout status deployment/<service-name> -n production`.
5. Once traffic has shifted back to the previous version, confirm error rate and latency have returned to baseline on the Grafana dashboard.
6. Post in #incidents (if an active incident) or #deploys (if precautionary) with the rollback reason, the version rolled back from and to, and current system status.
7. Create a follow-up ticket to investigate root cause before attempting the deployment again.

## Rollback Time Expectations
A rollback should restore traffic to the previous version within 3-5 minutes of initiating the rollback command. If rollback is not restoring service within 10 minutes, escalate immediately per the Incident Escalation runbook.

## Database Migrations
If the deployment included a database migration, do not roll back the application code without first checking the Database Migration runbook — rolling back application code against a migrated schema can cause data corruption.
