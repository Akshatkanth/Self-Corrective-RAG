# Monitoring and Alerting Setup

## Overview
This runbook describes the monitoring stack and how alerts are configured for production services.

## Stack
- Metrics: Prometheus, scraped every 15 seconds from each service's `/metrics` endpoint.
- Dashboards: Grafana, with one dashboard per service plus a shared "Platform Overview" dashboard.
- Alerting: Alertmanager routes alerts to PagerDuty (for paging alerts) or Slack (for informational alerts).
- Logs: Centralized in Loki, queryable via Grafana Explore.

## Key Alerts

### High Error Rate
Fires when a service's 5xx error rate exceeds 2% over a 5-minute window. Routed to PagerDuty for the owning team's on-call.

### High Latency
Fires when p99 latency exceeds the service-specific SLO (defined per service in `alerting-rules.yaml`) for 5 consecutive minutes. Routed to PagerDuty.

### Pod Restart Loop
Fires when a pod restarts more than 3 times in 10 minutes. Routed to Slack #platform-alerts as informational, escalated to PagerDuty if restarts continue past 20 minutes.

### Disk Usage
Fires when any node's disk usage exceeds 85%. Routed to Slack #platform-alerts.

## Adding a New Alert
1. Add the alert rule to `alerting-rules.yaml` in the `monitoring` repository.
2. Specify severity (`page` or `notify`) in the alert's labels.
3. Open a PR and get review from the Platform team.
4. Once merged, the rule is automatically picked up by Prometheus within 5 minutes (no restart needed).

## Silencing Alerts
During planned maintenance, silence relevant alerts in Alertmanager UI beforehand to avoid unnecessary paging. Always set an expiration time on silences — do not leave indefinite silences active.
