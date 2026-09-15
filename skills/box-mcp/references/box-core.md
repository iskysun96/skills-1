<!-- GENERATED FILE: DO NOT EDIT. Source: shared/references/core.md; SHA256: c124a0c08ad6d56c1198dbd2f99e81c085dece2121f520a00c4f8d8fd04f86e7 -->

<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Box Platform API v2; effective access remains actor-dependent
sources:
  - https://developer.box.com/guides/
  - https://developer.box.com/reference/
-->

# Box Core Operating Rules

Use this reference for rules shared by independently installable Box skills.

## Before acting

1. Identify the authenticated Box user or service account.
2. Resolve resources to immutable Box IDs; names and paths are context, not identity.
3. Read the target before changing it. For ambiguous names, present candidates instead of guessing.
4. Request only the fields and content required for the task.

## Mutations

- Get confirmation before deleting content, widening access, changing collaborators or shared links, switching actor, or starting a broad batch.
- Prefer the narrowest role, scope, audience, and folder boundary that completes the task.
- Run dependent writes in order. Do not parallelize operations that can race on auth state or the same object.
- Verify every mutation with a read using the same actor. Report the object ID and observed state.

## Content and secrets

- Keep access tokens, refresh tokens, client secrets, private keys, authorization codes, and configuration files out of prompts, logs, source control, and command output.
- Prefer Box-native search, metadata, previews, and Box AI over downloading file bodies when they can answer the question.
- Do not expose file contents or metadata beyond the audience and purpose the user authorized.

## Output discipline

- Prefer structured, field-limited results. Paginate deliberately and summarize large collections.
- Preserve IDs returned by Box rather than reconstructing paths later.
- On failure, report the actor, operation, object ID, status or error code, and a redacted request correlation ID when available.
