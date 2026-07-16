# Secrets Rotation Procedure

## Overview
This runbook covers how to rotate credentials, API keys, and certificates used by production services.

## Secrets Inventory
All secrets are stored in HashiCorp Vault under the `production/` path, namespaced by service (e.g., `production/payments-api/db-password`). Services fetch secrets at startup via the Vault Agent sidecar; they are never baked into container images or committed to source control.

## Routine Rotation Schedule
- Database credentials: every 90 days.
- Third-party API keys (payment processor, email provider): every 180 days, or per vendor requirement.
- TLS certificates: auto-renewed 30 days before expiry via cert-manager; no manual action needed under normal circumstances.
- Internal service-to-service auth tokens: every 90 days.

## Rotation Steps
1. Generate the new credential with the issuing system (database, vendor dashboard, or internal auth service).
2. Write the new value to Vault under a new versioned path (Vault keeps version history automatically).
3. Trigger a rolling restart of the affected service so pods pick up the new secret via the Vault Agent sidecar. Use `kubectl rollout restart deployment/<service-name> -n production`.
4. Confirm the service is healthy post-restart by checking error rates on Grafana.
5. Revoke the old credential at the source system only after confirming the new one is in use (typically wait 24 hours).

## Emergency Rotation
If a secret is suspected to be compromised, skip the wait period: rotate immediately and revoke the old credential right away, accepting brief risk of service disruption over the risk of continued exposure. Declare a SEV2 incident to track the rotation and any required follow-up (e.g., auditing access logs).
