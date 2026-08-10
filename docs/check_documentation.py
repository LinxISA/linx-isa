#!/usr/bin/env python3
"""Run repository-local documentation integrity checks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


TEXT_SUFFIXES = {".adoc", ".json", ".md", ".py", ".sh", ".yaml", ".yml"}
RETIRED_MNEMONICS = (
    "B" + ".IOD",
    "BSTART" + ".PAR",
    "C" + ".B.IOS",
    "B" + ".ATTR",
    "B" + ".IOTI",
)
RETIRED_SOURCE_POLICY = "linx-v03-" + "parity"
RETIRED_PAGE_SLUGS = (
    "b_" + "iod",
    "bstart_" + "par",
    "c_b_" + "ios",
    "b_" + "attr",
    "b_" + "ioti",
)
CURRENT_RETIREMENT_NOTICES = {Path("docs/releases/v0.57.0.md")}


def _error(errors: list[str], message: str) -> None:
    errors.append(message)
    print(f"error: {message}", file=sys.stderr)


def _is_archive(path: Path) -> bool:
    return "archive" in path.parts


def _archive_is_marked(root: Path, path: Path) -> bool:
    current = path.parent
    while current != root and root in current.parents:
        marker = current / "README.md"
        if marker.is_file():
            text = marker.read_text(encoding="utf-8", errors="replace")
            if "Archive status:" in text or "归档状态：" in text:
                return True
        current = current.parent
    return False


def _check_retired_surfaces(root: Path, errors: list[str]) -> None:
    scan_roots = (root / "docs", root / "tools" / "bringup")
    extra_files = (root / "mkdocs.yml", root / "mkdocs.zh.yml")
    candidates = [
        path
        for scan_root in scan_roots
        for path in scan_root.rglob("*")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
    ]
    candidates.extend(path for path in extra_files if path.is_file())

    for path in candidates:
        rel = path.relative_to(root)
        if rel == Path("docs/check_documentation.py"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = [token for token in (*RETIRED_MNEMONICS, RETIRED_SOURCE_POLICY) if token in text]
        if rel in {Path("mkdocs.yml"), Path("mkdocs.zh.yml"), Path("docs/zh/assets/lang-map.json")}:
            hits.extend(slug for slug in RETIRED_PAGE_SLUGS if slug in text.lower())
        if not hits:
            continue
        if _is_archive(rel):
            if not _archive_is_marked(root, path):
                _error(errors, f"unmarked archive contains retired ISA text: {rel}")
            continue
        if (
            rel in CURRENT_RETIREMENT_NOTICES
            and RETIRED_SOURCE_POLICY not in hits
            and "retired and rejected" in text
        ):
            continue
        _error(errors, f"active surface contains retired token(s) {', '.join(hits)}: {rel}")

    obsolete_pages = (
        root / "docs/isa/header" / ("B" + ".IOD.md"),
        root / "docs/isa/header" / ("B" + ".ATTR.md"),
        root / "docs/isa/instructions/b_iod.md",
        root / "docs/isa/instructions/b_ioti.md",
        root / "docs/isa/instructions/bstart_par.md",
        root / "docs/zh/isa/header" / ("B" + ".IOD.md"),
        root / "docs/zh/isa/header" / ("B" + ".ATTR.md"),
        root / "docs/zh/isa/header" / ("BSTART" + ".PAR.md"),
        root / "docs/zh/isa/instructions/b_iod.md",
        root / "docs/zh/isa/instructions/b_ioti.md",
        root / "docs/zh/isa/instructions/bstart_par.md",
    )
    for path in obsolete_pages:
        if path.exists():
            _error(errors, f"obsolete active instruction page exists: {path.relative_to(root)}")

    duplicate_uops = root / "docs/bringup/golden/uop_classification_v0.57"
    if duplicate_uops.exists():
        _error(errors, "duplicate documentation uop mirror exists; use isa/v0.57/uop_classification_v0.57")

    for rel in (Path("docs/bringup/gates/qemu_isa_coverage_latest.json"),):
        path = root / rel
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            _error(errors, f"invalid QEMU coverage report {rel}: {exc}")
            continue
        rendered = json.dumps(report, sort_keys=True)
        for mnemonic in RETIRED_MNEMONICS:
            if mnemonic in rendered:
                _error(errors, f"stale QEMU coverage report contains retired mnemonic {mnemonic}: {rel}")


def _check_generated_image_links(root: Path, errors: list[str]) -> None:
    """Require every generated local SVG reference to resolve exactly."""
    generated_sources = [
        root / "docs/isa/encoding.md",
        *(root / "docs/isa/instructions").glob("*.md"),
        root / "docs/architecture/isa-manual/src/generated/instruction_details.adoc",
        *(root / "docs/architecture/isa-manual/src/generated/instructions").glob("*.adoc"),
    ]
    patterns = (
        re.compile(r'<img\s+[^>]*src="([^"]+\.svg)"'),
        re.compile(r"!?\[[^\]]*\]\(([^)]+\.svg)\)"),
        re.compile(r"image::([^\[]+\.svg)\["),
    )
    for source in generated_sources:
        if not source.is_file():
            _error(errors, f"missing generated documentation source: {source.relative_to(root)}")
            continue
        text = source.read_text(encoding="utf-8", errors="replace")
        for pattern in patterns:
            for match in pattern.finditer(text):
                target_text = match.group(1)
                if "://" in target_text or target_text.startswith("/"):
                    continue
                targets = [(source.parent / target_text).resolve()]
                # AsciiDoc instruction fragments are included from the
                # generated manual root, so image:: paths are resolved against
                # that include context rather than the fragment directory.
                if source.parent.name == "instructions":
                    targets.append((source.parent.parent / target_text).resolve())
                if not any(target.is_file() for target in targets):
                    _error(
                        errors,
                        f"broken generated SVG link in {source.relative_to(root)}: {target_text}",
                    )


def _check_asciidoc_includes(root: Path, errors: list[str]) -> None:
    """Require every local AsciiDoc include target to exist."""
    manual_src = root / "docs" / "architecture" / "isa-manual" / "src"
    include_pattern = re.compile(r"^include::([^\[]+)\[", re.MULTILINE)
    for source in manual_src.rglob("*.adoc"):
        text = source.read_text(encoding="utf-8", errors="replace")
        for match in include_pattern.finditer(text):
            target_text = match.group(1)
            if "://" in target_text or target_text.startswith("/") or "{" in target_text:
                continue
            target = (source.parent / target_text).resolve()
            if not target.is_file():
                _error(
                    errors,
                    f"broken AsciiDoc include in {source.relative_to(root)}: {target_text}",
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="superproject root")
    parser.add_argument(
        "--skip-generated",
        action="store_true",
        help="skip generated ISA page drift checking",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    docs = root / "docs"
    errors: list[str] = []

    _check_retired_surfaces(root, errors)
    _check_generated_image_links(root, errors)
    _check_asciidoc_includes(root, errors)

    placeholders = [
        path.relative_to(root)
        for path in (docs / "zh").rglob("*")
        if path.is_file()
        and path.name != "translation-manifest.json"
        and "ZXTERMEN" in path.read_text(encoding="utf-8", errors="replace")
    ]
    for path in placeholders:
        _error(errors, f"unresolved translation placeholder: {path}")

    tracked = subprocess.run(
        ["git", "ls-files", "-z", "docs"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    for raw in tracked:
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="replace")
        if "#" in rel and (root / rel).exists():
            _error(errors, f"tracked documentation filename contains '#': {rel}")

    manifest_path = docs / "zh" / "translation-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _error(errors, f"invalid Chinese translation manifest: {exc}")
    else:
        if manifest.get("normative_language") != "en":
            _error(errors, "translation manifest must declare English as normative")
        if manifest.get("canonical_isa") != "isa/v0.58/linxisa-v0.58.json":
            _error(errors, "translation manifest points at a non-canonical ISA source")
        pages = manifest.get("pages")
        if not isinstance(pages, dict) or not pages:
            _error(errors, "translation manifest lacks per-page source hashes")
        else:
            result = subprocess.run(
                [sys.executable, "tools/docs/update_translation_manifest.py", "--check"],
                cwd=root,
                check=False,
            )
            if result.returncode:
                _error(errors, "Chinese translation source/translation hashes are stale")

    encoding = (docs / "isa" / "encoding.md").read_text(encoding="utf-8")
    required_encoding_text = (
        "only as a non-normative review aid",
        "It is not a generator input",
    )
    for token in required_encoding_text:
        if token not in encoding:
            _error(errors, f"encoding workbook policy is missing: {token}")

    for rel in (
        "docs/isa/instructions/bstart_call.md",
        "docs/isa/instructions/hl_bstart_call.md",
    ):
        text = (root / rel).read_text(encoding="utf-8")
        for token in ("preserves `ra`", "adjacent `SETRET` or `C.SETRET`"):
            if token not in text:
                _error(errors, f"{rel} is missing the call/return contract token: {token}")

    with tempfile.TemporaryDirectory(prefix="linxisa-gate-status-") as temp_dir:
        rendered_status = Path(temp_dir) / "GATE_STATUS.md"
        result = subprocess.run(
            [
                sys.executable,
                "tools/bringup/gate_report.py",
                "render",
                "--report",
                "docs/bringup/gates/latest.json",
                "--out-md",
                str(rendered_status),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            _error(errors, "failed to render docs/bringup/gates/latest.json")
        elif rendered_status.read_bytes() != (docs / "bringup" / "GATE_STATUS.md").read_bytes():
            _error(errors, "GATE_STATUS.md does not match the authoritative latest.json")

    if not args.skip_generated:
        generated_checks = (
            (
                [
                    sys.executable,
                    "tools/isa/gen_encoding_svg.py",
                    "--out-dir",
                    "docs/isa/wavedrom",
                    "--check",
                ],
                "MkDocs encoding SVGs",
            ),
            (
                [
                    sys.executable,
                    "tools/isa/gen_encoding_svg.py",
                    "--out-dir",
                    "docs/architecture/isa-manual/src/generated/encodings",
                    "--check",
                ],
                "AsciiDoc encoding SVGs",
            ),
            ([sys.executable, "docs/isa/gen_isa_pages.py", "--check"], "generated ISA pages"),
            ([sys.executable, "tools/isa/gen_manual_adoc.py", "--check"], "generated manual tables"),
            (
                [sys.executable, "tools/isa/gen_instruction_fragments.py", "--check"],
                "generated instruction fragments",
            ),
        )
        for command, label in generated_checks:
            result = subprocess.run(command, cwd=root, check=False)
            if result.returncode:
                _error(errors, f"{label} are out of date")

    if errors:
        return 1
    print("ok: documentation integrity checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
