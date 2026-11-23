#!/usr/bin/env python3
"""Build and read source-verified Chinese PTO reader summaries."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
from html import escape, unescape
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
SCALARS = ROOT / "isa/v0.59/state/pto_scalar_forms.json"
COMMANDS = ROOT / "isa/v0.59/state/pto_command_forms.json"
TILES = ROOT / "isa/v0.59/state/pto_tile_operations.json"
DATA = ROOT / "docs/architecture/isa-manual/reference/data/manual-reader-zh.json"
LICENSE_ASSET = (
    ROOT / "docs/architecture/isa-manual/reference/data/PTO-SPEC-LICENSE.txt"
)
ZH_ROOT = "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current"
PURPOSE = re.compile(r"<!-- PTO-READER-BLOCK: [^>]+ role=purpose -->")
GENERATED = re.compile(r"<!-- GENERATED FROM: ([^>]+) -->\s*\n# ([^\n]+)")
OPERATION_BEGIN = b"// DOC-BEGIN: operation"
OPERATION_END = b"// DOC-END: operation"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def _render(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _git(repo: Path, *args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=text,
        check=False,
    )
    if result.returncode:
        error = result.stderr if text else result.stderr.decode("utf-8", "replace")
        raise ValueError(error.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def _plain_markdown(value: str) -> str:
    """Reduce one trusted Markdown paragraph to compact plain text."""
    code_spans: list[str] = []

    def protect_code(match: re.Match[str]) -> str:
        code_spans.append(match.group(1))
        return f"\ue000{len(code_spans) - 1}\ue001"

    text = re.sub(r"`([^`\n]*)`", protect_code, value)
    text = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[\^[^]]+\]", "", text)
    # Preserve architectural placeholders such as <dst>, register operands
    # such as [SrcL], and identifier underscores. Only remove known HTML tags.
    text = re.sub(
        r"</?(?:em|strong|code|br|span|p|sub|sup)(?:\s+[^>]*)?\s*/?>",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_\n]+)__", r"\1", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"\1", text)
    text = re.sub(r"~~([^~\n]+)~~", r"\1", text)
    text = text.replace("\\*", "*").replace("\\_", "_")
    for index, code in enumerate(code_spans):
        text = text.replace(f"\ue000{index}\ue001", code)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _purpose(markdown: str) -> tuple[str, str]:
    marker = PURPOSE.search(markdown)
    if marker is None:
        raise ValueError("reader page has no exact role=purpose block")
    lines = markdown[marker.end() :].splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines or not lines[0].startswith("## "):
        raise ValueError("purpose block has no level-two heading")
    heading = _plain_markdown(lines.pop(0)[3:])
    while lines and not lines[0].strip():
        lines.pop(0)
    paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            break
        if stripped.startswith(("#", "- ", "* ", ">", "```", "<!--")):
            break
        paragraph.append(stripped)
    plain = _plain_markdown(" ".join(paragraph))
    if not heading or not plain:
        raise ValueError("purpose block has no trustworthy first paragraph")
    return heading, plain


def _operation_blocks(source: bytes) -> list[dict[str, Any]]:
    """Return exact marked source blocks with one-based inclusive line ranges."""
    lines = source.splitlines(keepends=True)
    blocks: list[dict[str, Any]] = []
    begin: int | None = None
    for index, line in enumerate(lines):
        marker = line.rstrip(b"\r\n").strip()
        if marker == OPERATION_BEGIN:
            if begin is not None:
                raise ValueError("nested DOC-BEGIN: operation markers")
            begin = index
        elif marker == OPERATION_END:
            if begin is None:
                raise ValueError("DOC-END: operation without begin marker")
            block = b"".join(lines[begin : index + 1])
            blocks.append(
                {
                    "line_start": begin + 1,
                    "line_end": index + 1,
                    "sha256": hashlib.sha256(block).hexdigest(),
                    "text": block.decode("utf-8"),
                }
            )
            begin = None
    if begin is not None:
        raise ValueError("DOC-BEGIN: operation without end marker")
    return blocks


def _expected_rows() -> tuple[dict[str, list[dict[str, str]]], int, int]:
    expected: dict[str, list[dict[str, str]]] = {}
    common_count = 0
    for owner, path in (("scalar", SCALARS), ("command", COMMANDS)):
        rows = _load(path)["forms"]
        common_count += len(rows)
        for row in rows:
            expected.setdefault(str(row["mnemonic"]), []).append(
                {"owner": owner, "identity": str(row["form_id"])}
            )
    tile_rows = _load(TILES)["operations"]
    for row in tile_rows:
        expected.setdefault(str(row["name"]), []).append(
            {
                "owner": "tile",
                "identity": (
                    f"tile:{row['engine']}:{row.get('mode', '-')}:"
                    f"{row['function']}:{row['name']}"
                ),
            }
        )
    return expected, common_count, len(tile_rows)


def build(pto_root: Path) -> tuple[dict[str, Any], str]:
    lock = _load(LOCK)
    commit = str(lock["source"]["commit"])
    expected_tree = str(lock["source"]["tree"])
    actual_tree = str(_git(pto_root, "rev-parse", f"{commit}^{{tree}}")).strip()
    if actual_tree != expected_tree:
        raise ValueError(
            f"pinned PTO tree differs: expected {expected_tree}, got {actual_tree}"
        )

    archive = _git(pto_root, "archive", commit, ZH_ROOT, text=False)
    pages: dict[str, dict[str, str]] = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        for member in bundle:
            if not member.isfile() or not member.name.endswith(".md"):
                continue
            extracted = bundle.extractfile(member)
            if extracted is None:
                continue
            markdown = extracted.read().decode("utf-8")
            identity = GENERATED.search(markdown)
            if identity is None or PURPOSE.search(markdown) is None:
                continue
            asl_path = identity.group(1).strip()
            mnemonic = identity.group(2).strip()
            if (
                PurePosixPath(asl_path).is_absolute()
                or ".." in PurePosixPath(asl_path).parts
            ):
                raise ValueError(f"unsafe ASL path in {member.name}: {asl_path}")
            if asl_path in pages:
                raise ValueError(f"ambiguous Chinese reader pages for {asl_path}")
            heading, paragraph = _purpose(markdown)
            pages[asl_path] = {
                "mnemonic": mnemonic,
                "reader_path": member.name,
                "heading": heading,
                "paragraph": paragraph,
            }

    expected, common_count, tile_count = _expected_rows()
    by_mnemonic: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for asl_path, page in pages.items():
        by_mnemonic.setdefault(page["mnemonic"], []).append((asl_path, page))

    records: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for mnemonic, identities in expected.items():
        matches = by_mnemonic.get(mnemonic, [])
        if len(matches) != 1:
            missing.append(mnemonic)
            continue
        asl_path, page = matches[0]
        # Prove the normative owner exists at the same pinned commit.
        _git(pto_root, "cat-file", "-e", f"{commit}:{asl_path}")
        asl_source = bytes(_git(pto_root, "show", f"{commit}:{asl_path}", text=False))
        operation_blocks = _operation_blocks(asl_source)
        records[asl_path] = {
            "mnemonic": mnemonic,
            "owners": sorted({item["owner"] for item in identities}),
            "identities": sorted(item["identity"] for item in identities),
            "reader_path": page["reader_path"],
            "purpose_heading": page["heading"],
            "purpose_text": page["paragraph"],
            "purpose_sha256": hashlib.sha256(
                page["paragraph"].encode("utf-8")
            ).hexdigest(),
            "normative_asl_url": (
                f"https://github.com/PTO-ISA/pto-spec/blob/{commit}/{asl_path}"
            ),
            "reader_source_url": (
                "https://github.com/PTO-ISA/pto-spec/blob/"
                f"{commit}/{page['reader_path']}"
            ),
            "asl_file_sha256": hashlib.sha256(asl_source).hexdigest(),
            "operation_kind": (
                "doc-operation-blocks" if operation_blocks else "source-link-fallback"
            ),
            "operation_blocks": operation_blocks,
            "operation_note": (
                "该 ASL 文件没有 DOC-BEGIN/END: operation 标记；请查看固定版本的完整规范源文件。"
                if not operation_blocks
                else ""
            ),
        }
    if missing:
        raise ValueError(f"missing or ambiguous Chinese reader pages: {missing[:10]}")

    license_text = str(_git(pto_root, "show", f"{commit}:LICENSE"))
    if not license_text.endswith("\n"):
        license_text += "\n"
    data = {
        "schema": "linxisa.manual-reader-zh.v1",
        "language": "zh-CN",
        "source": {
            "repository": lock["source"]["repository"],
            "commit": commit,
            "tree": expected_tree,
            "pto_release": lock["release"],
            "publication": lock["publication"],
        },
        "coverage": {
            "common_forms": common_count,
            "tile_operations": tile_count,
            "unique_reader_pages": len(records),
        },
        "content_policy": {
            "purpose_text_role": "non-normative-explanation",
            "normative_owner": "pinned-asl-path",
            "markdown_links": "stripped-from-offline-plain-text",
        },
        "license": {
            "asset": LICENSE_ASSET.name,
            "upstream_path": "LICENSE",
            "sha256": hashlib.sha256(license_text.encode("utf-8")).hexdigest(),
            "notice": license_text,
        },
        "records": records,
    }
    return data, license_text


@lru_cache(maxsize=1)
def _offline() -> dict[str, Any]:
    return _load(DATA)


def _record(asl_path: str) -> dict[str, Any] | None:
    if not isinstance(asl_path, str):
        return None
    path = PurePosixPath(asl_path)
    if path.is_absolute() or ".." in path.parts:
        return None
    value = _offline().get("records", {}).get(path.as_posix())
    return value if isinstance(value, dict) else None


def reader_summary(asl_path: str) -> str:
    """Return source-verified Chinese purpose prose, or empty for no exact match."""
    record = _record(asl_path)
    return str(record["purpose_text"]) if record else ""


def reader_detail(asl_path: str) -> str:
    """Render an explanatory reader block that keeps normative ASL explicit."""
    record = _record(asl_path)
    if record is None:
        return ""
    return (
        '<section class="reader-detail" data-content-role="non-normative-explanation">'
        f"<p>{escape(str(record['purpose_text']))}</p>"
        f'<a class="reader-detail-authority" href="{escape(str(record["reader_source_url"]), quote=True)}" '
        'rel="noopener noreferrer">中文导读 · 解释性说明</a></section>'
    )


def operation_detail(asl_path: str) -> str:
    """Render exact normative ASL operation blocks, or a pinned source fallback."""
    record = _record(asl_path)
    if record is None:
        return ""
    blocks = record.get("operation_blocks", [])
    url = str(record["normative_asl_url"])
    mnemonic = escape(str(record["mnemonic"]))
    if not blocks:
        note = escape(str(record.get("operation_note", "请查看固定版本的规范源文件。")))
        return (
            '<details class="asl-operation" data-content-role="normative-asl">'
            f"<summary>规范 ASL · {mnemonic}</summary><p>{note} "
            f'<a href="{escape(url, quote=True)}" rel="noopener noreferrer">'
            "查看固定版本的完整 ASL</a></p></details>"
        )
    rendered: list[str] = []
    for index, block in enumerate(blocks, start=1):
        line_start = int(block["line_start"])
        line_end = int(block["line_end"])
        label = f"第 {index} 段 · " if len(blocks) > 1 else ""
        source_url = f"{url}#L{line_start}-L{line_end}"
        rendered.append(
            f'<div class="asl-operation-block"><p>{label}'
            f'<a href="{escape(source_url, quote=True)}" rel="noopener noreferrer">'
            f"规范源文件第 {line_start}–{line_end} 行</a></p>"
            f"<pre><code>{escape(str(block['text']))}</code></pre></div>"
        )
    return (
        '<details class="asl-operation" data-content-role="normative-asl">'
        f"<summary>规范 ASL · {mnemonic}</summary>{''.join(rendered)}</details>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pto-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data, license_text = build(args.pto_root.resolve())
    expected_data = _render(data)
    if args.check:
        if DATA.read_text(encoding="utf-8") != expected_data:
            raise SystemExit(f"stale Chinese reader data: {DATA}")
        if LICENSE_ASSET.read_text(encoding="utf-8") != license_text:
            raise SystemExit(f"stale PTO license asset: {LICENSE_ASSET}")
        print(
            "Chinese reader data is current: "
            f"{data['coverage']['common_forms']} common forms, "
            f"{data['coverage']['tile_operations']} Tile operations"
        )
        return 0
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(expected_data, encoding="utf-8")
    LICENSE_ASSET.write_text(license_text, encoding="utf-8")
    print(f"wrote {DATA}")
    print(f"wrote {LICENSE_ASSET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["operation_detail", "reader_detail", "reader_summary"]
