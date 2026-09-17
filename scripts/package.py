#!/usr/bin/env python3
"""Build a reproducible universal release archive and SHA256SUMS."""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

EXCLUDED_DIRS = {".git", "dist", "tmp", "__pycache__", ".pytest_cache"}


def package_files(root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and not any(part in EXCLUDED_DIRS for part in path.parts)
            and path.suffix != ".pyc"
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def build(root: Path, output: Path) -> tuple[Path, Path]:
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not version or "\n" in version:
        raise ValueError("VERSION must contain one non-empty line")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"codex_workflow-{version}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(
        archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for source in package_files(root):
            relative = source.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"codex_workflow/{relative}")
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if source.suffix == ".sh" else 0o644
            info.external_attr = (0o100000 | mode) << 16
            bundle.writestr(info, source.read_bytes())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    sums = output / "SHA256SUMS"
    sums.write_text(f"{checksum}  {archive.name}\n", encoding="ascii")
    return archive, sums


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    archive, sums = build(args.root.resolve(), (args.output or args.root / "dist").resolve())
    print(f"created {archive}")
    print(f"created {sums}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
