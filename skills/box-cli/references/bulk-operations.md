<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Box CLI v4 native bulk support varies by command
sources:
  - https://developer.box.com/guides/cli/quick-start/options-and-bulk-commands/
  - https://github.com/box/boxcli#readme
-->

# Bulk Operations

Use native CLI bulk input when the installed command supports it. Confirm its exact CSV columns and flags with `--help`; they vary by command and version.

## Safe batch plan

1. Inventory source IDs, target IDs, current state, and actor.
2. Create a deterministic input file containing IDs rather than ambiguous names.
3. Test one representative row, then a small sample.
4. Present total count, mutation type, access impact, and rollback or recovery plan.
5. Obtain confirmation for destructive, permission-changing, impersonated, or broad work.
6. Run the supported bulk command once. Do not launch concurrent CLI processes against the same environment.
7. Save structured results, separate successes from failures, and retry only transient failures.
8. Reconcile expected and observed counts with read-only queries.

Prefer restartable batches: include a stable row key, record returned Box IDs, and skip completed rows on rerun. A partial failure must not cause successful rows to be replayed blindly.

For an endpoint without a native bulk command, use a bounded script with an official Box SDK when the user is building durable application code. For one-off CLI work, use [REST API fallback](rest-api-fallback.md) and keep pacing and evidence explicit.
