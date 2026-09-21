# Public Evaluation Baseline

The repository contains a reproducible comparison protocol, synthetic cases, and a deterministic mock adapter. It does not contain private evaluation prompts, customer data, credentials, internal endpoints, model-provider traces, or real evaluation results.

## Comparison

Run each case under four isolated conditions with the same model, reasoning level, tools, prompt, permissions, and synthetic fixture:

- **A, tools only:** no Box skill.
- **B, master baseline:** the unchanged `box` skill.
- **C, candidate only:** `box-cli` installed independently.
- **D, full plugin:** the master, legal skills, and `box-cli` together.

Reset state between runs and randomize execution order with the manifest seed. Grade responses blind using [the rubric](rubric.md). One repetition is enough for a public smoke comparison; add repetitions when a result is close to a release gate, nondeterministic, or safety-sensitive.

## Public-data boundary

Only synthetic fixtures and generic prompts belong in this repository. Before adding or sharing an evaluation artifact, confirm that it contains none of the following:

- access tokens, secrets, private keys, cookies, authorization codes, or credential configuration;
- customer, employee, partner, tenant, enterprise, file, folder, or user data from a real Box environment;
- private repository content, internal hostnames, unpublished product details, or non-public support material;
- local home-directory paths, usernames, machine names, runner commands, or environment-variable values; or
- raw model transcripts, grader rationales, vendor request IDs, or traces that are not approved for public release.

Real runner output is local-only. `evals/results/*.json` is ignored by Git. Publish only a separately reviewed aggregate if Box explicitly approves it.

## Commands

Inspect the deterministic randomized plan:

```bash
python3 scripts/run_skill_evals.py --skill box-cli --plan
```

Smoke-test the runner contract without a model or Box account:

```bash
python3 scripts/run_skill_evals.py --skill box-cli \
  --runner "python3 evals/fixtures/mock_runner.py" \
  --output evals/results/box-cli-smoke.json
```

A real adapter receives one JSON job on standard input and returns one JSON object on standard output. The job includes the case, synthetic fixture, condition, repetition, seed, prompt, and resolved skill paths. The harness records the response locally but does not grade it or make network calls.
