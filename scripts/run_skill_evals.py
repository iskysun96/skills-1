#!/usr/bin/env python3
"""Plan or execute isolated A/B/C/D skill evaluations through a runner adapter."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {path.relative_to(ROOT)}: {error}") from error


def load_cases(skill: str) -> list[dict]:
    path = EVALS / "cases" / f"{skill}.json"
    data = load_json(path)
    if data.get("candidate") != skill or not isinstance(data.get("cases"), list):
        raise ValueError(f"invalid candidate case file: {path.relative_to(ROOT)}")
    cases = data["cases"]
    for compatibility in sorted((EVALS / "compatibility").glob("*.json")):
        extra = load_json(compatibility)
        if skill in extra.get("applies_to", []):
            cases.extend(extra.get("cases", []))
    seen: set[str] = set()
    for case in cases:
        required = {"id", "prompt", "fixture", "tags", "p0"}
        if not required.issubset(case) or case["id"] in seen:
            raise ValueError(f"invalid or duplicate case in {path.relative_to(ROOT)}")
        fixture_path = EVALS / "fixtures" / case["fixture"]
        if not fixture_path.is_file():
            raise ValueError(f"missing fixture: {fixture_path.relative_to(ROOT)}")
        seen.add(case["id"])
    return cases


def build_jobs(skill: str, repetitions: int, seed: int, manifest: dict) -> list[dict]:
    jobs = []
    for case in load_cases(skill):
        fixture = load_json(EVALS / "fixtures" / case["fixture"])
        for condition, config in manifest["conditions"].items():
            paths = [value.format(candidate=skill) for value in config["skills"]]
            missing = [value for value in paths if not (ROOT / value).is_dir()]
            if missing:
                raise ValueError(f"condition {condition} has missing skill paths: {missing}")
            for repetition in range(1, repetitions + 1):
                jobs.append({
                    "case": case,
                    "condition": condition,
                    "condition_name": config["name"],
                    "repetition": repetition,
                    "seed": seed,
                    "prompt": case["prompt"],
                    "fixture": fixture,
                    "skill_paths": [str((ROOT / value).resolve()) for value in paths],
                })
    random.Random(seed).shuffle(jobs)
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True, choices=("box-cli", "box-mcp"))
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--plan", action="store_true", help="print the randomized matrix without a runner")
    parser.add_argument("--runner", help="adapter command; JSON job in, JSON result out")
    parser.add_argument("--output", type=Path, help="result JSON path")
    args = parser.parse_args()

    try:
        manifest = load_json(EVALS / "manifest.yaml")
        if manifest.get("schema_version") != 1:
            raise ValueError("unsupported eval manifest schema")
        repetitions = args.repetitions or manifest["default_repetitions"]
        minimum = manifest["release_gates"]["minimum_repetitions"]
        if repetitions < 1:
            raise ValueError("repetitions must be positive")
        if not args.plan and repetitions < minimum and "mock_runner.py" not in (args.runner or ""):
            raise ValueError(f"real comparisons require at least {minimum} repetitions")
        seed = args.seed if args.seed is not None else manifest["seed"]
        jobs = build_jobs(args.skill, repetitions, seed, manifest)
    except (KeyError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.plan:
        plan = [{
            "order": index,
            "case": job["case"]["id"],
            "condition": job["condition"],
            "repetition": job["repetition"],
        } for index, job in enumerate(jobs, 1)]
        print(json.dumps({"skill": args.skill, "seed": seed, "jobs": plan}, indent=2))
        return 0

    if not args.runner or not args.output:
        parser.error("--runner and --output are required unless --plan is used")
    command = shlex.split(args.runner)
    if not command:
        parser.error("--runner cannot be empty")
    command = [
        str((ROOT / value).resolve()) if not Path(value).is_absolute() and (ROOT / value).exists() else value
        for value in command
    ]

    results = []
    failures = 0
    for index, job in enumerate(jobs, 1):
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="box-skill-eval-") as temp_dir:
            completed = subprocess.run(
                command,
                cwd=temp_dir,
                input=json.dumps(job),
                text=True,
                capture_output=True,
                check=False,
            )
        duration = round(time.monotonic() - started, 6)
        record = {
            "order": index,
            "case": job["case"]["id"],
            "condition": job["condition"],
            "repetition": job["repetition"],
            "duration_seconds": duration,
            "runner_exit_code": completed.returncode,
        }
        try:
            record["result"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            record["error"] = "runner did not return valid JSON"
        if completed.returncode or "error" in record:
            failures += 1
            record["runner_stderr"] = completed.stderr[-2000:]
        results.append(record)

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "skill": args.skill,
        "seed": seed,
        "repetitions": repetitions,
        "runner": command,
        "results": results,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        display_path = output.relative_to(ROOT)
    except ValueError:
        display_path = output
    print(f"wrote {len(results)} result(s) to {display_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
