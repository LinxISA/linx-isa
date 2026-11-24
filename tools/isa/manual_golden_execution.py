#!/usr/bin/env python3
"""Reviewed execution, state, system and implementation pages for v0.59.2."""

from __future__ import annotations

from hashlib import sha256
from html import escape
from typing import Any, Mapping


IMPLEMENTATION_SOURCES = {
    "implementation-bcc": "docs/zh/isa/model/BCC.md",
    "implementation-bctrl": "docs/zh/isa/model/BCTRL.md",
    "implementation-bifu": "docs/zh/isa/model/BIFU.md",
    "implementation-bissue": "docs/zh/isa/model/BIssue.md",
    "implementation-brob": "docs/zh/isa/model/BROB.md",
    "implementation-brename": "docs/zh/isa/model/BRename.md",
    "implementation-iex-dispatch": "docs/zh/isa/model/iex_dispatch.md",
    "implementation-iex-issueq": "docs/zh/isa/model/iex_issueq.md",
    "implementation-pe": "docs/zh/isa/model/pe.md",
    "implementation-pe-ibp": "docs/zh/isa/model/pe_ibp.md",
    "implementation-pe-ifu": "docs/zh/isa/model/pe_ifu.md",
    "implementation-pe-rob": "docs/zh/isa/model/pe_rob.md",
}
SAIL_EXECUTE_SOURCE = "isa/sail/model/execute/execute.sail"


_IMPLEMENTATION_REVIEW = {
    "implementation-bcc": (
        "BCC 与参考模型边界",
        "LinxCoreModel 的 cacheline 取指映射到 I-SIDE，预测算法映射到独立 B-SIDE。两侧独立反压，模型内部 stage 名称不定义目标架构 stage。",
        "current-mapping-note",
    ),
    "implementation-bctrl": (
        "Decode 与 Dispatch 参考映射",
        "资料以 D1 完整译码、D2 计算组资源、D3 原子接纳为参考流程。模型中的 MachineHeader 和函数名只描述软件组织。",
        "current-mapping-note",
    ),
    "implementation-bifu": (
        "IFU 参考映射",
        "资料说明 I-SIDE 和 B-SIDE 的解耦流水、预测 provider 次序、checkpoint 与恢复。这些 predictor 结构不是软件可见状态。",
        "current-mapping-note",
    ),
    "implementation-bissue": (
        "Block Issue Queue 实现示例",
        "示例从 BROB 最老块开始选择可发射项，在需要清除的块处停止，并把控制请求送往选定 PE。选择策略和扫描方式是模型选择。",
        "implementation-snapshot",
    ),
    "implementation-brob": (
        "BROB 实现示例",
        "示例用按程序序的 block retirement 维护资源释放。原资料明确说明该模型快照尚未实现处理器异常，不能用它证明完整精确异常。",
        "implementation-snapshot-with-gap",
    ),
    "implementation-brename": (
        "Block Rename 实现示例",
        "示例把 GET、SET 请求映射到投机映射表和物理寄存器空闲表。每周期重命名宽度和表结构是模型参数。",
        "implementation-snapshot",
    ),
    "implementation-iex-dispatch": (
        "IEX Dispatch 实现示例",
        "示例用分类队列接收重命名后的 ALU、load、store-address 和 store-data 微操作，再按实现策略分发。",
        "implementation-snapshot",
    ),
    "implementation-iex-issueq": (
        "IEX Issue Queue 实现示例",
        "示例列出 ALU、load、store、branch issue queue 及 select、RF、EXE 阶段。数量和阶段划分只描述该模型快照。",
        "implementation-snapshot",
    ),
    "implementation-pe": (
        "PE 与 IEX 实现索引",
        "该页组织 PE 取指、预测、ROB、dispatch 和 issue queue 的实现资料，不增加架构寄存器、时序或吞吐保证。",
        "implementation-index",
    ),
    "implementation-pe-ibp": (
        "PE 分支预测实现示例",
        "示例比较 perfect-trace、1 位和 2 位计数器模式，并使用 HyperTrace 与 hyperIQ。这些不是 ISA 要求的预测器。",
        "implementation-snapshot",
    ),
    "implementation-pe-ifu": (
        "PE IFU 参考映射",
        "资料描述 I-F0..I-F4、Instruction Buffer、D1 和独立 B-F0..B-F4，可用于当前 LinxCore IFU 设计对照。",
        "current-mapping-note",
    ),
    "implementation-pe-rob": (
        "PE ROB 实现示例",
        "示例列出算术、AGU、store、load 和 branch 的写回暂存通道。通道拆分与容器是模型内部结构。",
        "implementation-snapshot",
    ),
}


