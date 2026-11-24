"""Reader-facing provenance for the LinxISA v0.59.2 active-form manual."""

from __future__ import annotations

from hashlib import sha256
from html import escape
from pathlib import Path
from typing import Mapping
import json


RELEASE_TAG = "v0.59.2"
RELEASE_VERSION = "0.59.2"
ACTIVE_FORM_COUNT = 1306
ACTIVE_MNEMONIC_COUNT = 561
OBSOLETE_FORM_COUNT = 193
TILE_OPERATION_COUNT = 119


def _link(href: str, label: str) -> str:
    return f'<a href="{escape(href, quote=True)}">{escape(label)}</a>'


def sources_v0592(
    commit: str,
    inputs: Mapping[str, bytes],
    manifest: Mapping[str, object],
    lock: Mapping[str, object],
) -> str:
    """Render the v0.59.2 source page without publishing obsolete catalog rows."""
    if manifest.get("version") != RELEASE_VERSION:
        raise ValueError("v0.59.2 source page requires the v0.59.2 release manifest")
    cardinality = manifest.get("cardinality", {})
    if not isinstance(cardinality, Mapping) or (
        cardinality.get("instructions") != 1499
        or cardinality.get("linx_only_obsolete_forms") != OBSOLETE_FORM_COUNT
        or cardinality.get("linx_only_reserved-unimplemented_forms") != 4
    ):
        raise ValueError("v0.59.2 release cardinality differs")
    source = lock.get("source", {})
    identity = manifest.get("identity", {})
    if not isinstance(source, Mapping) or not isinstance(identity, Mapping):
        raise ValueError("v0.59.2 PTO provenance is incomplete")
    forbidden = [
        path
        for path in inputs
        if Path(path).name in {"linxisa-v0.59.json", "linxisa-v0.59.2.json"}
    ]
    if forbidden:
        raise ValueError(
            "the active-form manual must not package a catalog containing obsolete rows"
        )

    repo = f"https://github.com/LinxISA/linx-isa/blob/{commit}/"
    facts = (
        ("LinxISA 标签", RELEASE_TAG),
        ("规范提交", commit),
        (
            "手册收录",
            f"{ACTIVE_FORM_COUNT} 个有效或预留形式，{ACTIVE_MNEMONIC_COUNT} 个目录助记符",
        ),
        ("Tile 操作", f"{TILE_OPERATION_COUNT} 个；VEC、SFU、TLSU、CUBE 均保留"),
        ("PTO 标签", str(lock["publication"]["tag"])),
        ("PTO 源提交", str(source["commit"])),
        ("ELF 编码 ABI", str(identity["encoding_abi"])),
        ("ELF 编码投影 SHA-256", str(identity["encoding_projection_sha256"])),
    )
    body = (
        '<dl class="contract-grid">'
        + "".join(
            f"<dt>{escape(name)}</dt><dd><code>{escape(value)}</code></dd>"
            for name, value in facts
        )
        + "</dl>"
    )
    body += (
        "<h2>手册范围</h2>"
        "<p>按功能分类或助记符查找指令，从编码索引查看固定位和字段。Tile VEC、SFU、TLSU 和 CUBE 的操作在 Tile 索引中按引擎列出。</p>"
        "<p>DMA.FREE.L、DMA.FREE.S、MCOPY.DL、MCOPY.DS 仅预留编码，执行须在读取操作数或产生架构效果之前拒绝。</p>"
        "<h2>如何使用编码图</h2>"
        "<p>从编号最小的片段开始取指，每段内左侧为高位。掩码为 1 的位必须与匹配值相同；"
        "其余位由操作数字段占用。字段域和形式约束共同决定合法取值。</p>"
        "<p>"
        + _link(repo + "docs/zh/releases/v0.59.2.md", "0.59.2 发行说明")
        + " · "
        + _link(
            repo + "isa/v0.59.2/release_manifest.json", "规范清单"
        )
        + "</p>"
    )
    body += '<h2>离线发布文件</h2><div class="table-scroll"><table><tr><th>文件</th><th>SHA-256</th></tr>'
    for path, data in inputs.items():
        filename = Path(path).name
        body += (
            f"<tr><td>{_link('spec/' + filename, filename)}</td>"
            f"<td><code>{sha256(data).hexdigest()}</code></td></tr>"
        )
    return (
        body
        + "</table></div><p>"
        + _link("audit.json", "逐形式核对记录（JSON）")
        + "</p>"
    )


__all__ = ["sources_v0592"]
