<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Box CLI v4 and Box Platform API v2
sources:
  - https://developer.box.com/guides/cli/quick-start/build-commands-help/
  - https://developer.box.com/reference/
  - https://developer.box.com/guides/api-calls/
-->

# REST API Fallback

Use this only when the installed CLI has no dedicated command.

## Preferred fallback: `box request`

Confirm syntax with `box request --help`, then call the documented Box API path through the CLI. This preserves the selected CLI environment, refresh behavior, and actor controls. Specify the HTTP method, body, and fields exactly as the current API reference requires.

Before running the request:

- verify the endpoint and method in the official Box API reference;
- confirm the actor and required scope;
- avoid embedding a token or secret in the command;
- show the user any destructive or access-changing payload;
- plan a read-after-write request.

## Raw HTTP

Use raw HTTP only if `box request` is unavailable or unsuitable and the user has an approved secure token source. Never ask for a token in chat or persist it in shell history. Prefer an existing secret manager or environment configured by the user. Apply the retry and evidence rules in [reliability, errors, and evidence](box-reliability-errors-and-evidence.md).

If the result is application code rather than an operator command, use an official Box SDK maintained for the project's language instead of turning this fallback into a custom auth implementation.