_REVIEW = {
    "block-isa": (
        "current-reviewed-base-page",
        "现行块配置、块体和提交规则有发布消费者。",
    ),
    "branch": ("current-reviewed-base-page", "基础与F-H保留块头继续使用块间控制状态。"),
    "execution": (
        "current-reviewed-base-page",
        "现行标量和Tile块继续使用配置、块体、提交阶段。",
    ),
    "execution-machine": (
        "current-reviewed-base-page",
        "保留架构阶段说明，不绑定具体流水级。",
    ),
    "execution-mode": (
        "outside-current-instruction-interface",
        "本页描述的两级块入口属于 A–E。发布模型保留相关兼容路径；该裁决没有独立废弃并行或顺序执行的设计原理。",
    ),
    "program-order": (
        "current-reviewed-base-page",
        "当前标量、内存和Tile结果仍依赖程序序。",
    ),
    "fixup": (
        "replace-with-retained-extended-fall-forms",
        "G/H 的六个 FALL 形式继续编码扩展目标。以发布 decoder 与 execute helper 核对字段读取；它们不足以证明旧文中 FUTO 超时代理和整套异常处理承诺。",
    ),
    "constraints": (
        "current-reviewed-base-page",
        "当前操作仍使用合法性与首效果前检查规则。",
    ),
    "std-block": ("current-base-page", "BSTART.STD仍是PTO-common。"),
    "sys-block": ("current-base-page", "BSTART.SYS仍是PTO-common。"),
    "fp-block": ("current-base-page", "BSTART.FP仍是PTO-common。"),
    "memory-block": ("remove-obsolete-topic", "该页只描述MSEQ/MPAR分离块。"),
    "vector-block": ("remove-obsolete-topic", "该页只描述VSEQ/VPAR及V.*块体。"),
    "cube-block": ("current-tile-page", "12个CUBE Tile操作继续存在。"),
    "tlsu-block": ("current-reviewed-base-page", "28个TLSU Tile操作继续存在。"),
    "tepl-carrier": ("current-tile-page", "BSTART.TEPL与Tile VEC/SFU继续存在。"),
    "xb-block": (
        "replace-with-current-extension-boundary",
        "XB保留解码身份但PTO路径在字段解释前拒绝。",
    ),
    "register-state": (
        "current-reviewed-base-page",
        "保留当前标量、Tile、块和SSR状态。",
    ),
    "ggpr": ("current-base-page", "Reg5绝对寄存器映射继续使用。"),
    "sgpr": ("current-base-page", "T/U临时队列继续由全部Reg5指令使用。"),
    "vgpr": (
        "compatibility-model-state",
        "这份资料描述二级执行模型的寄存器队列。193 项裁决指定编码；未对这些队列另行作废弃决策。用途见固定的 Sail 状态及执行代码。",
    ),
    "tile-registers": ("current-base-page", "119个Tile操作继续使用显式Tile绑定。"),
    "predicate": (
        "distinguish-state-and-consumers",
        "此前隐式 lane 谓词与现行 RowMajor 打包谓词并非同一接口。PTO 明确定义 P0–P7 的读写但没有直接编码消费者；TCMP、TSEL 等仍直接支持打包谓词、PredicateCell 或 GPR 载体，见 arch-tile-masks.html。",
    ),
    "barg": ("current-base-page", "保留块头继续使用块控制状态。"),
    "bpc": ("current-base-page", "保留块头继续使用BPC。"),
    "tpc": ("current-base-page", "全部当前指令继续使用TPC。"),
    "loop": ("current-base-page", "LB0/LB1/LB2继续定义Tile维度。"),
    "ltar": ("current-base-page", "保留当前目的和Tile绑定说明。"),
    "ssr": ("current-machine-generated-page", "100项SSR由当前目录生成。"),
    "core-state": (
        "move-to-implementation-section",
        "旧Janus核心图属于实现示例，CORE_STATE由SSR目录保留。",
    ),
    "state-lgpr": (
        "replace-with-current-temporary-and-gqm-queues",
        "旧页的 RI/RO 依赖块外参数传递；本次决策只列举指令形式。可由现行模型独立验证的是 T/U 与通用队列管理，二者另按各自操作说明。",
    ),
    "acr": ("current-base-page", "100项SSR中的context-family仍按ACR分bank。"),
    "privilege": ("current-base-page", "系统和维护指令仍执行权限检查。"),
    "privilege-switch": (
        "current-reviewed-supplement",
        "ACRE/ACRC及保存SSR仍有当前消费者。",
    ),
    "exception-model": (
        "current-machine-generated-page",
        "13项trap和保存SSR来自当前目录。",
    ),
    "interrupts": ("current-base-page", "IPENDING/TOPEI/EOIEI仍在100项SSR中。"),
    "timer": ("current-base-page", "TIME/CYCLE/TIMER_*仍在100项SSR中。"),
    "memory-context": (
        "current-base-page",
        "当前scope、atomics、fence和TLSU仍使用内存规则。",
    ),
    "arch-exception": (
        "replace-with-current-save-and-recovery-page",
        "只保留100项SSR能够保存和恢复的状态。",
    ),
    **{
        key: (
            "retain-as-nonnormative-implementation-evidence",
            "固定实现文档仍可用于设计对照，不转化为ISA承诺。",
        )
        for key in IMPLEMENTATION_SOURCES
    },
}


