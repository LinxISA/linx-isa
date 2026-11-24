#!/usr/bin/env python3
"""Reproduce the continuity review of the 118 Chinese architecture source chapters."""

import argparse
from collections import Counter
from pathlib import Path
import json
import subprocess

from manual_architecture import architecture_pages
from manual_golden_datatypes import datatype_review
from manual_golden_execution import (
    execution_review,
    implementation_review,
    IMPLEMENTATION_SOURCES,
)
from manual_golden_registers import register_review
from manual_v0592_edition import CATALOG, COMMIT, read
from manual_tag import REPO_ROOT, REVIEWED_COMMIT

REPORT = REPO_ROOT / "docs/architecture/research/v0.59.2-design-continuity.md"
PTO = (
    "https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/"
)
LINX = "https://github.com/LinxISA/linx-isa/blob/" + COMMIT + "/"
STATE = "isa/v0.59/state/"
BRANCH = "asl/scalar/model/dispatch/top-level.asl"


def prior(path):
    return subprocess.check_output(
        ["git", "show", f"{REVIEWED_COMMIT}:{path}"], cwd=REPO_ROOT
    )


def check_catalogs():
    old = json.loads(prior("isa/v0.59/linxisa-v0.59.json"))
    new = json.loads(read(CATALOG))
    previous = {row["id"]: row for row in old["instructions"]}
    current = {row["id"]: row for row in new["instructions"]}
    if previous.keys() != current.keys() or len(previous) != 1499:
        raise ValueError("release form identity mismatch")
    states = Counter()
    for identity, row in current.items():
        if {k: v for k, v in row.items() if k != "architecture_status"} != previous[
            identity
        ]:
            raise ValueError(f"release definition differs for {identity}")
        states[row.get("architecture_status", {}).get("state", "pto")] += 1
    if states != {
        "pto": 1283,
        "obsolete": 193,
        "retained": 19,
        "reserved-unimplemented": 4,
    }:
        raise ValueError(f"unexpected release status counts {states}")
    for name in (
        "pto_scalar_forms",
        "pto_command_forms",
        "pto_tile_operations",
        "pto_system_registers",
        "extension_encoding_reservations",
        "pto_hardware_numeric_vectors",
        "pto_hardware_conformance_profile",
    ):
        path = STATE + name + ".json"
        if prior(path) != read(path):
            raise ValueError(f"release input changed: {path}")


