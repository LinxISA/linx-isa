"""Current-only architecture pages for the LinxISA 0.59.1 HTML edition."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any

try:
    from manual_v0591_datatypes import datatype_assets
    from manual_v0591_datatypes import datatype_index
    from manual_v0591_datatypes import datatype_pages
    from manual_v0591_registers import PTO_COMMIT
    from manual_v0591_registers import register_evidence
    from manual_v0591_registers import register_routes
    from manual_v0591_registers import register_sections
except ModuleNotFoundError:
    from tools.isa.manual_v0591_datatypes import datatype_assets
    from tools.isa.manual_v0591_datatypes import datatype_index
    from tools.isa.manual_v0591_datatypes import datatype_pages
    from tools.isa.manual_v0591_registers import PTO_COMMIT
    from tools.isa.manual_v0591_registers import register_evidence
    from tools.isa.manual_v0591_registers import register_routes
    from tools.isa.manual_v0591_registers import register_sections


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "isa/v0.59/linxisa-v0.59.json"
LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
REGISTERS = ROOT / "isa/v0.59/state/pto_system_registers.json"
TILE_OPERATIONS = ROOT / "isa/v0.59/state/pto_tile_operations.json"

REMOVED = frozenset(
    {
        "B.TEXT",
        "BSTART.MPAR",
        "BSTART.MSEQ",
        "BSTART.VPAR",
        "BSTART.VSEQ",
        "C.BSTART.MPAR",
        "C.BSTART.MSEQ",
        "C.BSTART.VPAR",
        "C.BSTART.VSEQ",
    }
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _article(body: str) -> str:
    return '<article class="architecture-current">' + body + "</article>"


def _forms(catalog: dict[str, Any], mnemonic: str) -> list[dict[str, Any]]:
    return [row for row in catalog["instructions"] if row["mnemonic"] == mnemonic]


def _form_table(rows: list[dict[str, Any]]) -> str:
    body = "".join(
        "<tr>"
        f"<td><code>{escape(str(row['mnemonic']))}</code></td>"
        f"<td>{int(row['length_bits'])}</td>"
        f"<td><code>{escape(str(row['asm']))}</code></td>"
        "</tr>"
        for row in rows
    )
    return (
        '<div class="table-scroll"><table><thead><tr><th>助记符</th><th>位宽</th>'
        f"<th>汇编形式</th></tr></thead><tbody>{body}</tbody></table></div>"
    )


def _core_pages(
    catalog: dict[str, Any], registers: dict[str, Any], tile: dict[str, Any]
) -> dict[str, tuple[str, str]]:
    counts = catalog["release_status"]["counts"]
    overview = _article(
        "<h2>规范边界</h2>"
        f"<p>本视图只描述 LinxISA 0.59.1 的 {catalog['instruction_count']} 个当前指令形式："
        f"{counts['common']} 个公共形式、{counts['linx_only']} 个 Linx 扩展形式和 "
        f"{counts['scoped']} 个作用域形式。编码和架构效果来自 0.59.1 目录及其锁定的 PTO 定义。</p>"
        "<p>架构定义说明软件可观察的状态、合法性和效果；实现说明只能解释一种实现如何满足这些约束，"
        "不增加流水级数、队列深度、吞吐或物理寄存器数量等架构保证。</p>"
    )

    fall_names = (
        "HL.BSTART.FP",
        "HL.BSTART.STD",
        "HL.BSTART.SYS",
        "L.BSTART.FP",
        "L.BSTART.STD",
        "L.BSTART.SYS",
    )
    fall = [
        row
        for name in fall_names
        for row in _forms(catalog, name)
        if "FALL" in str(row["asm"])
    ]
    execution = _article(
        "<h2>块入口与 FALL</h2>"
        "<p>FP、STD、SYS 的短扩展和长扩展入口保留六个 FALL 形式。FALL 使用当前顺序后继作为块目标，"
        "并按该助记符建立对应的块类型；CALL、DIRECT、COND 仍只出现在各自有编码的形式上。</p>"
        + _form_table(fall)
        + "<h2>实施边界</h2><p>参考 Sail 提供可执行的解码、陷阱顺序和已实现效果。"
        "没有实现的当前编码必须在读取操作数或产生架构效果前拒绝；这不把某个微体系结构队列或调度策略提升为 ISA 状态。</p>"
    )

    bdim = _forms(catalog, "B.DIM")
    register_page = _article(
        "<h2>标量寄存器与 T/U</h2>"
        "<p>普通 Reg5 源选择标量寄存器；作用域标量形式可显式读取 T#1 至 T#4、U#1 至 U#4，"
        "并由带有相应目的字段的指令把结果写入 T 或 U。读取和写回由指令字段明确指定，不存在额外的隐式块外队列入口。</p>"
        "<h2>LB0、LB1、LB2</h2><p>三个 LB 保存块局部维度。B.DIM 明确选择目的 LB，"
        "Tile 入口和 Tile 操作按自己的契约消费这些维度。</p>"
        + _form_table(bdim)
        + "<h2>Tile 谓词与掩码</h2><p>谓词不是通用的隐藏向量状态。TCMP、TCMPS 产生操作定义的谓词载体；"
        "TSEL、TSELS 读取其显式掩码源；MGATHER_MASK 与 MSCATTER_MASK 的掩码也由各自操作数字段给出。"
        "未参与元素的填充值和副作用以具体 Tile 操作契约为准。</p>"
    )

    implementation = _article(
        "<h2>架构要求</h2><p>实现必须遵守目录中的编码、操作数、异常先后顺序、系统寄存器行为、"
        "Tile 操作合法性以及完成后的架构状态。</p>"
        "<h2>实现选择</h2><p>取指宽度、重命名、ROB、issue queue、执行端口、Tile 物理存储和流水级划分"
        "均属于实现。手册中的示意图不得被解释为这些资源的固定数量或时序承诺。</p>"
    )
    return {
        "arch-overview.html": ("架构总览", overview),
        "arch-execution.html": ("执行与块控制", execution),
        "arch-registers.html": ("寄存器、LB 与 Tile 谓词", register_page),
        "arch-implementation-boundary.html": ("架构与实施边界", implementation),
    }


def pages() -> dict[str, tuple[str, str]]:
    catalog = _load(CATALOG)
    registers = _load(REGISTERS)
    tile = _load(TILE_OPERATIONS)
    result = _core_pages(catalog, registers, tile)
    ssr_html, _ = register_sections(registers)
    result["arch-ssr.html"] = (
        "系统寄存器（SSR）",
        _article(
            '<h2 id="system-registers">系统寄存器目录</h2>'
            "<p>下表逐项列出 100 个当前 SSR 的地址、作用域、真实字段、读写行为、副作用和复位定义。"
            "所有条目直接来自锁定的系统寄存器目录。</p>" + ssr_html
        ),
    )
    result.update(datatype_pages())
    result["arch-datatypes.html"] = datatype_index()
    return dict(sorted(result.items()))


def routes() -> dict[str, str]:
    result = {route: route for route in pages()}
    result.update(register_routes(_load(REGISTERS)))
    return dict(sorted(result.items()))


def assets() -> dict[str, bytes]:
    return datatype_assets()


def audit() -> dict[str, Any]:
    catalog = _load(CATALOG)
    lock = _load(LOCK)
    registers = _load(REGISTERS)
    tile = _load(TILE_OPERATIONS)
    instructions = catalog["instructions"]
    obsolete = [
        row["id"]
        for row in instructions
        if row["mnemonic"].startswith("V.") or row["mnemonic"] in REMOVED
    ]
    if obsolete:
        raise ValueError(
            f"0.59.1 architecture view contains {len(obsolete)} retired forms"
        )
    if len(instructions) != 1306:
        raise ValueError("0.59.1 architecture view requires exactly 1306 forms")
    if lock["release"] != "0.59.1" or lock["source"]["commit"] != PTO_COMMIT:
        raise ValueError("0.59.1 architecture evidence does not match the PTO lock")
    if (
        registers.get("register_definition_count") != 100
        or len(registers.get("registers", [])) != 100
    ):
        raise ValueError("SSR view requires exactly 100 current definitions")
    if lock["catalogs"]["system_registers"]["count"] != 100:
        raise ValueError("PTO lock does not bind the 100-register catalog")
    if (
        tile.get("operation_count") != 119
        or lock["catalogs"]["tile_operations"]["count"] != 119
    ):
        raise ValueError(
            "Tile operation view differs from the locked 119-operation catalog"
        )
    fall = [
        row
        for row in instructions
        if row["mnemonic"]
        in {
            "HL.BSTART.FP",
            "HL.BSTART.STD",
            "HL.BSTART.SYS",
            "L.BSTART.FP",
            "L.BSTART.STD",
            "L.BSTART.SYS",
        }
        and "FALL" in row["asm"]
    ]
    if len(fall) != 6:
        raise ValueError("the six current extended FALL forms are incomplete")
    data_assets = assets()
    bad_svg = [
        name
        for name, data in data_assets.items()
        if not data.lstrip().startswith(b"<svg")
        or b'width="1"' in data
        or b'height="1"' in data
    ]
    if bad_svg:
        raise ValueError(f"datatype assets are not effective SVGs: {bad_svg}")
    evidence = register_evidence(registers)
    return {
        "schema": "linxisa.manual-v0591-architecture-audit.v1",
        "version": "0.59.1",
        "pto_commit": PTO_COMMIT,
        "catalog_forms": len(instructions),
        "ssr_count": evidence["register_count"],
        "tile_operation_count": tile["operation_count"],
        "fall_forms": [row["id"] for row in fall],
        "page_count": len(pages()),
        "route_count": len(routes()),
        "asset_count": len(data_assets),
        "register_evidence": evidence,
        "sources": {
            "catalog": CATALOG.relative_to(ROOT).as_posix(),
            "pto_lock": LOCK.relative_to(ROOT).as_posix(),
            "system_registers": REGISTERS.relative_to(ROOT).as_posix(),
            "tile_operations": TILE_OPERATIONS.relative_to(ROOT).as_posix(),
        },
    }


__all__ = ["assets", "audit", "pages", "routes"]
