#!/usr/bin/env python3
"""Generate current SSR field and behavior descriptions from the locked register catalog."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from html import escape
import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping


PTO_COMMIT = "a89a53d48f5708328be609fe2e6296ac8bdb4bc2"
CATALOG_SOURCE = "isa/v0.59/state/pto_system_registers.json"
PTO_ROOT = f"https://github.com/PTO-ISA/pto-spec/blob/{PTO_COMMIT}/"
SYSTEM_REGISTER_SOURCE = "asl/arch/data-types/system-registers.asl"
ACCESS_SOURCE = "asl/scalar/model/sys/registers.asl"
BASE_SEMANTICS_SOURCE = "asl/scalar/model/sys/semantics.asl"
CORE_STATE_SOURCE = "asl/arch/state/numeric-status.asl"
ACR_SOURCE = "asl/arch/system-registers/access-control.asl"
TIMER_SOURCE = "asl/arch/system-registers/timer.asl"
INTERRUPT_SOURCE = "asl/arch/system-registers/interrupt.asl"
TRAP_SOURCE = "asl/arch/memory-model/fault-precision.asl"
TRAP_CONTEXT_SOURCE = "asl/arch/state/trap-context.asl"
MESSAGE_SOURCE = "asl/arch/state/message-buffer.asl"
MESSAGE_SEND_SOURCE = "asl/arch/state/message-buffer-send.asl"


_READ = {
    "stored-value": "读取保存值",
    "architectural-time": "读取架构时间",
    "fixed-value": "读取固定的 profile 值",
    "current-worker-launch-value-or-base": "有活动 worker 时读取启动几何，否则读取基础值",
    "executing-pe-index": "读取当前 Core 内执行 PE 的编号 0 至 3",
    "packed-trap-status": "读取打包的异常状态",
    "trap-argument-zero": "读取异常参数 0",
    "refresh-timer-then-pending-bitmap": "先刷新定时器状态，再读取待处理中断位图",
    "refresh-timer-then-lowest-pending-id": "先刷新定时器状态，再读取最低编号的待处理中断",
    "saved-context-value": "读取保存的执行上下文",
    "message-status": "读取消息状态",
    "message-snapshot": "读取当前 claim 的稳定快照",
    "message-config": "读取消息配置",
    "reject-write-only": "读取会引发非法指令故障",
}
_WRITE = {
    "store-value": "写入并保存完整 64 位值",
    "reject-read-only": "写入会引发非法指令故障",
    "unpack-trap-status": "把写入值解包到异常状态",
    "store-trap-argument-zero": "写入异常参数 0",
    "store-saved-context-value": "写入保存的执行上下文字段",
    "acknowledge-interrupt-id": "确认给定的 6 位中断编号",
    "message-staging": "写入当前上下文的私有发送暂存区",
    "message-command": "提交 claim、release 或 acknowledge 命令",
    "message-config": "写入或选择消息配置",
}
_RESET = {
    "zero": "0",
    "one": "1",
    "external-and-timer-enabled": "3（外部中断和定时器中断均使能）",
    "pto-model-max-tile-capacity-bytes": "PTO 模型规定的最大 Tile 容量（字节）",
}
_SIDE_EFFECT = {
    "write-selects-current-acr": "写入同时把 CORE_STATE[3:0] 选为当前 ACR",
    "advances-on-every-execution-attempt": "每次架构指令执行尝试推进一个时间单位",
    "launch-admission-binds-value": "worker 获准启动时绑定本次启动几何",
    "matching-done-restores-base-value": "匹配的 DONE 恢复基础值",
    "limits-per-tile-and-aggregate-allocation": "限制单个 Tile 和总 Tile 分配容量",
    "save-and-recovery-state": "参与异常保存与恢复",
    "selects-trap-entry-tpc": "非零值选择异常入口 TPC；零值退回故障地址",
    "reads-and-writes-trap-bank-fields": "读写打包的异常编号、原因和状态位",
    "reads-and-writes-trap-bank-argument": "读写异常参数 0",
    "controls-external-and-timer-trap-entry": "位 0、1 分别控制外部和定时器异常入口",
    "reflects-external-and-timer-pending-sources": "反映外部和定时器待处理源",
    "priority-derived-from-pending-bitmap": "返回待处理位图中编号最低的一项",
    "clears-selected-pending-id": "清除指定待处理中断编号",
    "clears-asynchronous-trap-status": "同时清除异步异常和参数有效状态",
    "identity-translation-does-not-consume-value": "当前恒等地址转换模型保存但不消费该值",
    "refreshes-timer-pending-state": "写入后立即刷新定时器待处理状态",
    "does-not-consume-value": "当前执行模型保存但不消费该值",
    "trap-save-clears-value": "异常保存时写零",
    "recovery-does-not-consume-value": "恢复路径当前不消费该值",
    "trap-save-preserves-value": "异常保存保持该值",
    "debug-matching-disabled": "当前 profile 不启用调试匹配",
    "marks-valid-snapshot-read": "成功读取后标记对应快照字已读",
    "writes-private-tx-staging": "写入当前上下文的私有发送暂存区",
    "updates-claim-or-ack": "更新 claim、release 或 acknowledge 状态",
    "selects-and-binds-message-context": "选择并绑定消息上下文",
    "aliases-architectural-time": "与 TIME、CYCLE 使用同一架构时间源",
}


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _anchor(name: str) -> str:
    return "ssr-" + _slug(name)


def _behavior_owners(document: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for behavior in document["behavior_classes"]:
        for name in behavior["registers"]:
            if name in result:
                raise ValueError(f"duplicate behavior owner for {name}")
            result[name] = behavior
    names = {str(row["name"]) for row in document["registers"]}
    if names != set(result):
        raise ValueError("system-register behavior coverage differs")
    return result


def _source_for(name: str) -> str:
    if name == "CORE_STATE":
        return CORE_STATE_SOURCE
    if name.startswith(("ECSTATE", "EVBASE", "EBARG")):
        return TRAP_CONTEXT_SOURCE
    if name.startswith(("TRAPNO", "TRAPARG")):
        return TRAP_SOURCE
    if name.startswith(("ECONFIG", "IPENDING", "TOPEI", "EOIEI")):
        return INTERRUPT_SOURCE
    if name.startswith(("TIMER_TIME", "TIMER_TIMECMP")):
        return TIMER_SOURCE
    if name in {
        "MSGBRXMSGID_HI",
        "MSGBRXMSGID_LO",
        "MSGBTXID_HI",
        "MSGBTXID_LO",
    }:
        return MESSAGE_SEND_SOURCE
    if name.startswith("MSGB"):
        return MESSAGE_SOURCE
    if name in {
        "THREAD_PTR",
        "GLOBAL_PTR",
        "TIME",
        "CYCLE",
        "THREAD_ID",
        "BLOCKNUM",
        "BLOCKID",
    }:
        return BASE_SEMANTICS_SOURCE
    if name in {
        "CORE_ID",
        "VENDOR",
        "VERSION",
        "CORE_FEATURE",
        "CORE_FEATURE_ENABLE",
        "TILE_CAPACITY",
    }:
        return ACCESS_SOURCE
    return ACCESS_SOURCE


def _evidence_for(name: str) -> tuple[str, ...]:
    result = {SYSTEM_REGISTER_SOURCE, ACCESS_SOURCE, _source_for(name)}
    if name == "CORE_STATE":
        result.update(
            {
                CORE_STATE_SOURCE,
                ACR_SOURCE,
                "asl/scalar/model/fsu/scalar-fp.asl",
                "asl/scalar/model/fsu/arithmetic.asl",
            }
        )
    if name.startswith("MSGB"):
        result.add(MESSAGE_SOURCE)
        result.add(MESSAGE_SEND_SOURCE)
    return tuple(sorted(result))


def _purpose(name: str, behavior: Mapping[str, Any]) -> str:
    exact = {
        "THREAD_PTR": "为软件保存当前线程的数据基址。架构把它定义为普通 64 位存储。",
        "GLOBAL_PTR": "为软件保存全局数据基址。架构把它定义为普通 64 位存储。",
        "TIME": "返回当前架构时间。每次架构指令执行尝试使该时间推进一。",
        "CYCLE": "返回与 TIME 相同的架构时间源，地址为 0x0C00。",
        "CORE_STATE": "保存当前 ACR、标量浮点舍入模式和累计数值状态；写入会切换当前 ACR。",
        "CORE_ID": "读取当前 profile 提供的固定 Core 标识值。",
        "VENDOR": "读取当前 profile 提供的固定供应商标识值。",
        "VERSION": "读取当前 profile 的版本标识；复位值为 1。",
        "CORE_FEATURE": "读取当前 profile 的固定特征值。当前机器记录没有为各个位分配功能名称。",
        "CORE_FEATURE_ENABLE": "保存软件写入的特征使能值。当前机器记录没有为各个位分配功能名称。",
        "THREAD_ID": "返回当前 Core 内正在执行本指令的 PE 编号 0 至 3。跨块、重试、异常和返回时保持该 PE 的身份。",
        "TILE_CAPACITY": "返回 PTO 模型允许的最大 Tile 容量，以字节计。",
        "BLOCKNUM": "有活动 worker 时返回该次启动绑定的 block 数；无任务时返回基础值。",
        "BLOCKID": "有活动 worker 时返回该次启动绑定的 block 编号；无任务时返回基础值。",
        "ECSTATE_ACRn": "保存异常来源的 CORE_STATE，并用位 3:0 记录源 ACR、位 4 记录异常是否发生在块体中。",
        "EVBASE_ACRn": "保存该 ACR 的异常入口。值为零时，异常入口使用故障地址；非零时使用本寄存器值。",
        "TRAPNO_ACRn": "以一个 64 位值打包异步标志、参数有效标志、24 位原因和 6 位异常编号。",
        "TRAPARG0_ACRn": "保存异常参数 0。具体参数类型由 TRAPNO 对应异常定义决定。",
        "ECONFIG_ACRn": "控制外部中断和定时器中断入口；复位值 3 使能二者。",
        "IPENDING_ACRn": "返回 64 位待处理中断位图；读取前刷新定时器待处理位。",
        "TOPEI_ACRn": "返回 IPENDING 中编号最低的待处理中断；没有待处理项时为零。",
        "EOIEI_ACRn": "写入低 6 位中断编号以清除对应待处理位，并清除异步异常状态。高位非零时不清除待处理位。",
        "TIMER_TIME_ACRn": "返回与 TIME、CYCLE 相同的架构时间源。",
        "TIMER_TIMECMP_ACRn": "保存定时器比较值。非零且架构时间达到该值时置位定时器中断；零值不产生该定时器待处理位。",
        "XBINFO_ACRn": "当前 profile 仅保存该 64 位值，执行模型不消费它。",
        "ACR_PARAM_ACRn": "当前 profile 仅保存该 64 位值，执行模型不消费它。",
    }
    if name in exact:
        return exact[name]
    if name.startswith("ETEMP"):
        return "保存异常处理软件使用的 64 位临时值。"
    if name.startswith("TTBR") or name in {
        "TCR_ACR1",
        "MAIR_ACR1",
        "IOTTBR_ACR1",
        "IOTCR_ACR1",
        "IOMAIR_ACR1",
    }:
        return "保存地址转换配置。当前 profile 使用恒等地址转换，不消费该值。"
    if name == "EBARG0_ACRn":
        return "保存异常恢复控制字，包括源 ACR、有效位、块活动状态、块类型、转移类型和 taken 状态。"
    if name.startswith("EBARG_BPC_CUR"):
        return "保存异常发生时的 BPC。"
    if name.startswith("EBARG_BPC_TGT"):
        return "保存异常发生时块描述符中的目标 BPC。"
    if name.startswith("EBARG_TPC"):
        return "保存异常发生指令的 TPC；恢复成功时写回 TPC。"
    if name.startswith("EBARG_LRA"):
        return "保存异常发生时的返回地址状态。"
    if re.match(r"EBARG_[TU]Q[0-3]_ACRn", name):
        return "保存对应 T/U 临时队列槽的 64 位值，供异常恢复使用。"
    if name in {"EBARG_LB_ACRn", "EBARG_LC_ACRn"}:
        return "保留的块内状态槽。异常保存写零，当前恢复路径不消费该值。"
    if name.startswith("EBARG_EXTCTX") or name == "EBARG_TPLFLAGS_ACRn":
        return "保存扩展上下文元数据。异常保存保持该值，当前恢复路径不消费它。"
    if name.startswith(("DBG", "DB", "DC", "DW")):
        return "保存调试配置或比较值；当前 profile 不启用调试匹配。"
    if name == "MSGBCR":
        return "返回最近一次成功发送接纳或精确重放的 control 字。失败或 control 改变的重试不会覆盖它。"
    if re.fullmatch(r"MSGBD(?:10|[1-9])", name):
        return (
            "写入当前上下文的私有发送暂存字；读取当前 claim 的稳定接收快照，并标记该字已读。"
            "空或不可访问的快照读取在目的寄存器和已读掩码改变前引发故障。"
        )
    if name == "MSGBRXCLAIM":
        return "写 0 不操作，写 1 尝试 claim；其他位非零返回 BAD_COMMAND，且不产生 claim 效果。"
    if name == "MSGBRXSTATE":
        return "返回 claim 结果、OWNED、ACKED 和有效字数。"
    if name == "MSGBRXTOKEN":
        return "返回 claim 专属 token：高 16 位是 RX epoch，低 48 位是 claim sequence；有效 token 的两部分都非零。"
    if name in {"MSGBRXMSGID_HI", "MSGBRXMSGID_LO", "MSGBRXCONTROL"}:
        return "返回当前 claim 的稳定消息身份或 control 快照；读取不会弹出消息。"
    if name == "MSGBRXRELEASE":
        return "写入完整 claim token 以释放对应快照。token、epoch、所有者和 claim 必须精确匹配。"
    if name == "MSGBACK":
        return "写入完整 claim token 以确认消息。只有 token、epoch、所有者和已读掩码全部通过时才弹出该消息。"
    if name == "MSGBACKSTAT":
        return "返回最近一次 ACK 的结果和 VALID 位；读取不会清除结果。"
    if name == "MSGBACKID":
        return "返回与 ACKSTAT 同一次尝试对应的完整 token。"
    if name in {"MSGBTXID_HI", "MSGBTXID_LO"}:
        return "返回最近一次成功发送接纳或精确重放的 transport ID。"
    if name == "MSGBTXSTAT":
        return "返回最近一次发送结果和 VALID 位。"
    if name == "MSGBENDPOINT":
        return "返回当前上下文绑定的 endpoint；编号不规定实现的物理拓扑。"
    if name == "MSGBCFGSEL":
        return "选择当前 PE 的目标 ACR bank；仅低 4 位有效，只允许 ACR0 配置。"
    if name == "MSGBCFG":
        return (
            "配置 ENABLE[0]、RX_EPOCH[31:16] 和 SOURCE_EPOCH[63:32]；位 15:1 必须为零。"
        )
    if name == "MSGBDOMAIN":
        return "保存所选 bank 的 64 位可信隔离域；首次绑定后不可改变。"
    return f"行为类别 {behavior['id']} 的系统寄存器。"


_FIELDS: dict[str, tuple[tuple[str, str], ...]] = {
    "CORE_STATE": (
        ("3:0", "当前 ACR；写入 CORE_STATE 时同步选择该 ACR"),
        ("36:32", "NV、DZ、OF、UF、NX 累计数值状态；数值操作按位 OR，不清除已有标志"),
        ("39:37", "标量浮点舍入：001=RTM、010=RTP、011=RTZ，其他编码=RNE"),
    ),
    "ECSTATE_ACRn": (
        ("3:0", "异常来源 ACR"),
        ("4", "异常发生时块体已开始"),
        ("36:32", "保存的 NV、DZ、OF、UF、NX"),
        ("39:37", "保存的标量浮点舍入编码"),
    ),
    "TRAPNO_ACRn": (
        ("63", "异步异常标志"),
        ("62", "TRAPARG0 有效标志"),
        ("47:24", "24 位异常 cause"),
        ("5:0", "6 位异常编号"),
    ),
    "ECONFIG_ACRn": (("0", "外部中断使能"), ("1", "定时器中断使能")),
    "EOIEI_ACRn": (("5:0", "待确认的中断编号；位 63:6 必须为零才清除该 pending 位"),),
    "EBARG0_ACRn": (
        ("3:0", "源 ACR"),
        ("4", "恢复图像有效"),
        ("5", "块活动"),
        ("6", "块体活动"),
        ("10:7", "块类型编码"),
        ("13:11", "转移类型编码"),
        ("14", "taken 状态"),
    ),
    "MSGBRXCLAIM": (("0", "0=无操作，1=claim；其他位必须为零"),),
    "MSGBRXSTATE": (
        ("7:0", "结果码"),
        ("8", "OWNED"),
        ("9", "ACKED"),
        ("15:12", "有效消息字数"),
    ),
    "MSGBRXTOKEN": (("63:48", "RX epoch"), ("47:0", "claim sequence")),
    "MSGBACKSTAT": (("7:0", "ACK 结果码"), ("8", "VALID")),
    "MSGBTXSTAT": (("7:0", "发送结果码"), ("8", "VALID")),
    "MSGBCFGSEL": (("3:0", "目标 ACR"), ("63:4", "必须为零")),
    "MSGBCFG": (
        ("0", "ENABLE"),
        ("15:1", "必须为零"),
        ("31:16", "RX epoch"),
        ("63:32", "source epoch"),
    ),
}


def _fields(name: str) -> tuple[tuple[str, str], ...]:
    if name in _FIELDS:
        return _FIELDS[name]
    if name in {"MSGBRXMSGID_HI", "MSGBTXID_HI"}:
        return (("63:32", "可信源 endpoint"), ("31:0", "源 epoch"))
    if name in {"MSGBRXMSGID_LO", "MSGBTXID_LO"}:
        return (("63:0", "发送 sequence"),)
    return ()


def register_routes(document: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(row["name"]): f"arch-ssr.html#{_anchor(str(row['name']))}"
        for row in document["registers"]
    }


def register_sections(document: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    """Render one directly addressable current-definition section per register."""
    if document.get("register_definition_count") != 100:
        raise ValueError("register detail view requires exactly 100 definitions")
    owners = _behavior_owners(document)
    sections = []
    records: dict[str, Any] = {}
    for row in document["registers"]:
        name = str(row["name"])
        behavior = owners[name]
        address = str(row.get("address", row.get("low_index")))
        key = f"{row['scope']}:{name}:{address}"
        effects = [_SIDE_EFFECT[value] for value in behavior["side_effects"]]
        behavior_text = (
            f"{_READ[behavior['read']]}；{_WRITE[behavior['write']]}；"
            f"复位值为 {_RESET[behavior['reset']]}"
            + ("；" + "；".join(effects) if effects else "")
        )
        if name.startswith("MSGB"):
            behavior_text += "；MSGB 寄存器不具有普通交换语义，SSRSWAP 在读取前拒绝"
        field_rows = _fields(name)
        fields_html = ""
        if field_rows:
            fields_html = (
                '<div class="table-scroll"><table><thead><tr><th>位</th><th>当前含义</th></tr></thead><tbody>'
                + "".join(
                    f"<tr><td><code>{escape(bits)}</code></td><td>{escape(meaning)}</td></tr>"
                    for bits, meaning in field_rows
                )
                + "</tbody></table></div>"
            )
        sources = _evidence_for(name)
        full_address = (
            f"完整地址按 <code>(ACR &lt;&lt; 12) | {escape(address)}</code> 形成。"
            "当前 profile 只允许 ACR0 访问 context-family、地址转换和调试寄存器。"
            if row["scope"] == "context-family" and not row.get("fixed_context")
            else "本寄存器固定属于 ACR1；当前 profile 只允许 ACR0 访问该配置。"
            if row.get("fixed_context") == 1
            else ""
        )
        if name.startswith("MSGB"):
            full_address = (
                "配置寄存器只允许 ACR0 访问。"
                if name in {"MSGBCFGSEL", "MSGBCFG", "MSGBDOMAIN"}
                else "操作寄存器要求当前 bank 已使能并绑定到活动 kernel invocation。"
            )
        sections.append(
            f'<section class="system-register-detail" id="{_anchor(name)}" data-register-detail-key="{escape(key, quote=True)}">'
            f"<h3><code>{escape(name)}</code></h3>"
            f"<p><strong>地址</strong> <code>{escape(address)}</code>　"
            f"<strong>访问</strong> <code>{escape(str(row['access']))}</code>　"
            f"<strong>作用域</strong> <code>{escape(str(row['scope']))}</code></p>"
            + (f"<p>{full_address}</p>" if full_address else "")
            + f"<p>{escape(_purpose(name, behavior))}</p>"
            + f"<p>{escape(behavior_text)}</p>"
            + fields_html
            + '<p class="source">当前架构来源　'
            + " · ".join(
                f'<a href="{PTO_ROOT}{source}">{escape(source.rsplit("/", 1)[-1])}</a>'
                for source in sources
            )
            + "</p>"
            + "</section>"
        )
        records[name] = {
            "anchor": _anchor(name),
            "key": key,
            "behavior_class": behavior["id"],
            "behavior_status": behavior["behavior_status"],
            "evidence": [CATALOG_SOURCE, *sources],
            "fields": [bits for bits, _ in field_rows],
        }
    if len(records) != 100:
        raise ValueError("register detail inventory differs")
    return "".join(sections), records


def register_evidence(document: Mapping[str, Any]) -> dict[str, Any]:
    """Record the catalog and upstream sources backing each current register."""
    _, records = register_sections(document)
    return {
        "schema": "linxisa.golden-ssr-evidence.v1",
        "pto_source_commit": PTO_COMMIT,
        "register_count": len(records),
        "catalog_content_sha256": sha256(
            json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "registers": records,
    }


_ASL_FACTS = {
    CORE_STATE_SOURCE: (
        "_SystemRegisters.core_state[36:32]",
        "NumericStatusFlags() OR flags",
    ),
    "asl/scalar/model/fsu/scalar-fp.asl": ("_SystemRegisters.core_state[39:37]",),
    "asl/scalar/model/fsu/arithmetic.asl": (
        "encoded == '001' then return NumericRound_RTM",
        "encoded == '010' then return NumericRound_RTP",
        "encoded == '011' then return NumericRound_RTZ",
        "else return NumericRound_RNE",
    ),
    ACR_SOURCE: ("_SystemRegisters.core_state[3:0] = AccessControlRingBits(ring)",),
    TRAP_SOURCE: (
        "value[63] = if _ACRTrapAsynchronous",
        "value[62] = if _ACRTrapArgumentValid",
        "value[24 +: 24] = _ACRTrapCause",
        "value[0 +: 6] = _ACRTrapNumber",
    ),
    TRAP_CONTEXT_SOURCE: (
        "ecstate[3:0] = AccessControlRingBits(source)",
        "ecstate[4] = if _BundleBodyActive",
        "control[10:7] = BundleKindCode",
        "control[13:11] = BundleTransferCode",
        "control[14] = if _BARG.taken",
    ),
    INTERRUPT_SOURCE: (
        "interrupt_config[1]",
        "interrupt_config[0]",
        "for interrupt_id = 0 to 63",
        "if value[63:6] == Zeros{58}",
    ),
    MESSAGE_SOURCE: (
        "command != Zeros{PTO_XLEN} + 1",
        "snapshot.token[63:48]",
        "snapshot.token[47:0]",
        "!MessageBufferReadComplete(index)",
        "ClearMessageBufferQueuedMessage(index)",
    ),
    MESSAGE_SEND_SOURCE: (
        "let id_hi = MessageBufferEndpointWord(source_index)[31:0] ::",
        "let id_lo = _MessageBufferBanks[[source_index]].transmit_sequence + 1",
        "tx_message_id_hi = id_hi",
        "tx_message_id_lo = id_lo",
    ),
    SYSTEM_REGISTER_SOURCE: (
        "MSGBRXSTATE (0x083c) reports result [7:0], OWNED[8], ACKED[9]",
        "MSGBCFG (0x084a) assigns ENABLE[0], RX_EPOCH[31:16]",
        "All MSGB SSRSWAP forms MUST reject before read-side effects",
    ),
}


def validate_asl_evidence(root: Path) -> list[str]:
    """Verify reader-visible field slices against the exact PTO checkout."""
    root = root.resolve()
    errors: list[str] = []
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"PTO source checkout unavailable: {exc}"]
    if commit != PTO_COMMIT:
        errors.append(f"PTO source HEAD {commit} != {PTO_COMMIT}")
    for relative, facts in _ASL_FACTS.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing PTO ASL evidence: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for fact in facts:
            if fact not in text:
                errors.append(f"{relative}: missing field evidence {fact!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pto-root", required=True, type=Path)
    args = parser.parse_args(argv)
    errors = validate_asl_evidence(args.pto_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: current SSR field details match the pinned PTO ASL sources")
    return 0


__all__ = [
    "register_evidence",
    "register_routes",
    "register_sections",
    "validate_asl_evidence",
]


if __name__ == "__main__":
    raise SystemExit(main())
