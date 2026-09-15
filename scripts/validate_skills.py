#!/usr/bin/env python3
"""Validate skill structure, local references, metadata, secrets, and generated copies."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^]]*]\((?!https?://|#)([^)]+)\)")
GENERATED = "<!-- GENERATED FILE: DO NOT EDIT."
NEW_SKILLS = {"box-cli", "box-mcp"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    "hard-coded credential": re.compile(
        r"(?i)(?:client[_-]?secret|access[_-]?token|refresh[_-]?token|authorization[_-]?token)"
        r"\s*[:=]\s*[\"'](?!<|your-|redacted|example|bearer_token)[A-Za-z0-9._-]{16,}"
    ),
}


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


def metadata_errors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []
    for field in ("owner:", "last_verified:", "assumptions:", "sources:"):
        if field not in text[:600]:
            errors.append(f"{path.relative_to(ROOT)}: missing reference metadata '{field[:-1]}'")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", action="append", help="validate one skill; repeatable")
    args = parser.parse_args()
    selected = set(args.skill or [])
    errors: list[str] = []

    skill_dirs = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    known = {path.name for path in skill_dirs}
    if selected - known:
        errors.append(f"unknown skill(s): {', '.join(sorted(selected - known))}")
    if selected:
        skill_dirs = [path for path in skill_dirs if path.name in selected]

    inspected: list[Path] = []
    for skill_dir in skill_dirs:
        manifest = skill_dir / "SKILL.md"
        if not manifest.is_file():
            errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
            continue
        inspected.append(manifest)
        fields = parse_frontmatter(manifest)
        if fields.get("name") != skill_dir.name:
            errors.append(f"{manifest.relative_to(ROOT)}: name must match directory")
        if not NAME_RE.fullmatch(fields.get("name", "")):
            errors.append(f"{manifest.relative_to(ROOT)}: invalid skill name")
        if not fields.get("description"):
            errors.append(f"{manifest.relative_to(ROOT)}: missing description")

        for markdown in [manifest, *sorted((skill_dir / "references").glob("*.md"))]:
            inspected.append(markdown)
            text = markdown.read_text(encoding="utf-8")
            for raw_target in LINK_RE.findall(text):
                target = raw_target.split("#", 1)[0]
                resolved = (markdown.parent / target).resolve()
                if target and not resolved.is_file():
                    errors.append(f"{markdown.relative_to(ROOT)}: broken local link '{raw_target}'")
                elif target and skill_dir.name in NEW_SKILLS:
                    try:
                        resolved.relative_to(skill_dir.resolve())
                    except ValueError:
                        errors.append(f"{markdown.relative_to(ROOT)}: cross-skill link '{raw_target}'")
            for label, pattern in SECRET_PATTERNS.items():
                if not text.startswith(GENERATED) and pattern.search(text):
                    errors.append(f"{markdown.relative_to(ROOT)}: possible {label}")

        if skill_dir.name in NEW_SKILLS:
            for reference in sorted((skill_dir / "references").glob("*.md")):
                if not reference.read_text(encoding="utf-8").startswith(GENERATED):
                    errors.extend(metadata_errors(reference))

    if not selected or selected & NEW_SKILLS:
        for shared in sorted((ROOT / "shared" / "references").glob("*.md")):
            inspected.append(shared)
            errors.extend(metadata_errors(shared))

        command = [sys.executable, str(ROOT / "scripts" / "sync_shared_references.py"), "--check"]
        for skill in sorted(selected & NEW_SKILLS):
            command.extend(["--skill", skill])
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode:
            errors.append(result.stderr.strip() or result.stdout.strip())

    flat_references = list((ROOT / "shared" / "references").glob("*.md"))
    for skill in NEW_SKILLS:
        flat_references.extend((ROOT / "skills" / skill / "references").glob("*.md"))
    hashes: dict[str, Path] = {}
    for reference in flat_references:
        if not reference.is_file() or reference.read_text(encoding="utf-8").startswith(GENERATED):
            continue
        digest = hashlib.sha256(reference.read_bytes()).hexdigest()
        if digest in hashes:
            errors.append(
                f"duplicate hand-authored references: {hashes[digest].relative_to(ROOT)} and "
                f"{reference.relative_to(ROOT)}"
            )
        hashes[digest] = reference

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"validated {len(skill_dirs)} skill(s) and {len(set(inspected))} Markdown file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
