<!--
owner: Box Developer Relations
last_verified: 2026-09-15
assumptions: Box CLI v4; confirm flags against the installed version
sources:
  - https://github.com/box/boxcli#readme
  - https://github.com/box/boxcli/blob/main/docs/login.md
  - https://github.com/box/boxcli/blob/main/docs/authentication.md
-->

# Setup and Profiles

## Install

Use the current Windows or macOS installer from the Box CLI releases, or install with Node.js:

```bash
npm install --global @box/cli
box --version
```

## Choose a login flow

Ask whether the CLI and browser are on the same computer.

- Local browser, content operations: have the user run `box login -d`. The official CLI app requires no Developer Console app and uses content-action scopes.
- Headless or remote shell: have the user run `box login --code` and complete the displayed URL and code flow themselves.
- Custom scopes or application configuration: have the user run `box login --platform-app` and enter credentials only in the CLI prompt.
- JWT or CCG automation: create and authorize a server application, protect its configuration file, then add it with the command documented for that auth method. Do not commit the configuration file.

Developer tokens are for short local experiments only. Do not build production automation around them.

## Profiles and actors

Use named environments when multiple enterprises or identities are needed. Select the intended environment explicitly for a task and verify it with:

```bash
box users:get me --json --fields id,name,login
```

Use impersonation only when the application and administrator permit it, and only after the user confirms the target actor. Apply the same actor flag to both the write and its verification. Do not use environment-inspection commands that reveal stored credentials.

For the underlying auth choices and permission intersection, read [authentication and identity](box-authentication-and-identity.md).
