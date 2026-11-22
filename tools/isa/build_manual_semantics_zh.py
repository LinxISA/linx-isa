#!/usr/bin/env python3
"""Archive the pinned PTO detailed Chinese reader blocks by common form ID."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

try:
    from manual_reader import _plain_markdown
except ModuleNotFoundError:
    from tools.isa.manual_reader import _plain_markdown

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
READER = ROOT / "docs/architecture/isa-manual/reference/data/manual-reader-zh.json"
OUTPUT = ROOT / "docs/architecture/isa-manual/reference/data/manual-semantics-zh.json"
MARKER = re.compile(r"<!-- PTO-READER-BLOCK: [^>]+ role=([^ ]+) -->")
ROLES = ("purpose", "mechanism", "inputs-outputs", "effects", "constraints", "example")


def _clean_statement(value: str) -> str:
    # Some generated reader pages repeat the English catalog summary after a
    # complete Chinese statement. It is provenance filler, not an extra fact.
    value = re.sub(r"\s*其记录的摘要为：[^\u4e00-\u9fff]*", "", value)
    value = re.sub(r"[（(]asl/[^)）]+[)）]", "", value)
    value = re.sub(r"asl/[A-Za-z0-9_./-]+:\d+", "规范执行路径", value)
    value = re.sub(r"(?:^|\s+)设计要点：.*?。", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True)


def _section(markdown: str, role: str) -> dict[str, object]:
    match = next((m for m in MARKER.finditer(markdown) if m.group(1) == role), None)
    if match is None:
        raise ValueError(f"missing Chinese reader role={role}")
    tail = markdown[match.end() :]
    end = MARKER.search(tail)
    if end:
        tail = tail[: end.start()]
    supplement_end = tail.find("<!-- SUPPLEMENTARY-END -->")
    if supplement_end >= 0:
        tail = tail[:supplement_end]
    lines = tail.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines or not lines[0].startswith("## "):
        raise ValueError(f"reader role={role} has no heading")
    heading = _plain_markdown(lines.pop(0)[3:])
    statements: list[str] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            value = _clean_statement(_plain_markdown(" ".join(paragraph)))
            if value:
                statements.append(value)
            paragraph.clear()

    in_fence = False
    fence: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence:
                value = "\n".join(fence).strip()
                if value:
                    statements.append(value)
                fence.clear()
            else:
                flush()
            in_fence = not in_fence
            continue
        if in_fence:
            fence.append(line.rstrip())
        elif not stripped:
            flush()
        elif stripped.startswith(("- ", "* ")):
            flush()
            value = _clean_statement(_plain_markdown(stripped[2:]))
            if value:
                statements.append(value)
        elif stripped.startswith("<!--"):
            flush()
        else:
            paragraph.append(stripped)
    flush()
    if not heading or not statements:
        raise ValueError(f"empty Chinese reader role={role}")
    return {"heading": heading, "statements": statements}


def build(pto_root: Path) -> dict[str, object]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    commit = str(lock["source"]["commit"])
    if _git(pto_root, "rev-parse", "HEAD").strip() != commit:
        raise ValueError("PTO checkout is not the pinned 0.59.1 source commit")
    records = json.loads(READER.read_text(encoding="utf-8"))["records"]
    forms: dict[str, object] = {}
    for source_path, record in records.items():
        identities = [
            value for value in record["identities"] if not value.startswith("tile:")
        ]
        if not identities:
            continue
        reader_path = str(record["reader_path"])
        markdown = _git(pto_root, "show", f"{commit}:{reader_path}")
        roles = {role: _section(markdown, role) for role in ROLES}
        value = {
            "mnemonic": record["mnemonic"],
            "source_path": source_path,
            "reader_path": reader_path,
            "source_commit": commit,
            "roles": roles,
        }
        for form_id in identities:
            forms[form_id] = value
    return {
        "schema": "linxisa.manual.semantics-zh.v1",
        "source_commit": commit,
        "forms": dict(sorted(forms.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pto-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = (
        json.dumps(
            build(args.pto_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n"
    )
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale Chinese semantic data: {OUTPUT}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Chinese semantics: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