def report():
    check_catalogs()
    chapters = {p.source_path: p for p in architecture_pages() if p.source_path}
    registers = {
        r["source"]: r
        for r in register_review(json.loads(read(STATE + "pto_system_registers.json")))
    }
    types = datatype_review()
    exe = execution_review()
    impl = implementation_review(
        COMMIT, {p: read(p) for p in IMPLEMENTATION_SOURCES.values()}
    )
    if (
        len(chapters) != 118
        or not registers.keys() <= chapters.keys()
        or not types.keys() <= chapters.keys()
    ):
        raise ValueError("earlier chapter inventory or review inputs differ")
    lines = [
        "# LinxISA v0.59.2 设计延续性核对",
        "",
        "核对基线为签名标签 v0.59.1 与 v0.59.2，以及两版共同锁定的 PTO 提交 `a89a53d48f57`。每项判断区分编码、行为、软件可见状态和实现选择。正文采用能够由本版证据确认的设计；仅有名称相同或来源年代较早，都不足以判定该设计的去留。",
        "",
        "## 发布差异与影响",
        "",
        "- 按 form ID 对比全部 1,499 条记录。除新增的架构状态外，汇编、固定位、字段、约束及原有语义记录逐项相同。193 个编码形式标为 obsolete，19 个 Linx 形式继续保留，4 个仅预留编码。另有 1,283 个 PTO 共有形式。",
        "- 两版的标量、块命令、Tile、SSR、扩展预留、硬件数值符合性配置与数值向量共七份输入逐字节相同。保留项可沿已有定义查证；从 v0.58 或更早文档引用的具体位号、类型和操作仍需核对。[机器目录]("
        + LINX
        + CATALOG
        + ") · [编码状态裁决]("
        + LINX
        + "docs/zh/architecture/linx-two-level-block-obsolescence.md)",
        "- 谓词设计须区分三个层面：PTO 状态模型定义 P0–P7，但该模型明确没有直接消费这组寄存器的指令编码；RowMajor 打包谓词、CUBE PredicateCell 和 GPR 掩码仍有具体 Tile 消费者；Linx 二级执行模型的 lane 状态另有其模型用途。编码裁决没有给所有相关状态新增硬件禁令。[谓词状态]("
        + PTO
        + "asl/arch/programming-model/predicate-registers.asl) · [TCMP]("
        + PTO
        + "asl/tile/elementwise-tile-tile/logical/TCMP.asl)",
        "- 汇编备注另外逐条比对：38 个基础整数和 15 个长立即数形式保留可执行于 Tile 标量块体的规则；16 个压缩形式保留 16 位编码说明；4 个 MIN/MAX 形式按整数比较与适用性规则修正。没有将旧页里的可选扩展开关或‘只能在浮点块执行’推广成全局限制。[标量块体入口]("
        + PTO
        + BRANCH
        + ") · [适用性检查]("
        + PTO
        + "asl/scalar/model/sys/semantics.asl)",
        "",
        "## 架构、执行与系统",
        "",
        "| 原主题 | 核对结果 | 当前依据或手册入口 |",
        "| --- | --- | --- |",
    ]
    seen = set()
    for path, c in chapters.items():
        if path in registers or path in types or c.key in impl:
            continue
        info = exe[c.key]
        route = {
            "predicate": "arch-tile-masks.html",
            "core-state": "arch-ssr.html#ssr-core-state",
        }.get(c.key, c.route)
        if c.key in {"vgpr", "execution-mode", "memory-block", "vector-block"}:
            ref = (
                "[编码裁决]("
                + LINX
                + "docs/zh/architecture/linx-two-level-block-obsolescence.md) · [Sail 状态]("
                + LINX
                + "isa/sail/model/state/state.sail)"
            )
        else:
            ref = "`" + route + "`"
        lines.append(f"| [{c.title}]({LINX}{path}) | {info['evidence']} | {ref} |")
        seen.add(path)
    lines += [
        "",
        "## 寄存器及其字段",
        "",
        "逐项比较了 41 篇寄存器来源，其中寄存器访问概述也在架构状态分组下出现。复用槽位不能单凭地址推断行为；读写、复位、字段切片和访问范围以当前行为类及执行函数核对。",
        "",
        "| 原来源 | 当前寄存器或分组 | 核对结果 | 依据 |",
        "| --- | --- | --- | --- |",
    ]
    for path, r in sorted(registers.items()):
        names = r["current_registers"]
        dest = (
            "、".join(names)
            if len(names) < 9
            else f"{len(names)} 项；按当前寄存器表查阅"
        )
        ref = next((e for e in r["evidence"] if e.startswith("asl/")), None)
        lines.append(
            f"| [{Path(path).stem}]({LINX}{path}) | {dest or '见核对结果'} | {r['reason']} | "
            + (
                f"[ASL]({PTO}{ref})"
                if ref
                else f"[SSR 目录]({LINX}{STATE}pto_system_registers.json)"
            )
            + " |"
        )
        seen.add(path)
    lines += [
        "",
        "## 数值格式、载体与操作适用性",
        "",
        "| 原格式主题 | 核对结果 | 权威定义 |",
        "| --- | --- | --- |",
    ]
    for path, r in sorted(types.items()):
        refs = " · ".join(f"[{Path(e).stem}]({PTO}{e})" for e in r["authority"])
        lines.append(f"| [{Path(path).stem}]({LINX}{path}) | {r['reason']} | {refs} |")
        seen.add(path)
    lines += [
        "",
        "## 实现资料",
        "",
        "以下十二篇资料可用于核对设计机制。本次架构决策没有废弃对应流水线、预测器或队列设计。其实现参数不自动成为对所有 Linx 处理器的架构要求；这里也不据此宣称 RTL 已验证。",
        "",
        "| 设计资料 | 固定版本记录的机制与适用边界 |",
        "| --- | --- |",
    ]
    for r in impl.values():
        lines.append(f"| [{r['title']}]({r['source_url']}) | {r['summary']} |")
        seen.add(r["source_path"])
    if seen != chapters.keys():
        raise ValueError(f"review coverage differs: {seen ^ chapters.keys()}")
    lines += [
        "",
        "## 附属参考资料",
        "",
        "- 伪代码中的整数解释、移位、扩展、取反及 Reg5 读写继续提供。系统寄存器含义与地址以 100 项 SSR 及其字段页为准。",
        "- 编码格式按 16、32、48、64 位分别说明。按已发布形式检查当前操作数、位域和块体条件；相同长度不保证相同适用性。",
        "- 原目录的四个 TC 文件实际以 TLB.IA、TLB.IALL、TLB.IAV、TLB.IV 为标题；对应页面按这四个现行助记符查阅。数据和指令同步分别对照 FENCE.D、FENCE.I 的正式作用域及效果，未推导 DSB/ISB 是现行拼写或可逐字替换的编码别名。块提交条件见 SETC 家族，OPE 和 IFU 资料按实现边界归档。",
        "",
        "从仓库根目录运行 `python3 tools/isa/review_v0592_design_continuity.py --check` 可复核两个标签与本文覆盖范围。",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    check = parser.parse_args().check
    text = report()
    if check:
        if not REPORT.exists() or REPORT.read_text() != text:
            raise SystemExit(f"stale continuity report: {REPORT}")
        print("OK: 1,499 forms and all 118 prior architecture sources reviewed")
    else:
        REPORT.write_text(text, encoding="utf-8")
