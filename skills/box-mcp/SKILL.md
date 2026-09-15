---
name: box-mcp
description: >
  Connect and operate the hosted Box MCP server from AI clients and agents.
  Use for MCP setup, OAuth troubleshooting, runtime tool discovery, Box file and
  folder work, search, metadata, collaboration, Box AI, Hubs, and Doc Gen through
  mcp.box.com.
---

# Box MCP

Use Box's hosted MCP server for agent-driven Box work. This skill is independently installable; it does not require the `box` skill.

## Route the task

| Need | Read |
| --- | --- |
| Connect a client, enable MCP, authenticate, or diagnose missing tools | [Setup and clients](references/setup-and-clients.md) |
| Files, folders, search, metadata, collaboration, AI, Hubs, or Doc Gen | [Feature workflows](references/feature-workflows.md) |
| Shared Box safety and identity rules | [Box core](references/box-core.md), [authentication and identity](references/box-authentication-and-identity.md) |
| Errors, retries, or evidence | [Reliability, errors, and evidence](references/box-reliability-errors-and-evidence.md) |
| Missing or gated capability | [Feature availability and entitlements](references/box-feature-availability-and-entitlements.md) |

Read only the references needed for the current task.

## Workflow

1. Use runtime tool discovery; never assume every documented tool is enabled.
2. Call `who_am_i`. If it fails, use the client's reconnect or OAuth flow and follow [setup and clients](references/setup-and-clients.md).
3. State the authenticated user and constrain work to the requested files, folders, or hub.
4. Resolve names to IDs with search or folder listing, then read details before a mutation.
5. Get confirmation before deletion, access changes, external sharing, collaboration changes, or a broad or higher-cost AI operation.
6. Invoke the smallest suitable tool with explicit IDs and fields. Run dependent mutations in order.
7. Verify mutations with a read using the same MCP connection and actor.
8. Return object IDs, actor, action, and verification; redact secrets and unnecessary content.

## Non-negotiable rules

- Use `https://mcp.box.com` for new integrations. The community self-hosted Box MCP server is deprecated.
- Never fabricate a tool that runtime discovery does not expose.
- Do not place OAuth credentials or bearer tokens in prompts, source control, or repository MCP configuration.
- A missing tool may be disabled by default, outside the actor's entitlement, or unsupported by the client. Diagnose before falling back.
- Upload and download URL tools require a code-executing client capable of a direct network transfer; do not claim they work in declarative-only clients.