def _link(route: str, label: str) -> str:
    return f'<a href="{escape(route, quote=True)}">{escape(label)}</a>'


def _article(body: str) -> str:
    return (
        '<section class="authored-reader golden-execution"><!-- authored:start -->'
        + body
        + "<!-- authored:end --></section>"
    )


def _forms(catalog: Mapping[str, Any], mnemonic: str) -> list[Mapping[str, Any]]:
    return [row for row in catalog["instructions"] if row["mnemonic"] == mnemonic]


def _form_table(catalog: Mapping[str, Any], names: tuple[str, ...]) -> str:
    rows = []
    for name in names:
        for form in _forms(catalog, name):
            status = form.get("architecture_status", {})
            state = status.get("state", "PTO-common")
            ownership = status.get("encoding_ownership")
            label = f"{state} / {ownership}" if ownership else state
            rows.append(
                f"<tr><td><code>{escape(str(form['asm']))}</code></td><td><code>{escape(str(form['id']))}</code></td><td>{escape(label)}</td></tr>"
            )
    return (
        '<div class="table-scroll"><table><thead><tr><th>汇编形式</th><th>Form ID</th><th>状态</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div>"
    )


def execution_review() -> dict[str, dict[str, str]]:
    """Return the source-key decision table used by the golden manual."""
    return {
        key: {"disposition": value[0], "evidence": value[1]}
        for key, value in _REVIEW.items()
    }


def implementation_review(
    commit: str, implementation_sources: Mapping[str, bytes]
) -> dict[str, dict[str, str]]:
    """Return fixed-source evidence for a separate implementation review report."""
    if set(implementation_sources) != set(IMPLEMENTATION_SOURCES.values()):
        raise ValueError("implementation source inventory differs")
    result = {}
    for key, path in IMPLEMENTATION_SOURCES.items():
        title, summary, status = _IMPLEMENTATION_REVIEW[key]
        result[key] = {
            "title": title,
            "summary": summary,
            "review_status": status,
            "source_path": path,
            "source_sha256": sha256(implementation_sources[path]).hexdigest(),
            "source_url": f"https://github.com/LinxISA/linx-isa/blob/{commit}/{path}",
            "normative_scope": "implementation-reference-only",
        }
    return result


