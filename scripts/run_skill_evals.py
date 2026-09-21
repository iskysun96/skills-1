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
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def load_cases(skill: str) -> list[dict]:
    path = EVALS / "cases" / f"{skill}.json"
    data = load_json(path)
    if data.get("candidate") != skill or not isinstance(data.get("cases"), list):
        raise ValueError(f"invalid candidate case file: {path.relative_to(ROOT)}")
    cases = list(data["cases"])
    for compatibility_path in sorted((EVALS / "compatibility").glob("*.json")):
        compatibility = load_json(compatibility_path)
        if skill in compatibility.get("applies_to", []):
            cases.extend(compatibility.get("cases", []))
    return cases


def build_jobs(skill: str, repetitions: int, seed: int, manifest: dict) -> list[dict]:
    jobs: list[dict] = []
    for case in load_cases(skill):
        fixture_path = EVALS / "fixtures" / case["fixture"]
        fixture = load_json(fixture_path)
        for condition, config in manifest["conditions"].items():
            relative_paths = [value.format(candidate=skill) for value in config["skills"]]
            missing = [value for value in relative_paths if not (ROOT / value).is_dir()]
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
                    "skill_paths": [str((ROOT / value).resolve()) for value in relative_paths],
                })
    random.Random(seed).shuffle(jobs)
    return jobs


def resolve_output(path: Path) -> Path:
    output = path if path.is_absolute() else ROOT / path
    output = output.resolve()
    if output.is_relative_to(ROOT) and not output.is_relative_to((EVALS / "results").resolve()):
        raise ValueError("repository-local results must be written under ignored evals/results/")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--runner", help="adapter command; JSON job in, JSON result out")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        manifest = load_json(EVALS / "manifest.json")
        if manifest.get("schema_version") != 1:
            raise ValueError("unsupported evaluation manifest schema")
        repetitions = args.repetitions or manifest["default_repetitions"]
        if repetitions < 1:
            raise ValueError("repetitions must be positive")
        seed = args.seed if args.seed is not None else manifest["seed"]
        jobs = build_jobs(args.skill, repetitions, seed, manifest)
    except (KeyError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.plan:
        plan = [
            {
                "order": index,
                "case": job["case"]["id"],
                "condition": job["condition"],
                "repetition": job["repetition"],
            }
            for index, job in enumerate(jobs, 1)
        ]
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

    try:
        output = resolve_output(args.output)
    except ValueError as error:
        parser.error(str(error))

    results: list[dict] = []
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
        record = {
            "order": index,
            "case": job["case"]["id"],
            "condition": job["condition"],
            "repetition": job["repetition"],
            "duration_seconds": round(time.monotonic() - started, 6),
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

    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "skill": args.skill,
        "seed": seed,
        "repetitions": repetitions,
        "runner": Path(command[0]).name,
        "results": results,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(results)} local result(s) to {output.name}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
