# Box Agent Skills

Agent Skills that help developers and AI agents work safely and effectively with the Box Developer Platform.

The skills in this repo follow the [Agent Skills](https://agentskills.io/) format and can also be installed as a plugin for platforms like Codex, [Cursor](https://cursor.com), [Claude](https://claude.com), including Claude Code and Cowork, and [Kiro](https://kiro.dev).

## Installation

### As an Agent Skill

```bash
# Choose skills interactively
npx skills add box/skills

# Or install one independently
npx skills add box/skills --skill box-mcp
npx skills add box/skills --skill box-cli
```

Check out the latest and full list of skills [here](https://skills.sh/box/skills).

### As a Platform Plugin

This repo can also be installed as a plugin for supported platforms. MCP connection and OAuth setup vary by platform — see the setup guide for your platform below.

The root `plugin.json` and `mcp.json` follow the [Agent Plugins v1.0.0 specification](https://agent-plugins.org/specification). The portable MCP configuration declares the Box MCP endpoint; authentication remains managed by each client. Do not add credentials to this repository's root `mcp.json`; configure them only in your client's settings.

| Platform | Setup guide |
|---|---|
| Codex | [`.codex-plugin/README.md`](.codex-plugin/README.md) |
| Cursor | [`.cursor-plugin/README.md`](.cursor-plugin/README.md) |
| Claude Code | [`.claude-plugin/README.md`](.claude-plugin/README.md) |
| Kiro | [Install as a Kiro Power](#kiro-power) |

### Kiro Power

In Kiro, open the Powers panel and install the Box Power. If it is not shown in the catalog, select **Add Custom Power** → **Import power from GitHub** and enter `https://github.com/box/skills`. The bundled skills work in both Kiro IDE and CLI.

Note that the Box MCP Server currently does not support Dynamic Client Registration, so credential-free Power authentication is not yet available in Kiro IDE. Kiro CLI users can configure Box OAuth client credentials in their user MCP settings; future managed OAuth integration or confidential-client OAuth support in the IDE can enable the bundled MCP connection there.

Try it with: `Use the Box Power to add Box file upload to this app.`

## Available Skills

| Skill | Purpose |
| --- | --- |
| `box` | Existing general Box foundation and router |
| `box-mcp` | Connect and operate Box's hosted MCP server |
| `box-cli` | Reproducible CLI operations with a REST API fallback |
| `box-legal-workflows` | Shared legal workflow guidance |
| `box-legal-workflows-intake` | Legal intake and onboarding |
| `box-legal-workflows-contract` | Contract review and monitoring |
| `box-legal-workflows-ma` | M&A virtual data rooms |

The `box-mcp` and `box-cli` skills contain every reference they need when installed alone. Maintainers edit canonical shared material under `shared/references/`; the sync script generates marked copies inside each independent skill.

## Usage

Skills are automatically available once installed. The agent will use them when relevant tasks are detected. Here are some example prompts:

### Implement Box content workflows

`Add Box file upload to my app`

`Create a shared link for this folder`

`Set up Box webhooks for new file events`

### Build document-driven flows

`Search my Box account for invoices`

`Use Box AI to classify documents`

`Wire webhooks to process new uploads`

### Troubleshoot integrations

`Debug 401 errors with my Box JWT auth`

`Fix webhook signature verification`

## Repository Structure

Each skill follows the [Agent Skills Open Standard](https://agentskills.io/):

- `SKILL.md` - Skill manifest with frontmatter, routing table, workflow steps, and guardrails
- `references/` - Individual reference files (auth, content workflows, MCP tool patterns, AI/retrieval, etc.)
- `shared/` - Canonical references and the map used to generate portable per-skill copies
- `scripts/` - Reference sync, validation, and comparative evaluation tools
- `evals/` - Synthetic cases, fixtures, rubric, and A/B/C/D comparison protocol

## Prerequisites

- **Box CLI** (optional) — Install from [developer.box.com/guides/cli](https://developer.box.com/guides/cli) for CLI-first verification.
- **BOX_ACCESS_TOKEN** (optional) — For direct REST verification when Box CLI is unavailable.

## Quick Verification

Preferred order for agent tooling is MCP first, Box CLI second, and direct REST only as a last-resort fallback.

```bash
# With Box CLI installed and authenticated:
box users:get me --json
box folders:items 0 --json --max-items 5

# Last-resort fallback (for sessions where MCP/CLI are unavailable):
export BOX_ACCESS_TOKEN="your-token"
curl -sS -H "Authorization: Bearer $BOX_ACCESS_TOKEN" -H "Accept: application/json" "https://api.box.com/2.0/folders/0"
```

## Contributing

Skills follow the [Agent Skills specification](https://agentskills.io). Keep each skill independently installable and load detailed references only when needed.

After editing canonical references, regenerate and validate the repository:

```bash
python3 scripts/sync_shared_references.py
python3 scripts/sync_shared_references.py --check
python3 scripts/validate_skills.py
python3 scripts/run_skill_evals.py --skill box-cli --plan
python3 scripts/run_skill_evals.py --skill box-mcp --plan
```

See [`evals/run-comparison.md`](evals/run-comparison.md) for the comparative reduction test and runner-adapter contract.

## License

MIT

## Privacy and Support

- [Box Privacy Policy](https://www.box.com/legal/privacypolicy)
- [Box Support](https://support.box.com/)
