#!/usr/bin/env python3
"""Materialize canonical shared references into independently installable skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "shared" / "reference-map.json"
MARKER = "<!-- GENERATED FILE: DO NOT EDIT."


def fail(message: str) -> None:
    raise ValueError(message)


def inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def load_jobs(selected: set[str] | None) -> list[tuple[Path, Path, str]]:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("references"), list):
        fail(f"Unsupported map schema: {MAP_PATH}")

    jobs: list[tuple[Path, Path, str]] = []
    known_skills: set[str] = set()
    destinations: set[Path] = set()
    for entry in data["references"]:
        source = (ROOT / entry["source"]).resolve()
        if not inside(source, ROOT / "shared" / "references") or not source.is_file():
            fail(f"Invalid shared source: {entry.get('source')}")
        output = entry["output"]
        if Path(output).name != output or not output.endswith(".md"):
            fail(f"Output must be one Markdown filename: {output}")
        source_text = source.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() + "\n"
        digest = hashlib.sha256(source_text.encode()).hexdigest()
        relative_source = source.relative_to(ROOT).as_posix()
        body = (
            f"{MARKER} Source: {relative_source}; SHA256: {digest} -->\n\n"
            f"{source_text}"
        )
        for skill in entry["skills"]:
            known_skills.add(skill)
            if selected and skill not in selected:
                continue
            skill_dir = ROOT / "skills" / skill
            if not skill_dir.is_dir():
                fail(f"Mapped skill directory does not exist: {skill_dir.relative_to(ROOT)}")
            destination = skill_dir / "references" / output
            if destination in destinations:
                fail(f"Duplicate generated destination: {destination.relative_to(ROOT)}")
            destinations.add(destination)
            jobs.append((source, destination, body))

    unknown = (selected or set()) - known_skills
    if unknown:
        fail(f"Unknown mapped skill(s): {', '.join(sorted(unknown))}")
    return jobs


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not path.read_text(encoding="utf-8").startswith(MARKER):
        fail(f"Refusing to overwrite hand-authored file: {path.relative_to(ROOT)}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if copies are missing or stale")
    parser.add_argument("--skill", action="append", help="limit work to a mapped skill; repeatable")
    args = parser.parse_args()

    try:
        jobs = load_jobs(set(args.skill) if args.skill else None)
        stale: list[str] = []
        expected = {destination.resolve() for _, destination, _ in jobs}
        for _, destination, content in jobs:
            relative = destination.relative_to(ROOT).as_posix()
            if args.check:
                if not destination.is_file() or destination.read_text(encoding="utf-8") != content:
                    stale.append(relative)
            else:
                write_atomic(destination, content)
                print(f"synced {relative}")

        if args.check and not args.skill:
            for candidate in (ROOT / "skills").glob("*/references/*.md"):
                if candidate.resolve() not in expected and candidate.read_text(encoding="utf-8").startswith(MARKER):
                    stale.append(f"{candidate.relative_to(ROOT).as_posix()} (orphaned)")

        if stale:
            print("Shared references are missing, stale, or orphaned:", file=sys.stderr)
            for path in stale:
                print(f"  - {path}", file=sys.stderr)
            print("Run: python3 scripts/sync_shared_references.py", file=sys.stderr)
            return 1
        if args.check:
            print(f"shared references are synchronized ({len(jobs)} copies)")
        return 0
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
