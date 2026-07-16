# Load Testing Procedure

## Overview
This runbook describes how load testing is performed before major releases or capacity planning exercises.

## Tooling
Load tests are run using k6, with test scripts stored in the `load-tests` repository. Tests target a dedicated staging environment that mirrors production instance types and scaling configuration, never production directly.

## When to Load Test
- Before launching a feature expected to significantly increase traffic (e.g., a marketing campaign, new integration).
- Quarterly, as part of general capacity planning, to validate current scaling thresholds are still appropriate.
- After any major architectural change to a service's data path (e.g., adding a new database read replica pattern).

## Steps
1. Define the target scenario: expected peak requests per second, ramp-up pattern, and duration.
2. Update or write the k6 script to reflect the scenario, checked into the `load-tests` repo.
3. Run the test against staging: `k6 run --vus 100 --duration 10m scenario.js` (adjust vus/duration per scenario).
4. Monitor the staging Grafana dashboard during the run for error rate, latency, and autoscaling behavior.
5. Record results (max sustained RPS, latency at that load, point of degradation) in the load test log spreadsheet.
6. If results reveal a bottleneck, file a ticket with the owning team before the associated feature launches.

## Pass Criteria
A load test passes if the service sustains the target RPS with p99 latency under its defined SLO and error rate under 1%, with autoscaling successfully adding capacity within 2 minutes of increased load.
