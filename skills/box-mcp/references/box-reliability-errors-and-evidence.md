<!-- GENERATED FILE: DO NOT EDIT. Source: shared/references/reliability-errors-and-evidence.md; SHA256: ba529dbe6dcea37addbac1b32d11082b07eff11fbcb0b2c8b020a4691485f41d -->

<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Box Platform API v2 error and rate-limit behavior
sources:
  - https://developer.box.com/guides/api-calls/permissions-and-errors/common-errors/
  - https://developer.box.com/guides/api-calls/permissions-and-errors/rate-limits/
  - https://developer.box.com/guides/api-calls/permissions-and-errors/429/
-->

# Reliability, Errors, and Evidence

Diagnose against the same actor, object ID, and operation that failed.

| Signal | Check first |
| --- | --- |
| 400 | Request shape, field names, conflicting parameters |
| 401 | Expired or invalid credential; wrong token type or audience |
| 403 | Scope, enterprise policy, item permission, feature entitlement |
| 404 | Exact ID, item type, trash state, and actor access |
| 409 | Name collision, stale version, or conflicting state |
| 429 | `Retry-After`, request pacing, duplicate work, batch size |

## Retry policy

- Retry only transient failures and 429 responses.
- Honor `Retry-After`; otherwise use bounded exponential backoff with jitter.
- Do not blindly retry permission, validation, or conflict errors.
- Make event consumers and retryable mutations idempotent. Persist event IDs or operation keys when supported.

## Evidence bundle

For a reproducible failure, capture redacted evidence:

- UTC time and environment;
- acting user or service-account ID;
- tool, command, or endpoint and HTTP method;
- Box object type and ID;
- status/error code and message;
- request or correlation ID;
- retry count and `Retry-After` value;
- expected result and smallest reproducible input.

For a successful write, capture the returned ID and a read-after-write observation. Never include credentials or document contents unless strictly required and authorized.
