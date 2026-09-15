<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Hosted Box MCP; client OAuth configuration varies
sources:
  - https://developer.box.com/guides/box-mcp/
  - https://developer.box.com/guides/box-mcp/setup/
  - https://docs.box.com/en/box-mcp/supported-ai-platforms
-->

# Setup and Clients

Box hosts the MCP endpoint at `https://mcp.box.com`; do not run a local server for the standard integration.

## Connect

1. Prefer the client's official Box integration or marketplace flow when available.
2. Otherwise follow the current platform-specific Box guide. Client configuration and redirect URIs differ.
3. A Box administrator enables the MCP integration. Custom or unlisted clients may require Integration Credentials, a matching redirect URI, and required access scopes in the Admin Console.
4. Store credentials only in the client's protected credential mechanism. Repository configuration may contain the endpoint, but never secrets.
5. Complete OAuth as the intended user and verify with `who_am_i`.

## Diagnose

If the connection or tools are missing, check in this order:

1. The client supports remote HTTP MCP and shows the server connected.
2. The endpoint is exactly `https://mcp.box.com`.
3. OAuth was completed by the intended user and the redirect URI matches.
4. The Box administrator enabled the MCP integration and necessary tool access.
5. Application scopes, user permissions, plan, and feature entitlements cover the operation.
6. Runtime discovery exposes the desired tool; some write tools are off by default.

Reconnect through the client's auth flow rather than editing tokens. For identity and permission behavior, read [authentication and identity](box-authentication-and-identity.md). For gated tools, read [feature availability and entitlements](box-feature-availability-and-entitlements.md).
