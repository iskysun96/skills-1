<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Box CLI v4; command flags may evolve
sources:
  - https://developer.box.com/guides/cli/quick-start/
  - https://developer.box.com/guides/cli/quick-start/options-and-bulk-commands/
  - https://github.com/box/boxcli#usage
-->

# CLI Operating Patterns

## Construct commands safely

1. Confirm syntax with `box <topic>:<command> --help`; do not guess flags.
2. Resolve a human name to an ID with a list or search command.
3. Use `--json` for machine-readable output and `--fields` to limit the response.
4. Keep writes serial, especially when they share an environment or modify the same item.
5. Store large reports in a user-approved path rather than flooding context.

Useful read-only checks:

```bash
box users:get me --json --fields id,name,login
box folders:get 0 --json --fields id,name
box folders:items 0 --json --fields id,type,name --max-items 20
box search "project name" --json --fields id,type,name,parent --limit 20
```

Treat these as patterns, not a substitute for `--help` on the installed CLI version.

## Mutation pattern

Before a write, capture the current item and exact actor. For permission or access changes, show the proposed role and audience and obtain confirmation. After the command, read the returned ID with the same environment and actor and compare the relevant fields.

For errors, collect the compact evidence described in [reliability, errors, and evidence](box-reliability-errors-and-evidence.md). Never solve a 403 by silently switching to a more privileged actor.
