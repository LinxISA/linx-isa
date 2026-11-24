#!/usr/bin/env python3
"""Build and render exact Sail evidence for retained Linx-only forms."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
from html import escape
import json
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

from export_linxisa_v0591_sail import check as check_export
from export_linxisa_v0591_sail import export as export_sail

from manual_tag import (
    RELEASE_TAG,
    REPO_ROOT,
    tagged_bytes,
    tagged_json,
)


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs/architecture/isa-manual/reference/data/manual-linx-sail.json"
CATALOG_PATH = "isa/v0.59/linxisa-v0.59.json"
DECODE_PACKAGE_PATH = "model/decode/decode.sail"
GENERATOR_PATH = "tools/isa/gen_sail_decode.py"


def _render(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _line_block(lines: list[str], anchor: int) -> tuple[int, int, str]:
    """Extract the exact enclosing `then { ... }` branch for a catalog comment."""
    start = anchor
    while start >= 0 and "then {" not in lines[start]:
        start -= 1
    if start < 0:
        raise ValueError(f"decode comment at line {anchor + 1} has no branch")
    depth = 0
    opened = False
    for end in range(start, len(lines)):
        depth += lines[end].count("{") - lines[end].count("}")
        opened = opened or "{" in lines[end]
        if opened and depth == 0:
            return start + 1, end + 1, "".join(lines[start : end + 1])
    raise ValueError(f"decode branch at line {start + 1} is unterminated")


def _function_block(source: bytes, name: str) -> tuple[int, int, str]:
    text = source.decode("utf-8")
    lines = text.splitlines(keepends=True)
    definition = re.compile(rf"^function\s+{re.escape(name)}\s*\(")
    starts = [index for index, line in enumerate(lines) if definition.search(line)]
    if len(starts) != 1:
        raise ValueError(
            f"expected one Sail definition for {name}, found {len(starts)}"
        )
    start = starts[0]
    depth = 0
    for end in range(start, len(lines)):
        depth += lines[end].count("{") - lines[end].count("}")
        if end >= start and depth == 0:
            return start + 1, end + 1, "".join(lines[start : end + 1])
    raise ValueError(f"Sail helper {name} is unterminated")


@lru_cache(maxsize=1)
def _exported_sail_sources() -> dict[str, bytes]:
    """Capture the hardened v0.59.1 export independently of the v0.58 model."""
    with tempfile.TemporaryDirectory(prefix="linx-v0591-manual-export-") as directory:
        root = Path(directory) / "sail"
        export_sail(root)
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted((root / "model").rglob("*.sail"))
        }


def _sail_sources() -> dict[str, bytes]:
    return _exported_sail_sources()


def _release_decode() -> bytes:
    """Return the decoder from the hardened v0.59.1 Sail export."""
    return _exported_sail_sources()[DECODE_PACKAGE_PATH]


def _handler_index(names: set[str]) -> dict[str, dict[str, Any]]:
    sources = _sail_sources()
    handlers: dict[str, dict[str, Any]] = {}
    for name in sorted(names):
        matches = [
            path
            for path, source in sources.items()
            if re.search(
                rf"(?m)^function\s+{re.escape(name)}\s*\(", source.decode("utf-8")
            )
        ]
        if len(matches) != 1:
            raise ValueError(f"Sail helper owner for {name} is ambiguous: {matches}")
        path = matches[0]
        start, end, excerpt = _function_block(sources[path], name)
        handlers[name] = {
            "path": path,
            "line_start": start,
            "line_end": end,
            "excerpt": excerpt,
            "excerpt_sha256": _sha(excerpt.encode("utf-8")),
            "file_sha256": _sha(sources[path]),
        }
    return handlers


def build() -> dict[str, Any]:
    catalog = tagged_json(CATALOG_PATH)
    decode = _release_decode()
    lines = decode.decode("utf-8").splitlines(keepends=True)
    forms: dict[str, dict[str, Any]] = {}
    helper_names: set[str] = set()
    for row in catalog["instructions"]:
        if row.get("pto_source_form_id"):
            continue
        exact_marker = f"// {row['mnemonic']} | {row['asm']} | {row['source']!r}"
        unsupported_marker = (
            f"// {row['mnemonic']} | {row['asm']} | unsupported executable subset"
        )
        exact_hits = [
            index for index, line in enumerate(lines) if line.strip() == exact_marker
        ]
        fallback_hits = [
            index
            for index, line in enumerate(lines)
            if line.strip() == unsupported_marker
        ]
        hits = exact_hits or fallback_hits
        if len(hits) != 1:
            raise ValueError(
                f"{row['id']}: expected one exact normalized decode branch, found {len(hits)}"
            )
        start, end, excerpt = _line_block(lines, hits[0])
        helpers = sorted(set(re.findall(r"\b(exec_[a-z0-9_]+)\s*\(", excerpt)))
        helper_names.update(helpers)
        traps = "trap_illegal_inst" in excerpt
        if helpers:
            disposition = "calls-sail-helper"
        elif traps:
            disposition = "traps-in-sail-executable-subset"
        else:
            disposition = "platform-dispatch-required"
        forms[str(row["id"])] = {
            "mnemonic": row["mnemonic"],
            "asm": row["asm"],
            "catalog_source": row["source"],
            "catalog_note": row.get("note", ""),
            "encoding": row["encoding"],
            "decode": {
                "package_path": DECODE_PACKAGE_PATH,
                "generator_path": GENERATOR_PATH,
                "line_start": start,
                "line_end": end,
                "excerpt": excerpt,
                "excerpt_sha256": _sha(excerpt.encode("utf-8")),
                "catalog_comment_kind": (
                    "exact-source-row" if exact_hits else "unsupported-subset-row"
                ),
            },
            "disposition": disposition,
            "helpers": helpers,
        }
    if len(forms) != 23:
        raise ValueError(f"expected 23 retained Linx-only forms, found {len(forms)}")
    handlers = _handler_index(helper_names)
    return {
        "schema": "linxisa.manual.linx-only-sail.v1",
        "release_tag": RELEASE_TAG,
        "source_identity": "hardened-v0.59.1-sail-export",
        "catalog": {
            "path": CATALOG_PATH,
            "sha256": _sha(tagged_bytes(CATALOG_PATH)),
        },
        "decoder": {
            "package_path": DECODE_PACKAGE_PATH,
            "sha256": _sha(decode),
            "generator_path": GENERATOR_PATH,
            "generator_sha256": _sha(tagged_bytes(GENERATOR_PATH)),
        },
        "coverage": {
            "linx_only_forms": len(forms),
            "helper_forms": sum(
                row["disposition"] == "calls-sail-helper" for row in forms.values()
            ),
            "trap_forms": sum(
                row["disposition"] == "traps-in-sail-executable-subset"
                for row in forms.values()
            ),
            "platform_dispatch_forms": sum(
                row["disposition"] == "platform-dispatch-required"
                for row in forms.values()
            ),
            "unique_helpers": len(handlers),
        },
        "forms": dict(sorted(forms.items())),
        "handlers": handlers,
    }


@lru_cache(maxsize=1)
def _offline() -> dict[str, Any]:
    return json.loads(DATA.read_text(encoding="utf-8"))


def _source_matches(row: Mapping[str, Any], evidence: Mapping[str, Any]) -> bool:
    return (
        str(row.get("mnemonic")) == evidence.get("mnemonic")
        and str(row.get("asm")) == evidence.get("asm")
        and str(row.get("note", "")) == evidence.get("catalog_note", "")
        and row.get("source") == evidence.get("catalog_source")
        and row.get("encoding") == evidence.get("encoding")
    )


def _source_block(title: str, record: Mapping[str, Any], css_class: str) -> str:
    start, end = int(record["line_start"]), int(record["line_end"])
    path = record.get("path") or record.get("package_path")
    source = (
        f"0.59.1 Sail 导出包 <code>{escape(str(path))}</code> "
        f"第 {start}–{end} 行"
    )
    return (
        f'<div class="{css_class}"><h4>{escape(title)}</h4>'
        f"<p>{source}</p>"
        f"<pre><code>{escape(str(record['excerpt']))}</code></pre></div>"
    )


def sail_detail(row: Mapping[str, Any]) -> str:
    """Render exact tagged Sail evidence for one retained Linx-only row."""
    form_id = str(row.get("id", ""))
    evidence = _offline().get("forms", {}).get(form_id)
    if not isinstance(evidence, dict) or not _source_matches(row, evidence):
        return ""
    disposition = str(evidence["disposition"])
    body = [_source_block("译码分支", evidence["decode"], "linx-sail-decode")]
    if disposition == "calls-sail-helper":
        for helper in evidence["helpers"]:
            handler = _offline()["handlers"].get(helper)
            if not isinstance(handler, dict):
                return ""
            body.append(
                _source_block(f"执行函数 · {helper}", handler, "linx-sail-handler")
            )
    elif disposition == "traps-in-sail-executable-subset":
        body.append(
            '<p class="linx-sail-result">官方 Sail 可执行子集在该译码分支调用 '
            "<code>trap_illegal_inst</code>，与 catalog 的 encoding-only 契约一致。"
            "LinxISA 0.59.1 不读取这些形式的操作数，不执行数据移动，也不产生架构结果或副作用。</p>"
        )
    else:
        body.append(
            '<p class="linx-sail-result">该分支未调用已收录的规范执行函数；'
            "结果需由平台实现/译码路径提供。</p>"
        )
    return (
        '<details class="linx-sail-evidence" data-disposition="'
        f'{escape(disposition, quote=True)}"><summary>发布版 Sail 模型 · '
        f"{escape(str(evidence['mnemonic']))}</summary>{''.join(body)}</details>"
    )


def _resolve_export(path: Path) -> Path:
    if path.is_file():
        path = Path(path.read_text(encoding="utf-8").strip())
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--official-export", type=Path)
    args = parser.parse_args()
    expected = _render(build())
    if args.official_export is not None:
        export = _resolve_export(args.official_export)
        check_export(export)
        exported_decode = export / DECODE_PACKAGE_PATH
        if exported_decode.read_bytes() != _release_decode():
            raise SystemExit(
                "official Sail export decoder differs from reproduced 0.59 decoder"
            )
    if args.check:
        if DATA.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale Linx-only Sail evidence: {DATA}")
        print("Linx-only Sail evidence is current: 23 forms")
        return 0
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(expected, encoding="utf-8")
    print(f"wrote {DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["sail_detail"]
