#!/usr/bin/env python3
"""Validate skill structure, evaluation fixtures, links, and public-safe content."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_LINK_RE = re.compile(r"\[[^]]*]\((?!https?://|#)([^)]+)\)")
PRIVATE_PATH_RE = re.compile(r"(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)(?:client[_-]?secret|access[_-]?token|refresh[_-]?token|authorization[_-]?token)"
    r"\s*[:=]\s*[\"'](?!<|your-|redacted|example)[A-Za-z0-9._-]{16,}"
)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    raw = text[4:].split("\n---\n", 1)[0]
    values: dict[str, str] = {}
    current = ""
    for line in raw.splitlines():
        if line and not line.startswith((" ", "\t")) and ":" in line:
            current, value = line.split(":", 1)
            values[current.strip()] = value.strip().strip("'\"")
        elif current and line.strip():
            values[current] = f"{values[current]} {line.strip()}".strip()
    return values


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {error}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(ROOT)}: top-level JSON value must be an object")
        return {}
    return value


def main() -> int:
    errors: list[str] = []
    skill_dirs = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())

    for skill_dir in skill_dirs:
        manifest = skill_dir / "SKILL.md"
        if not manifest.is_file():
            errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
            continue
        fields = parse_frontmatter(manifest)
        if fields.get("name") != skill_dir.name:
            errors.append(f"{manifest.relative_to(ROOT)}: name must match its directory")
        if not NAME_RE.fullmatch(fields.get("name", "")):
            errors.append(f"{manifest.relative_to(ROOT)}: invalid skill name")
        if not fields.get("description"):
            errors.append(f"{manifest.relative_to(ROOT)}: missing description")

        markdown_files = [manifest, *sorted(skill_dir.glob("references/**/*.md"))]
        for markdown in markdown_files:
            text = markdown.read_text(encoding="utf-8")
            for raw_target in LOCAL_LINK_RE.findall(text):
                target = raw_target.split("#", 1)[0]
                if target and not (markdown.parent / target).resolve().is_file():
                    errors.append(f"{markdown.relative_to(ROOT)}: broken local link '{raw_target}'")

    cli_dir = ROOT / "skills" / "box-cli"
    cli_files = sorted(path.relative_to(cli_dir).as_posix() for path in cli_dir.rglob("*") if path.is_file())
    if cli_files != ["SKILL.md"]:
        errors.append(f"skills/box-cli: expected the single-file baseline, found {cli_files}")

    manifest = load_json(ROOT / "evals" / "manifest.json", errors)
    cases = load_json(ROOT / "evals" / "cases" / "box-cli.json", errors)
    fixture = load_json(ROOT / "evals" / "fixtures" / "box-sandbox.json", errors)
    compatibility = load_json(ROOT / "evals" / "compatibility" / "master-and-legal.json", errors)

    if manifest.get("schema_version") != 1:
        errors.append("evals/manifest.json: unsupported schema_version")
    if cases.get("candidate") != "box-cli" or not isinstance(cases.get("cases"), list):
        errors.append("evals/cases/box-cli.json: invalid candidate or cases")
    if "Entirely synthetic public test data" not in fixture.get("notice", ""):
        errors.append("evals/fixtures/box-sandbox.json: missing explicit synthetic-data notice")
    if compatibility.get("applies_to") != ["box-cli"]:
        errors.append("evals/compatibility/master-and-legal.json: invalid applies_to")

    case_ids: set[str] = set()
    for case in [*cases.get("cases", []), *compatibility.get("cases", [])]:
        if not isinstance(case, dict):
            errors.append("evaluation case must be an object")
            continue
        required = {"id", "prompt", "fixture", "tags", "critical"}
        if not required.issubset(case):
            errors.append(f"evaluation case is missing fields: {case}")
            continue
        if case["id"] in case_ids:
            errors.append(f"duplicate evaluation case id: {case['id']}")
        case_ids.add(case["id"])
        if not (ROOT / "evals" / "fixtures" / case["fixture"]).is_file():
            errors.append(f"missing fixture for case {case['id']}: {case['fixture']}")

    public_files = [
        ROOT / "skills" / "box-cli" / "SKILL.md",
        *sorted((ROOT / "evals").rglob("*.json")),
        *sorted((ROOT / "evals").rglob("*.md")),
        *sorted((ROOT / "evals" / "fixtures").rglob("*.py")),
    ]
    for path in public_files:
        text = path.read_text(encoding="utf-8")
        for label, pattern in (
            ("private key", PRIVATE_KEY_RE),
            ("hard-coded credential", SECRET_ASSIGNMENT_RE),
            ("machine-specific home path", PRIVATE_PATH_RE),
        ):
            if pattern.search(text):
                errors.append(f"{path.relative_to(ROOT)}: possible {label}")

    result_files = [path for path in (ROOT / "evals" / "results").iterdir() if path.name != ".gitkeep"]
    if result_files:
        errors.append("evals/results: generated results must remain untracked and absent from validation")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"validated {len(skill_dirs)} skills, {len(case_ids)} synthetic cases, and public-data boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
