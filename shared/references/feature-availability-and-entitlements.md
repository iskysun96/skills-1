<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Hosted Box MCP; actual tools depend on admin settings and entitlement
sources:
  - https://developer.box.com/guides/box-mcp/
  - https://developer.box.com/guides/box-mcp/setup/
  - https://developer.box.com/guides/box-mcp/tools/
-->

# Feature Availability and Entitlements

Do not infer that a Box feature is available because a tool name appears in documentation or a skill.

Before depending on a feature:

1. Discover the tools exposed by the connected client at runtime.
2. Confirm the Box administrator enabled the integration and required access scopes.
3. Confirm the enterprise plan, user entitlement, and regional or rollout availability in current Box documentation.
4. Confirm the authenticated actor can access the target content.
5. If the feature is absent, explain which check failed and offer a supported alternative; do not fabricate a tool call.

Feature availability, tool names, limits, and costs can change. Re-check the official Box MCP tool catalog before adding or changing feature-specific instructions. Treat higher-cost AI operations and broad retrieval as an explicit planning decision: narrow the content set, estimate volume, and obtain confirmation before a large run.
