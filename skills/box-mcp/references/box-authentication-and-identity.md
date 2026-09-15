<!-- GENERATED FILE: DO NOT EDIT. Source: shared/references/authentication-and-identity.md; SHA256: 3b4def07510127f4de63d2b160466b58e97c58c22ee2e5898c9067e3eba7641b -->

<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Current OAuth 2.0, CCG, JWT, and developer-token guidance
sources:
  - https://developer.box.com/guides/authentication/
  - https://developer.box.com/guides/authentication/tokens/
  - https://developer.box.com/guides/authorization/
-->

# Authentication and Identity

Choose authentication from the actor and deployment model, not convenience alone.

| Need | Preferred path |
| --- | --- |
| A person authorizes access to their Box content | OAuth 2.0 user authentication |
| Unattended server workload without a key-pair requirement | Client Credentials Grant (CCG) |
| Unattended server workload that requires key-pair authentication | JWT |
| Short local experiment | Developer token, never production |

CCG and JWT server applications require enterprise administrator authorization. OAuth applications may also require approval under enterprise policy. Scopes set the application's ceiling, while the acting user's permissions further restrict what it can access.

## Identity checklist

Before a read or write, record:

- application and authentication method;
- authenticated user or service-account ID;
- whether impersonation or an `As-User` header is active;
- enterprise and application scopes relevant to the operation;
- target item ID and the actor's effective permission.

Do not treat a successful login as proof that a specific item is accessible. A 404 can intentionally hide content from an actor who lacks access.

## Token handling

- Let the client, CLI, or official SDK store and refresh credentials when possible.
- Never print environment configuration as an authentication check.
- Never ask a user to paste a secret into chat. Direct them to the client credential store, OS keychain, environment, or secret manager.
- Reauthenticate through the supported flow when refresh is no longer possible; do not improvise token exchange logic.
