---
name: box-cli
description: >
  Operate Box from the command line for content, search, metadata, collaboration,
  administration, troubleshooting, and bulk work. Use when a developer asks an
  agent to install, authenticate, or run the Box CLI, translate a Box task into
  reproducible commands, or use the Box REST API when the CLI lacks a command.
---

# Box CLI

Use the official Box CLI for reproducible Box operations and verification. This skill is independently installable; it does not require the `box` skill.

## Route the task

| Need | Read |
| --- | --- |
| Install, login, profiles, or actor selection | [Setup and profiles](references/setup-and-profiles.md) |
| Safe command construction, output, or verification | [CLI operating patterns](references/cli-operating-patterns.md) |
| Repeated or high-volume work | [Bulk operations](references/bulk-operations.md) |
| No matching CLI command | [REST API fallback](references/rest-api-fallback.md) |
| Shared Box safety and identity rules | [Box core](references/box-core.md), [authentication and identity](references/box-authentication-and-identity.md) |
| Errors, retries, or evidence | [Reliability, errors, and evidence](references/box-reliability-errors-and-evidence.md) |

Read only the references needed for the current task.

## Workflow

1. Check availability with `command -v box` and `box --version`.
2. If setup is needed, determine whether the terminal has a local browser before choosing a login flow. Never perform an interactive credential prompt on the user's behalf.
3. Confirm the actor without exposing configuration:

   ```bash
   box users:get me --json --fields id,name,login
   ```

4. Resolve names to Box IDs with read-only commands. Ask the user to choose if matches are ambiguous.
5. Show or explain permission-sensitive and destructive changes before running them.
6. Run commands serially. Use `--json` and the smallest useful `--fields` set.
7. Verify writes with a read using the same profile and actor.
8. Return the command, actor, affected object IDs, and verification result with secrets redacted.

## Non-negotiable rules

- Do not print or inspect raw environment configuration as an auth check.
- Do not place tokens, client secrets, private keys, or authorization codes in commands, source files, or chat.
- Get confirmation before deletion, collaboration or shared-link changes, impersonation, or a broad batch.
- Prefer `box request` before raw HTTP when a REST endpoint has no dedicated CLI command; it reuses the selected CLI identity.
- Direct HTTP is a last fallback and requires an explicitly provided secure auth mechanism.
