# Incident Escalation Path

## Overview
This runbook describes who to contact and in what order when an incident is declared, based on its severity (see Incident Severity Classification runbook).

## Declaring an Incident
Any engineer can declare an incident by running `/incident declare` in Slack, which creates a dedicated incident channel and pages the on-call engineer via PagerDuty.

## Escalation Order

### SEV1
1. Page primary on-call engineer immediately via PagerDuty.
2. If no acknowledgment within 5 minutes, PagerDuty auto-escalates to secondary on-call.
3. If no acknowledgment within 10 minutes total, escalate to Engineering Manager on-call.
4. Incident Commander role is assigned to the first engineering lead or manager who joins the incident channel.
5. Notify Customer Support lead so external communications can begin.

### SEV2
1. Page primary on-call engineer.
2. If no acknowledgment within 15 minutes, escalate to secondary on-call.
3. Engineering Manager is notified but not paged; they may join at their discretion.

### SEV3 / SEV4
No paging required. Create a ticket and route to the relevant team's backlog. On-call may address during business hours if capacity allows.

## Handoff
At shift change, the outgoing on-call engineer must brief the incoming on-call engineer on any open incidents, recent deployments, and any flaky alerts to watch for. Handoff notes are posted in #oncall-handoff.

## Post-Incident
All SEV1 and SEV2 incidents require a postmortem document within 3 business days, following the standard postmortem template stored in the engineering wiki.
