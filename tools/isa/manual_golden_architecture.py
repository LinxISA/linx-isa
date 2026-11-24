#!/usr/bin/env python3
"""Current-only architecture chapters for the LinxISA v0.59.2 HTML manual."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import json
from typing import Any, Mapping

from manual_active_articles import ACTIVE_REPLACEMENTS
from manual_markdown import render_markdown_text


from manual_golden_datatypes import datatype_pages, datatype_index
from manual_golden_execution import (
    golden_execution_pages,
    SAIL_EXECUTE_SOURCE,
)
from manual_golden_registers import register_routes, register_sections
from manual_v0592_edition import read as release_bytes, release_decoder

CATALOG_SOURCE = "isa/v0.59.2/linxisa-v0.59.2.json"
REGISTER_SOURCE = "isa/v0.59/state/pto_system_registers.json"
TILE_SOURCE = "isa/v0.59/state/pto_tile_operations.json"

_READ = {
    "stored-value": "读取保存值",
    "architectural-time": "读取架构时间",
    "fixed-value": "读取固定实现值",
    "current-worker-launch-value-or-base": "读取当前工作任务的启动参数，无任务时读取基础值",
    "executing-pe-index": "读取当前执行 PE 编号",
    "packed-trap-status": "读取打包的异常状态",
    "trap-argument-zero": "读取异常参数寄存器 TRAPARG0",
    "refresh-timer-then-pending-bitmap": "刷新定时器后读取待处理中断位图",
    "refresh-timer-then-lowest-pending-id": "刷新定时器后读取最低编号的待处理中断",
    "saved-context-value": "读取保存的执行上下文",
    "message-status": "读取消息状态",
    "message-snapshot": "读取消息快照",
    "message-config": "读取消息配置",
    "reject-write-only": "只写，读取会被拒绝",
}
_WRITE = {
    "store-value": "写入并保存新值",
    "reject-read-only": "只读，写入会被拒绝",
    "unpack-trap-status": "把写入值解包到异常状态",
    "store-trap-argument-zero": "写入异常参数寄存器 TRAPARG0",
    "store-saved-context-value": "写入保存的执行上下文",
    "acknowledge-interrupt-id": "确认指定中断编号",
    "message-staging": "写入私有消息发送暂存区",
    "message-command": "提交消息 claim、release 或 acknowledge 命令",
    "message-config": "写入或选择消息配置",
}
_RESET = {
    "zero": "0",
    "one": "1",
    "external-and-timer-enabled": "外部中断和定时器中断使能",
    "pto-model-max-tile-capacity-bytes": "PTO 模型规定的最大 Tile 容量（字节）",
}
_EFFECT = {
    "write-selects-current-acr": "写入值同时选择当前 ACR",
    "advances-on-every-execution-attempt": "每次执行尝试都会推进",
    "launch-admission-binds-value": "工作任务获准启动时绑定其块数与块编号",
    "matching-done-restores-base-value": "匹配的 DONE 恢复基础值",
    "limits-per-tile-and-aggregate-allocation": "限制单个 Tile 和总分配容量",
    "save-and-recovery-state": "参与异常保存与恢复",
    "selects-trap-entry-tpc": "选择异常入口 TPC",
    "reads-and-writes-trap-bank-fields": "读写异常 bank 字段",
    "reads-and-writes-trap-bank-argument": "读写异常 bank 参数",
    "controls-external-and-timer-trap-entry": "控制外部和定时器异常入口",
    "reflects-external-and-timer-pending-sources": "反映外部和定时器待处理源",
    "priority-derived-from-pending-bitmap": "优先级由待处理位图确定",
    "clears-selected-pending-id": "清除指定待处理中断编号",
    "clears-asynchronous-trap-status": "清除异步异常状态",
    "identity-translation-does-not-consume-value": "恒等地址转换不会使用该配置值",
    "refreshes-timer-pending-state": "刷新定时器待处理状态",
    "does-not-consume-value": "读写本身不消费该值",
    "trap-save-clears-value": "异常保存时清零",
    "recovery-does-not-consume-value": "恢复不会消费该值",
    "trap-save-preserves-value": "异常保存保持该值",
    "debug-matching-disabled": "本发布模型未启用调试匹配",
    "marks-valid-snapshot-read": "读取后标记快照有效",
    "writes-private-tx-staging": "写入私有发送暂存区",
    "updates-claim-or-ack": "更新 claim 或 acknowledge 状态",
    "selects-and-binds-message-context": "选择并绑定消息上下文",
    "aliases-architectural-time": "与架构时间同源",
}


def _link(route: str, label: str) -> str:
    return f'<a href="{escape(route, quote=True)}">{escape(label)}</a>'


def _article(body: str) -> str:
    return (
        '<section class="authored-reader golden-architecture">'
        "<!-- authored:start -->" + body + "<!-- authored:end --></section>"
    )


def _list(items: list[tuple[str, str]]) -> str:
    return (
        '<ul class="chapter-index">'
        + "".join(f"<li>{_link(route, title)}</li>" for route, title in items)
        + "</ul>"
    )


def _detail(text: str, links: list[tuple[str, str]] | None = None) -> str:
    result = f"<p>{escape(text)}</p>"
    if links:
        result += (
            "<p>相关定义　"
            + " · ".join(_link(route, label) for route, label in links)
            + "</p>"
        )
    return result


def _register_behavior(document: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for behavior in document["behavior_classes"]:
        for name in behavior["registers"]:
            if name in result:
                raise ValueError(f"duplicate behavior owner for {name}")
            result[name] = behavior
    names = {str(row["name"]) for row in document["registers"]}
    if names != set(result):
        raise ValueError("system-register behavior coverage differs from the catalog")
    return result


def _render_registers(document: Mapping[str, Any]) -> str:
    if document.get("register_definition_count") != 100:
        raise ValueError("v0.59.2 golden manual requires 100 system registers")
    owners = _register_behavior(document)
    anchors = register_routes(document)
    rows = []
    for register in document["registers"]:
        name = str(register["name"])
        behavior = owners[name]
        address = str(register.get("address", register.get("low_index")))
        effects = "；".join(_EFFECT[value] for value in behavior["side_effects"])
        operation = (
            f"{_READ[behavior['read']]}；{_WRITE[behavior['write']]}；"
            f"复位值为 {_RESET[behavior['reset']]}"
            + (f"；{effects}" if effects else "")
        )
        key = f"{register['scope']}:{name}:{address}"
        rows.append(
            f'<tr data-register-key="{escape(key, quote=True)}">'
            f'<td><a href="{escape(anchors[name].split("arch-ssr.html", 1)[1], quote=True)}"><code>{escape(name)}</code></a></td><td><code>{escape(address)}</code></td>'
            f"<td>{escape(str(register['access']))}</td><td>{escape(str(register['scope']))}</td>"
            f"<td>{escape(operation)}</td></tr>"
        )
    return (
        '<div class="table-scroll"><table class="system-register-catalog"><thead><tr>'
        "<th>名称</th><th>地址/低位索引</th><th>访问</th><th>作用域</th><th>当前架构行为</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    )


def _render_traps(document: Mapping[str, Any]) -> str:
    if document.get("trap_count") != len(document.get("trap_numbers", [])):
        raise ValueError("trap inventory count differs")
    rows = []
    for trap in document["trap_numbers"]:
        producers = "、".join(str(value) for value in trap["producers"])
        rows.append(
            f"<tr><td><code>{int(trap['number'])}</code></td><td><code>{escape(str(trap['name']))}</code></td>"
            f"<td>{escape(str(trap['argument']))}</td><td>{escape(str(trap['restart']))}</td>"
            f"<td><code>{escape(producers)}</code></td></tr>"
        )
    return (
        '<div class="table-scroll"><table><thead><tr><th>编号</th><th>名称</th><th>参数</th>'
        "<th>重启位置</th><th>产生路径</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def golden_architecture_routes() -> frozenset[str]:
    return (
        frozenset(
            {
                "architecture.html",
                "execution-model.html",
                "arch-state.html",
                "arch-system.html",
                "arch-ssr.html",
                "arch-datatypes.html",
                "arch-block-isa.html",
                "arch-branch.html",
                "arch-execution.html",
                "arch-execution-machine.html",
                "arch-program-order.html",
                "arch-constraints.html",
                "arch-std-block.html",
                "arch-fp-block.html",
                "arch-sys-block.html",
                "arch-cube-block.html",
                "arch-tlsu-block.html",
                "arch-tepl-carrier.html",
                "arch-register-state.html",
                "arch-ggpr.html",
                "arch-sgpr.html",
                "arch-tile-registers.html",
                "arch-barg.html",
                "arch-bpc.html",
                "arch-tpc.html",
                "arch-loop.html",
                "arch-ltar.html",
                "arch-ssr-overview.html",
                "arch-acr.html",
                "arch-privilege.html",
                "arch-exception-model.html",
                "arch-interrupts.html",
                "arch-timer.html",
                "arch-memory-context.html",
            }
        )
        | frozenset(datatype_pages())
        | {
            "arch-fixup.html",
            "arch-xb-block.html",
            "arch-state-lgpr.html",
            "arch-tile-masks.html",
            "arch-privilege-switch.html",
            "arch-exception-overview.html",
            "arch-instruction-widths.html",
        }
    )


def golden_architecture_bodies(
    commit: str,
    catalog: Mapping[str, Any],
    registers: Mapping[str, Any],
    tiles: Mapping[str, Any],
    source_bytes: Mapping[str, bytes] | None = None,
) -> tuple[dict[str, tuple[str, str]], dict[str, dict[str, Any]]]:
    """Return current architecture pages and their machine-source audit."""
    if catalog.get("version") != "0.59.2" or catalog.get("instruction_count") != 1499:
        raise ValueError("golden architecture requires the v0.59.2 release catalog")
    if tiles.get("operation_count") != 119:
        raise ValueError("golden architecture requires 119 Tile operations")
    engines = Counter(str(row["engine"]) for row in tiles["operations"])
    if engines != Counter({"VEC": 32, "SFU": 47, "TLSU": 28, "CUBE": 12}):
        raise ValueError("Tile engine inventory differs")

    execution = [
        ("arch-block-isa.html", "块生命周期"),
        ("arch-branch.html", "块间控制流"),
        ("arch-execution.html", "执行与提交"),
        ("arch-execution-machine.html", "执行机制"),
        ("arch-program-order.html", "程序序与可见性"),
        ("arch-constraints.html", "合法性与故障边界"),
        ("arch-std-block.html", "整型标量块"),
        ("arch-fp-block.html", "浮点标量块"),
        ("arch-sys-block.html", "系统块"),
        ("arch-cube-block.html", "CUBE Tile 操作"),
        ("arch-tlsu-block.html", "TLSU Tile 操作"),
        ("arch-tepl-carrier.html", "VEC/SFU 编码载体"),
    ]
    state = [
        ("arch-register-state.html", "架构状态目录"),
        ("arch-ggpr.html", "全局标量寄存器"),
        ("arch-sgpr.html", "标量源与临时队列"),
        ("arch-tile-registers.html", "Tile 资源与绑定"),
        ("arch-barg.html", "块控制状态"),
        ("arch-bpc.html", "BPC"),
        ("arch-tpc.html", "TPC"),
        ("arch-loop.html", "块内维度"),
        ("arch-ltar.html", "目标状态"),
        ("arch-ssr-overview.html", "系统寄存器访问"),
    ]
    system = [
        ("arch-acr.html", "访问控制环"),
        ("arch-privilege.html", "权限检查"),
        ("arch-exception-model.html", "异常模型"),
        ("arch-interrupts.html", "中断状态"),
        ("arch-timer.html", "定时器"),
        ("arch-memory-context.html", "内存与作用域"),
    ]
    intro = (
        "<p>本章只呈现 v0.59.2 发布目录和锁定 PTO 定义中的当前架构行为。"
        "具体指令的操作数、编码、异常和写回顺序以对应指令页为准。</p>"
    )
    pages: dict[str, tuple[str, str]] = {
        "architecture.html": (
            "架构与执行模型",
            intro
            + _list(
                [
                    ("execution-model.html", "执行模型与块生命周期"),
                    ("arch-state.html", "架构状态"),
                    ("arch-system.html", "异常、权限与内存"),
                    ("arch-ssr.html", "100 项系统寄存器"),
                    ("arch-datatypes.html", "数据类型"),
                ]
            ),
        ),
        "execution-model.html": ("执行模型与块生命周期", intro + _list(execution)),
        "arch-state.html": ("架构状态", intro + _list(state)),
        "arch-system.html": ("异常、权限与内存", intro + _list(system)),
        "arch-datatypes.html": (
            "数据类型",
            _article(
                "<p>标量浮点、整数转换和 Tile 操作各自编码源类型与目标类型。"
                "合法类型、舍入、饱和、NaN 和有符号零规则在对应操作页中列出；"
                "软件不得从名称推导未编码的转换。</p>"
                '<p>相关定义　<a href="op-fcvt.html">FCVT</a> · '
                '<a href="op-scvtf.html">SCVTF</a> · '
                '<a href="tile-tcvt.html">TCVT</a></p>'
            ),
        ),
    }

    current: dict[str, tuple[str, str]] = {
        "arch-block-isa.html": (
            "块生命周期",
            "块头建立块描述符并登记配置。第一条普通标量指令进入块体，之后再执行头部配置会触发块控制异常。BSTOP 或下一条 BSTART 形成提交边界。",
        ),
        "arch-branch.html": (
            "块间控制流",
            "FALL、DIRECT、COND、CALL、IND、ICALL 和 RET 的目标在块头执行时记录，在提交边界生效。每个块头形式使用的 PC 基准和返回地址写回以该形式的指令页为准。",
        ),
        "arch-execution.html": (
            "执行与提交",
            "指令先完成适用性、操作数可用性和合法性检查，再读取源并产生效果。Tile 头部先完成维度、属性和绑定登记，进入块体后可执行适用于当前 Tile 块的标量指令；提交时读取完整块描述符并发布结果。",
        ),
        "arch-execution-machine.html": (
            "执行机制",
            "当前架构区分块头配置、标量块体和提交。实现可以并行准备互不依赖的工作，但软件可见状态只按具体指令规定的快照、故障和写回规则改变。",
        ),
        "arch-program-order.html": (
            "程序序与可见性",
            "同一执行流的架构效果按程序序可见。实现可并行安排互不依赖的工作，但必须保持源快照、故障先后、内存次序和结果发布顺序。矩阵累加读取显式源 C 并写入独立目标 D。",
        ),
        "arch-constraints.html": (
            "合法性与故障边界",
            "固定编码、保留字段、操作数绑定、类型、布局、维度和资源容量必须在该操作的第一个架构效果之前检查。四个仅预留编码的形式必须在读取操作数或产生架构效果之前拒绝。",
        ),
        "arch-std-block.html": (
            "整型标量块",
            "BSTART.STD 建立整型标量块。块体接受对应指令页声明可用于标准块的标量指令，提交条件和下一块目标由块控制状态决定。",
        ),
        "arch-fp-block.html": (
            "浮点标量块",
            "BSTART.FP 建立浮点标量块。浮点操作通过 CORE_STATE 选择活动舍入模式并累计数值状态标志；具体格式范围和异常标志以操作页为准。",
        ),
        "arch-sys-block.html": (
            "系统块",
            "BSTART.SYS 建立系统块。系统寄存器访问、缓存与 TLB 维护以及架构上下文操作只在其发布定义允许的块类型与权限下执行。",
        ),
        "arch-cube-block.html": (
            "CUBE Tile 操作",
            f"CUBE 引擎包含 {engines['CUBE']} 个发布操作。矩阵输入、显式累加源、偏置、缩放和目的 Tile 都通过块头绑定；不存在隐式累加器。",
        ),
        "arch-tlsu-block.html": (
            "TLSU Tile 操作",
            f"TLSU 引擎包含 {engines['TLSU']} 个发布操作。地址、字节位移、布局、作用域和预检边界由各操作定义；故障前不得留下部分 Tile 结果。",
        ),
        "arch-tepl-carrier.html": (
            "VEC/SFU 编码载体",
            f"TEPL 是 Mode/Function 编码载体。Tile VEC 有 {engines['VEC']} 个操作，SFU 有 {engines['SFU']} 个操作。TEPL 本身不是执行引擎。",
        ),
        "arch-register-state.html": (
            "架构状态目录",
            "当前状态包括标量寄存器和临时队列、块控制状态、Local/Shared Tile、100 项系统寄存器以及各操作显式声明的输入和目的。",
        ),
        "arch-ggpr.html": (
            "全局标量寄存器",
            "Reg5 源代码 0 至 23 选择全局标量寄存器。代码 0 是架构零寄存器；其余代码的可写性和作为目的时的行为由通用 Reg5 映射定义。",
        ),
        "arch-sgpr.html": (
            "标量源与临时队列",
            "Reg5 源代码 24 至 27 选择 T#1 至 T#4，28 至 31 选择 U#1 至 U#4。相对读取不消费队列元素。目的代码 30、31 分别把结果压入 U、T 队列。",
        ),
        "arch-tile-registers.html": (
            "Tile 资源与绑定",
            "B.IOT 绑定 Local Tile 源和重命名目的。B.IOS 按绝对编号绑定 Shared Tile。Tile 的类型、布局、有效区域、物理大小和 definedness 都是显式描述符状态。",
        ),
        "arch-barg.html": (
            "块控制状态",
            "块描述符记录当前块类型、块起点、待提交目标、转移类型和操作配置。提交条件由 SETC.* 或 C.SETC.* 写入，具体重复写和适用性规则以指令页为准。",
        ),
        "arch-bpc.html": (
            "BPC",
            "BPC 是当前块起点。块间 PC 相对目标使用的基准由具体块头形式规定，不能统一假定为当前指令地址。",
        ),
        "arch-tpc.html": (
            "TPC",
            "TPC 指向当前块内正在执行的指令。成功执行后按指令长度推进；故障和阻塞路径是否推进由对应操作的精确规则决定。",
        ),
        "arch-loop.html": (
            "块内维度",
            "LB0、LB1、LB2 的省略有效值均为 1。显式 B.DIM 或 C.B.DIMI（包括写入零）替换对应有效值；presence 只用于重复写和恢复记账。",
        ),
        "arch-ltar.html": (
            "目标状态",
            "目标寄存器或 Tile 由每条指令的目的字段及绑定命令显式选择。双目的形式按指令页规定的先后顺序发布；别名时最终值由该顺序决定。",
        ),
        "arch-ssr-overview.html": (
            "系统寄存器访问",
            "SSRGET、SSRSET、SSRSWAP 及其压缩、长形式按编码地址访问系统寄存器。访问必须同时满足寄存器读写属性、当前 ACR 和指令适用性。",
        ),
        "arch-acr.html": (
            "访问控制环",
            "context-family 系统寄存器按当前 ACR 选择 bank。CORE_STATE 写入会选择当前 ACR；异常保存和恢复使用该 bank 的执行上下文。",
        ),
        "arch-privilege.html": (
            "权限检查",
            "系统寄存器与维护操作在第一个状态读取或效果前检查权限。权限不足、保留地址或错误的读写方向触发对应故障。",
        ),
        "arch-exception-model.html": (
            "异常模型",
            f"本版定义 {int(registers['trap_count'])} 个异常编号。异常入口、参数和重启位置见下表。"
            + _render_traps(registers),
        ),
        "arch-interrupts.html": (
            "中断状态",
            "IPENDING_ACRn 反映外部与定时器待处理源；TOPEI_ACRn 给出优先级选择后的编号；EOIEI_ACRn 确认编号并清理对应待处理和异步异常状态。",
        ),
        "arch-timer.html": (
            "定时器",
            "TIME、CYCLE 和 TIMER_TIME_ACRn 读取架构时间。TIMER_TIMECMP_ACRn 保存比较值并刷新定时器待处理状态。",
        ),
        "arch-memory-context.html": (
            "内存与作用域",
            "内存按小端序访问。带作用域的标量形式显式选择 Private、IntraCore 或 InterCore 属性；原子操作、FENCE.D、FENCE.I 和 Tile TLSU 操作分别定义自己的排序与可见性。",
        ),
    }
    related = {
        "arch-std-block.html": [
            ("op-bstart-std.html", "BSTART.STD"),
            ("op-bstop.html", "BSTOP"),
        ],
        "arch-fp-block.html": [
            ("op-bstart-fp.html", "BSTART.FP"),
            ("op-fadd.html", "FADD"),
        ],
        "arch-sys-block.html": [
            ("op-bstart-sys.html", "BSTART.SYS"),
            ("op-ssrget.html", "SSRGET"),
        ],
        "arch-cube-block.html": [
            ("tile-tmatmul.html", "TMATMUL"),
            ("tile-tmatmul-acc.html", "TMATMUL_ACC"),
            ("tile-tgemv.html", "TGEMV"),
        ],
        "arch-tlsu-block.html": [
            ("tile-tload.html", "TLOAD"),
            ("tile-tstore.html", "TSTORE"),
            ("tile-mgather.html", "MGATHER"),
            ("tile-mscatter.html", "MSCATTER"),
        ],
        "arch-tepl-carrier.html": [
            ("op-bstart-tepl.html", "BSTART.TEPL"),
            ("tiles-vec.html", "Tile VEC"),
            ("tiles-sfu.html", "Tile SFU"),
        ],
        "arch-tile-registers.html": [
            ("op-b-iot.html", "B.IOT"),
            ("op-b-ios.html", "B.IOS"),
            ("op-b-datr.html", "B.DATR"),
            ("op-b-dim.html", "B.DIM"),
        ],
        "arch-ssr-overview.html": [
            ("op-ssrget.html", "SSRGET"),
            ("op-ssrset.html", "SSRSET"),
            ("op-ssrswap.html", "SSRSWAP"),
            ("arch-ssr.html", "100 项寄存器表"),
        ],
        "arch-memory-context.html": [
            ("op-fence-d.html", "FENCE.D"),
            ("op-fence-i.html", "FENCE.I"),
            ("op-lr-d.html", "LR.D"),
            ("tile-mgather.html", "MGATHER"),
        ],
    }
    for route, (title, text) in current.items():
        body = text if "<" in text else f"<p>{escape(text)}</p>"
        if route in related and "<" not in text:
            body = _detail(text, related[route])
        pages[route] = (title, _article(body))

    # These ten chapters were already rewritten and reviewed against the
    # v0.59.2 catalog.  Render those complete explanations instead of reducing
    # them to a navigation synopsis.
    reviewed = {
        "docs/zh/isa/arch/bisa.md": "arch-block-isa.html",
        "docs/zh/isa/arch/branch.md": "arch-branch.html",
        "docs/zh/isa/arch/execute.md": "arch-execution.html",
        "docs/zh/isa/arch/executemachine.md": "arch-execution-machine.html",
        "docs/zh/isa/arch/prgorder.md": "arch-program-order.html",
        "docs/zh/isa/arch/constraints.md": "arch-constraints.html",
        "docs/zh/isa/exception/acr_switch.md": "arch-acr.html",
        "docs/zh/isa/register/common/intro.md": "arch-register-state.html",
        "docs/zh/isa/blockIntro/tlsu_block/intro.md": "arch-tlsu-block.html",
    }
    for path, route in reviewed.items():
        rendered = render_markdown_text(
            path,
            ACTIVE_REPLACEMENTS[path],
            current_page=route,
            document_routes={},
        )
        if rendered.documents or rendered.assets:
            raise ValueError(
                f"golden architecture replacement has dependencies: {path}"
            )
        pages[route] = (pages[route][0], _article(rendered.html))

    exception_path = "docs/zh/isa/arch/exception.md"
    exception = render_markdown_text(
        exception_path,
        ACTIVE_REPLACEMENTS[exception_path],
        current_page="arch-exception-model.html",
        document_routes={},
    )
    pages["arch-exception-model.html"] = (
        "异常模型",
        _article(
            exception.html
            + f"<h2>异常编号</h2><p>本版定义 {int(registers['trap_count'])} 个异常编号。</p>"
            + _render_traps(registers)
        ),
    )

    pages["arch-ssr.html"] = (
        "系统寄存器",
        _article(
            '<h2 id="system-registers">系统寄存器目录</h2><p>下表列出 100 项系统寄存器。'
            "按名称查看地址、权限、作用域、复位值及读写时的架构行为。</p>"
            + _render_registers(registers)
            + register_sections(registers)[0]
        ),
    )
    extended, execution_audit, _ = golden_execution_pages(
        commit,
        catalog,
        registers,
        release_decoder(),
        release_bytes(SAIL_EXECUTE_SOURCE),
    )
    pages.update(extended)
    pages.update(datatype_pages())
    pages["arch-datatypes.html"] = datatype_index()
    format_counts = Counter(
        row["length_bits"]
        for row in catalog["instructions"]
        if row.get("architecture_status", {}).get("state") != "obsolete"
    )
    widths = [
        (16, "C.ADD 对两个完整源值求和并把结果压入 T 队列。", "op-c-add.html", "C.ADD"),
        (
            32,
            "ADD 可先变换并移位右源，结果可写入 T、U 或通用寄存器。",
            "op-add.html",
            "ADD",
        ),
        (
            48,
            "HL.ADDI 对 24 位立即数作零扩展，再与源寄存器相加。",
            "op-hl-addi.html",
            "HL.ADDI",
        ),
        (
            64,
            "L.BSTART.STD 编码块转移；带作用域的访存形式也使用 64 位编码。",
            "op-l-bstart-std.html",
            "L.BSTART.STD",
        ),
    ]
    width_table = "".join(
        f"<tr><td>{width}</td><td>{format_counts[width]}</td><td>{desc} {_link(url, name)}</td></tr>"
        for width, desc, url, name in widths
    )
    pages["arch-instruction-widths.html"] = (
        "指令长度与块体适用性",
        _article(
            "<p>指令位宽决定一次取出的字节数。编码长度、操作数类型和允许执行的块类型分别由各形式定义。</p>"
            '<div class="table-scroll"><table><thead><tr><th>位宽</th><th>形式数</th><th>示例</th></tr></thead><tbody>'
            + width_table
            + "</tbody></table></div>"
            "<p>在已打开且尚未进入块体的 Tile 块中，标量指令译码成功后先进入块体，然后检查该操作是否适用以及操作数是否合法。"
            "后续的标量故障保留已经进入块体的状态和原块类型。系统块的专用操作仍要满足自己的适用条件。</p>"
            + _link("encoding.html", "查阅所有编码形式")
        ),
    )
    for index, links in {
        "execution-model.html": (
            "arch-instruction-widths.html",
            "arch-fixup.html",
            "arch-xb-block.html",
        ),
        "arch-state.html": ("arch-state-lgpr.html", "arch-tile-masks.html"),
        "arch-system.html": (
            "arch-privilege-switch.html",
            "arch-exception-overview.html",
        ),
    }.items():
        title, body = pages[index]
        pages[index] = (
            title,
            body + _list([(route, pages[route][0]) for route in links]),
        )
    if set(pages) != golden_architecture_routes():
        raise ValueError("golden architecture route inventory differs")

    if source_bytes is None:
        source_bytes = {
            CATALOG_SOURCE: json.dumps(
                catalog, sort_keys=True, separators=(",", ":")
            ).encode(),
            REGISTER_SOURCE: json.dumps(
                registers, sort_keys=True, separators=(",", ":")
            ).encode(),
            TILE_SOURCE: json.dumps(
                tiles, sort_keys=True, separators=(",", ":")
            ).encode(),
        }
    expected_sources = {CATALOG_SOURCE, REGISTER_SOURCE, TILE_SOURCE}
    if set(source_bytes) != expected_sources:
        raise ValueError("golden architecture source-byte inventory differs")
    decoded = {CATALOG_SOURCE: catalog, REGISTER_SOURCE: registers, TILE_SOURCE: tiles}
    for path, expected in decoded.items():
        if json.loads(source_bytes[path]) != expected:
            raise ValueError(f"golden architecture source bytes differ for {path}")
    audit = {
        route: {
            "origin": "v0.59.2-machine-projection",
            "source_commit": commit,
            "sources": {
                path: sha256(data).hexdigest() for path, data in source_bytes.items()
            },
            "body_sha256": sha256(body.encode()).hexdigest(),
        }
        for route, (_, body) in pages.items()
    }
    for route, record in execution_audit.items():
        audit[route]["sources"].update(record.get("sources", {}))
    return pages, audit


__all__ = [
    "golden_architecture_bodies",
    "golden_architecture_routes",
]
