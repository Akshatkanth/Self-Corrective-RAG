# Incident Severity Classification

## Overview
This runbook defines how incidents are classified so that response urgency and escalation paths are consistent across the organization.

## Severity Levels

### SEV1 - Critical
Complete outage of a customer-facing service, or any incident involving data loss or a security breach. Examples: payments processing fully down, authentication service unavailable for all users, customer data exposed.
- Response time: immediate, all-hands
- Requires incident commander
- Status page must be updated within 10 minutes

### SEV2 - High
Significant degradation of a customer-facing service affecting a large subset of users, but not a complete outage. Examples: elevated error rates (5-20%) on checkout, major feature unavailable, latency severely degraded for a subset of regions.
- Response time: within 15 minutes
- On-call engineer leads response, may pull in additional engineers

### SEV3 - Moderate
Minor degradation or an issue affecting a small subset of users or internal tooling. Examples: non-critical background job failing, internal dashboard down, minor UI bug affecting a small user segment.
- Response time: within 1 business day
- Handled by on-call or relevant team during normal hours

### SEV4 - Low
Cosmetic issues, minor bugs with no functional impact, or issues fully mitigated by existing redundancy.
- Response time: next sprint planning

## Escalation
See the Incident Escalation Path runbook for who to contact at each severity level and how to declare an incident.
