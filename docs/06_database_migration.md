# Database Migration Procedure

## Overview
This runbook describes how to safely apply schema migrations to production databases (PostgreSQL) without downtime.

## Principles
- Migrations must be backward-compatible with the currently deployed application version. Never deploy a migration that the running code can't tolerate.
- Follow the expand-contract pattern: add new columns/tables first (expand), deploy code that uses them, then remove old columns/tables in a later release (contract). Never combine adding and removing in the same migration.
- All migrations must be reversible. Write both the "up" and "down" migration.

## Steps
1. Write the migration using the project's migration tool (Alembic for Python services, Flyway for Java services).
2. Test the migration against a staging database restored from a recent production snapshot.
3. Estimate migration duration. Migrations expected to take longer than 30 seconds on the production table size must be run during the designated low-traffic maintenance window (Sundays 2-4am UTC).
4. Get migration reviewed and approved by a member of the Database team, in addition to normal code review.
5. Apply the migration as a separate deployment step, before deploying the application code that depends on it.
6. Verify the migration applied cleanly by checking the schema version table and running a smoke test query.
7. Deploy the application code that uses the new schema.

## Rollback
If a migration needs to be reversed, run the corresponding "down" migration. Do not attempt to manually reverse schema changes via ad-hoc SQL — always use the migration tool so the schema version history stays consistent.

## Large Table Migrations
For tables exceeding 10 million rows, coordinate with the Database team to use online schema change tooling (e.g., `pg_repack` or batched backfills) to avoid locking the table.
