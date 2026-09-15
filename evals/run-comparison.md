# Comparative Reduction Test

Run each case under four isolated conditions with the same model, reasoning, tools, prompt, permissions, and synthetic fixture:

- A — tools only, no Box skill.
- B — current experience, the unchanged `box` master skill.
- C — candidate skill installed alone.
- D — candidate alongside the master and existing legal skills.

Use at least three repetitions, reset state between runs, randomize execution order, and blind grading. Apply [the rubric](rubric.md), then enforce the gates in `manifest.yaml`.

## Harness

Validate and inspect the randomized run plan:

```bash
python3 scripts/run_skill_evals.py --skill box-cli --plan
```

Smoke-test the runner protocol without calling a model:

```bash
python3 scripts/run_skill_evals.py --skill box-cli --repetitions 1 \
  --runner "python3 evals/fixtures/mock_runner.py" \
  --output evals/results/box-cli-smoke.json
```

A real runner adapter receives one JSON job on standard input and must return one JSON object on standard output. The job contains `prompt`, `fixture`, resolved `skill_paths`, condition, case metadata, repetition, and seed. The response should include the model output, tool calls, outcome, and token/latency metrics. The harness captures errors and duration without interpreting vendor-specific traces.

The mock runner proves only that the repository's comparison pipeline is reproducible. It is not evidence that a skill is effective. Human or model graders should consume the saved real-run results using the rubric, blinded to condition labels.