def golden_execution_pages(
    commit: str,
    catalog: Mapping[str, Any],
    registers: Mapping[str, Any],
    sail_decode: bytes,
    sail_execute: bytes,
) -> tuple[
    dict[str, tuple[str, str]], dict[str, dict[str, Any]], dict[str, dict[str, str]]
]:
    if (
        catalog.get("version") != "0.59.2"
        or registers.get("register_definition_count") != 100
    ):
        raise ValueError("golden execution pages require v0.59.2 catalog and 100 SSRs")

    retained_names = (
        "HL.BSTART.FP",
        "HL.BSTART.STD",
        "HL.BSTART.SYS",
        "L.BSTART.FP",
        "L.BSTART.STD",
        "L.BSTART.SYS",
    )
    retained = [row for name in retained_names for row in _forms(catalog, name)]
    if len(retained) != 18 or any(
        row.get("architecture_status", {}).get("state") != "retained"
        for row in retained
    ):
        raise ValueError("extended block-header inventory differs")
    if sum("FALL" in row["asm"] for row in retained) != 6:
        raise ValueError("extended FALL form inventory differs")
    decode_text = sail_decode.decode("utf-8")
    execute_text = sail_execute.decode("utf-8")
    for row in retained:
        if row["asm"] not in decode_text:
            raise ValueError(
                f"retained block header missing from Sail decode: {row['id']}"
            )
    for helper in (
        "exec_hl_bstart_fp",
        "exec_hl_bstart_std",
        "exec_hl_bstart_sys",
        "exec_bstart_fp",
        "exec_bstart_std",
        "exec_bstart_sys",
    ):
        if helper not in execute_text:
            raise ValueError(
                f"retained block helper missing from Sail execute: {helper}"
            )
    if (
        "decode_block_target30" not in decode_text
        or "decode_block_target42" not in decode_text
    ):
        raise ValueError("retained block target decoding is missing")

    pages: dict[str, tuple[str, str]] = {}
    pages["arch-fixup.html"] = (
        "扩展 FALL 块头",
        _article(
            "<p>v0.59.2 保留六个带扩展目标字段的 FALL 形式。解码器形成块目标并按普通 FALL 类型建立新的 FP、STD 或 SYS 块。"
            "扩展目标的译码与异常路由是两项独立的操作。下表区分顺延、跳转、条件和调用所用的编码；异常入口及恢复状态见系统寄存器表。</p>"
            + _form_table(catalog, retained_names)
            + "<p>对应详情页　"
            + " · ".join(
                _link(f"op-{name.lower().replace('.', '-')}.html", name)
                for name in retained_names
            )
            + "</p>"
        ),
    )

    boundary_names = ("XB", "ESAVE", "ERCOV")
    boundary = [row for name in boundary_names for row in _forms(catalog, name)]
    if len(boundary) != 3 or any(
        "reject" not in row.get("note", "").lower() for row in boundary
    ):
        raise ValueError("extension-boundary inventory differs")
    pages["arch-xb-block.html"] = (
        "扩展调用与上下文编码边界",
        _article(
            "<p>XB、ESAVE 和 ERCOV 的机器字由扩展空间拥有。PTO 执行路径必须在解释字段、读取操作数或产生架构效果之前拒绝。"
            "识别出这些编码时，软件不能据此假定上下文已被保存或恢复。</p>"
            + _form_table(catalog, boundary_names)
            + "<p>对应详情页　"
            + " · ".join(
                _link(f"op-{name.lower()}.html", name) for name in boundary_names
            )
            + "</p>"
        ),
    )

    queue_names = ("HL.QMT", "HL.QPUSH", "HL.QPOP")
    queues = [row for name in queue_names for row in _forms(catalog, name)]
    if len(queues) != 3 or any(not row.get("pto_source_form_id") for row in queues):
        raise ValueError("GQM instruction inventory differs")
    pages["arch-state-lgpr.html"] = (
        "块内临时队列与 General Queue Management",
        _article(
            "<h2>T、U 临时队列</h2><p>Reg5 源代码 24 至 27 读取 T#1 至 T#4，28 至 31 读取 U#1 至 U#4；相对读取不消费队列项。"
            "目的代码 30、31 分别把结果压入 U、T 队列。每条指令按自己的源快照和写回顺序执行。</p>"
            "<h2>General Queue Management</h2><p>HL.QMT 查询或控制 GQM 队列；HL.QPUSH 原子地从头部或尾部压入一个 64 位项；"
            "HL.QPOP 原子地弹出一个头部项。队列容量、状态码与结果写回见各指令的定义。</p>"
            + _form_table(catalog, queue_names)
            + "<p>指令详情　"
            + " · ".join(
                _link(f"op-{name.lower().replace('.', '-')}.html", name)
                for name in queue_names
            )
            + "</p>"
        ),
    )
    pages["arch-tile-masks.html"] = (
        "当前 Tile 执行掩码",
        _article(
            "<p>MGATHER_MASK 和 MSCATTER_MASK 使用显式谓词 Tile 选择参与索引访存的坐标。"
            "未启用坐标不生成地址，也不产生转换、权限检查或内存效果。"
            "这类绑定是该次访问的显式操作数。</p>"
            "<p>PTO 状态模型定义八个 32 位谓词寄存器 P0 至 P7。P0 读出全一，写入无效果。"
            "当前 PTO 指令编码不直接选择这些寄存器；下述 Tile 操作使用各自明确定义的谓词载体。</p>"
            "<h2>比较结果如何交给后续操作</h2><p>TCMP 读取两个数值 Tile，TCMPS 读取一个数值 Tile 和一个标量。RowMajor 形式把比较结果写入打包谓词 Tile。逻辑索引 i 的结果位于第 ⌊i/8⌋ 个字节的第 i mod 8 位。TSEL 和 TSELS 可以消费这种谓词。</p>"
            '<p>对允许 CUBE_M16/M32 的比较形式，结果还可按各自的绑定要求写入 U8 PredicateCell 或 GPR。可用布局、类型和形状由具体操作决定。查阅 <a href="tile-tcmp.html">TCMP</a>、<a href="tile-tcmps.html">TCMPS</a>、<a href="tile-tsel.html">TSEL</a>、<a href="tile-tsels.html">TSELS</a>。</p>'
            '<p>相关定义　<a href="tile-mgather-mask.html">MGATHER_MASK</a> · '
            '<a href="tile-mscatter-mask.html">MSCATTER_MASK</a></p>'
        ),
    )

    system_names = {str(row["name"]) for row in registers["registers"]}
    required = {
        "CORE_STATE",
        "ECSTATE_ACRn",
        "EVBASE_ACRn",
        "TRAPNO_ACRn",
        "TRAPARG0_ACRn",
        "EBARG_BPC_CUR_ACRn",
        "EBARG_BPC_TGT_ACRn",
        "EBARG_TPC_ACRn",
        "EBARG_LRA_ACRn",
    }
    if not required <= system_names:
        raise ValueError("saved exception state inventory differs")
    pages["arch-privilege-switch.html"] = (
        "ACR 切换",
        _article(
            "<p>外部中断、同步异常和架构上下文请求通过当前 ACR 选择保存 bank 与入口。切换保存 CORE_STATE、BPC、TPC、BARG、异常编号和参数，"
            "异常入口使用目标 ACR 的 EVBASE_ACRn。</p>"
            "<p>ACRC 在路由预检通过后发出服务请求异常。ACRE 先检查完整的已保存上下文，再提交当前 SYS 块；成功时恢复该上下文并消费其有效标志。验证或提交失败时保留上下文。</p>"
            '<p>相关定义　<a href="op-acre.html">ACRE</a> · <a href="op-acrc.html">ACRC</a> · <a href="arch-ssr.html">系统寄存器表</a></p>'
        ),
    )
    pages["arch-exception-overview.html"] = (
        "异常保存与恢复",
        _article(
            "<p>同步故障在产生第一个禁止的架构效果前建立异常状态；异步中断在架构允许的边界进入。"
            "保存 bank 记录异常号、参数、当前块地址、目标地址、TPC、返回状态和需要恢复的块参数。</p>"
            '<p>相关定义　<a href="arch-exception-model.html">异常编号与入口</a> · <a href="arch-privilege-switch.html">ACR 切换</a> · <a href="arch-ssr.html">保存状态寄存器</a></p>'
        ),
    )

    audit: dict[str, dict[str, Any]] = {}
    for route, (_, body) in pages.items():
        record: dict[str, Any] = {
            "origin": "v0.59.2-reviewed-current-execution",
            "source_commit": commit,
            "body_sha256": sha256(body.encode()).hexdigest(),
        }
        if route == "arch-fixup.html":
            record["sources"] = {
                "sail-package/model/decode/decode.sail": sha256(
                    sail_decode
                ).hexdigest(),
                SAIL_EXECUTE_SOURCE: sha256(sail_execute).hexdigest(),
            }
        audit[route] = record
    return pages, audit, execution_review()


__all__ = [
    "IMPLEMENTATION_SOURCES",
    "SAIL_EXECUTE_SOURCE",
    "execution_review",
    "golden_execution_pages",
    "implementation_review",
]
