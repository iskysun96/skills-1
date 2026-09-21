#!/usr/bin/env python3
"""Create a deterministic, self-contained ZIP package for one skill."""

from __future__ import annotations

import argparse
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def skill_files(skill_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.parts)
    )


def build_archive(skill: str, output_dir: Path) -> Path:
    skill_dir = ROOT / "skills" / skill
    if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
        raise ValueError(f"unknown or invalid skill: {skill}")

    files = skill_files(skill_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{skill}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for source in files:
            relative = Path(skill) / source.relative_to(skill_dir)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, source.read_bytes())
    return archive


def verify_archive(archive: Path, skill: str) -> None:
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        if f"{skill}/SKILL.md" not in names:
            raise ValueError("package is missing SKILL.md")
        if any(name.startswith("/") or ".." in Path(name).parts for name in names):
            raise ValueError("package contains an unsafe path")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--check", action="store_true", help="build and verify in a temporary directory")
    args = parser.parse_args()

    try:
        if args.check:
            with tempfile.TemporaryDirectory(prefix="box-skill-package-") as temp_dir:
                archive = build_archive(args.skill, Path(temp_dir))
                verify_archive(archive, args.skill)
                print(f"validated portable package for {args.skill}")
        else:
            output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
            archive = build_archive(args.skill, output_dir)
            verify_archive(archive, args.skill)
            print(archive.relative_to(ROOT) if archive.is_relative_to(ROOT) else archive)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
