#!/usr/bin/env python3
"""Curated first-class architecture/state/execution chapters for the offline manual."""

from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from html import escape
import re
import subprocess
from manual_markdown import MarkdownFragment, render_article
from manual_tag import REPO_ROOT, REVIEWED_COMMIT, tagged_bytes, tagged_json


@dataclass(frozen=True)
class SystemRegisterRecord:
    key: str
    name: str
    address: str
    access: str
    scope: str
    historical_source: str | None
    historical_route: str | None


@dataclass(frozen=True)
class ArchitecturePage:
    key: str
    route: str
    title: str
    collection: str
    summary: str
    source_path: str | None = None
    status: str = "tagged-original"
    version_note: str = "发布 tag 中的中文架构原文；涉及编码时以 0.59.1 目录为准。"
    illustration: str | None = None


_CHAPTERS = (
    # Execution model and block lifetime.
    (
        "block-isa",
        "块指令与生命周期",
        "execution",
        "程序以 block 为提交和恢复边界；本章说明块头、块体、结束和跨块控制状态。",
        "docs/zh/isa/arch/bisa.md",
        "block-lifecycle",
    ),
    (
        "branch",
        "块间控制流",
        "execution",
        "说明 fall-through、直接/条件跳转、调用、返回及目标状态之间的关系。",
        "docs/zh/isa/arch/branch.md",
        "block-control-flow",
    ),
    (
        "execution",
        "执行模型",
        "execution",
        "从架构视角说明指令如何进入 block、读取状态、产生效果并在边界提交。",
        "docs/zh/isa/arch/execute.md",
        "execution-overview",
    ),
    (
        "execution-machine",
        "执行机制",
        "execution",
        "解释前端、执行资源、队列和 block 控制如何协同推进。",
        "docs/zh/isa/arch/executemachine.md",
        "execution-pipeline",
    ),
    (
        "execution-mode",
        "块体执行方式",
        "execution",
        "比较不同 block 类型和并行/顺序执行方式的架构含义。",
        "docs/zh/isa/arch/executemode.md",
        "block-modes",
    ),
    (
        "program-order",
        "程序序与可见性",
        "execution",
        "汇总程序序、效果先后和跨 block 可见性；内存细节以当前内存模型来源为准。",
        "docs/zh/isa/arch/prgorder.md",
        "program-order",
    ),
    (
        "fixup",
        "主动修复",
        "execution",
        "说明 fixup 入口、恢复状态和重新执行边界。",
        "docs/zh/isa/arch/fixup.md",
        "fixup-flow",
    ),
    (
        "constraints",
        "指令集约束",
        "execution",
        "列出实现和软件必须共同满足的架构约束。",
        "docs/zh/isa/arch/constraints.md",
        None,
    ),
    (
        "std-block",
        "整型标量 Block",
        "execution",
        "说明整型标量 block 的块头、块体和提交方式。",
        "docs/zh/isa/blockIntro/std_block/intro.md",
        None,
    ),
    (
        "sys-block",
        "系统 Block",
        "execution",
        "说明系统操作所在 block 的状态和执行边界。",
        "docs/zh/isa/blockIntro/sys_block/intro.md",
        None,
    ),
    (
        "fp-block",
        "浮点标量 Block",
        "execution",
        "说明浮点 block 的类型、属性和执行范围。",
        "docs/zh/isa/blockIntro/fp_block/intro.md",
        None,
    ),
    (
        "memory-block",
        "访存数据 Block",
        "execution",
        "说明访存 block 的分组、地址参数和数据流。",
        "docs/zh/isa/blockIntro/mem_block/intro.md",
        "memory-block-flow",
    ),
    (
        "cube-block",
        "矩阵数据 Block",
        "execution",
        "说明 CUBE block 的矩阵描述符和操作数组织。",
        "docs/zh/isa/blockIntro/cube_block/intro.md",
        "cube-block-shape",
    ),
    (
        "tlsu-block",
        "TLSU 数据搬运 Block",
        "execution",
        "说明 Tile 访存与数据搬运 block 的职责。",
        "docs/zh/isa/blockIntro/tlsu_block/intro.md",
        "tlsu-block-flow",
    ),
    (
        "tepl-carrier",
        "TEPL 编码载体",
        "execution",
        "说明 VEC/SFU 操作共用的 Mode/Function 编码载体；TEPL 不是执行引擎。",
        "docs/zh/isa/blockIntro/tepl_block/intro.md",
        None,
    ),
    (
        "xb-block",
        "系统调用 Block",
        "execution",
        "说明 XB block 的调用边界和上下文参数。",
        "docs/zh/isa/blockIntro/xb_block/intro.md",
        None,
    ),
    # Architectural state.
    (
        "register-state",
        "架构寄存器总览",
        "state",
        "建立通用、局部、向量、Tile、谓词和 block 状态的整体视图。",
        "docs/zh/isa/register/common/intro.md",
        "register-state-map",
    ),
    (
        "ggpr",
        "通用寄存器 GGPR",
        "state",
        "说明全局标量寄存器的命名、可见范围和操作数角色。",
        "docs/zh/isa/register/common/ggpr.md",
        None,
    ),
    (
        "sgpr",
        "标量寄存器 SGPR",
        "state",
        "说明标量执行上下文使用的寄存器状态。",
        "docs/zh/isa/register/common/sgpr.md",
        None,
    ),
    (
        "tile-registers",
        "Tile 寄存器",
        "state",
        "说明 Tile 身份、描述符、容量和 Local/Shared 使用边界。",
        "docs/zh/isa/register/common/tilereg.md",
        "tile-state-lifetime",
    ),
    (
        "predicate",
        "谓词寄存器",
        "state",
        "说明谓词状态如何控制逐 lane 或逐元素效果。",
        "docs/zh/isa/register/common/pred.md",
        None,
    ),
    (
        "barg",
        "Block 参数 BARG",
        "state",
        "说明 block 转移、目标和参数状态。",
        "docs/zh/isa/register/common/barg.md",
        "block-state",
    ),
    (
        "bpc",
        "Block PC",
        "state",
        "说明 block 控制流使用的程序计数状态。",
        "docs/zh/isa/register/common/bpc.md",
        None,
    ),
    (
        "tpc",
        "指令 TPC",
        "state",
        "说明当前指令位置和 PC-relative 语义使用的基址状态。",
        "docs/zh/isa/register/common/tpc.md",
        None,
    ),
    (
        "loop",
        "循环状态",
        "state",
        "说明架构循环寄存器与 block 执行的关系。",
        "docs/zh/isa/register/common/loop.md",
        None,
    ),
    (
        "ltar",
        "局部目标寄存器 LTAR",
        "state",
        "说明局部目标地址状态及其使用范围。",
        "docs/zh/isa/register/common/ltar.md",
        None,
    ),
    (
        "ssr",
        "系统寄存器总览",
        "state",
        "介绍 SSR 地址空间、访问类别和软件可见状态。",
        "docs/zh/isa/register/ssr/ssrintro.md",
        "ssr-map",
    ),
    # Privilege, exception, and memory-facing context.
    (
        "acr",
        "访问控制环 ACR",
        "system",
        "说明执行上下文、访问控制环和架构状态隔离。",
        "docs/zh/isa/arch/acr.md",
        "acr-contexts",
    ),
    (
        "privilege",
        "运行特权级",
        "system",
        "说明 ACR 内的运行权限和受控资源。",
        "docs/zh/isa/exception/acr.md",
        None,
    ),
    (
        "privilege-switch",
        "特权级切换",
        "system",
        "说明受控切换的入口、保存状态和恢复条件。",
        "docs/zh/isa/exception/acr_switch.md",
        "privilege-transition",
    ),
    (
        "exception-model",
        "异常模型",
        "system",
        "说明异常分类、保存状态、入口和返回流程。",
        "docs/zh/isa/exception/exception.md",
        "exception-lifecycle",
    ),
    (
        "interrupts",
        "中断",
        "system",
        "说明中断挂起、选择、入口和完成状态。",
        "docs/zh/isa/exception/interrupt.md",
        "interrupt-flow",
    ),
    (
        "timer",
        "通用定时器",
        "system",
        "说明定时器状态和定时中断接口。",
        "docs/zh/isa/timer.md",
        None,
    ),
    (
        "memory-context",
        "存储系统背景",
        "system",
        "提供缓存、访存通路和一致性背景；这是实现导读，不替代 0.59.1 指令语义。",
        "docs/zh/memory/overview.md",
        "memory-hierarchy",
    ),
)

_COLLECTIONS = {
    "execution": (
        "execution-model.html",
        "执行模型与 Block 生命周期",
        "block 结构、控制流、程序序和修复路径共同定义程序的执行过程。",
    ),
    "state": (
        "arch-state.html",
        "架构状态",
        "本组章节包括标量、向量、Tile、谓词、程序计数和系统寄存器。",
    ),
    "system": (
        "arch-system.html",
        "异常、权限与存储背景",
        "本组章节说明 ACR、特权切换、异常中断和存储系统接口。",
    ),
    "ssr": (
        "arch-ssr.html",
        "系统寄存器原文",
        "旧中文寄存器页按类别收录；地址、访问权限和 scope 以 0.59.1 目录为准。",
    ),
    "datatype": (
        "arch-datatypes.html",
        "数据类型",
        "整数、浮点、低精度和 microscaling 数据类型。",
    ),
    "implementation": (
        "arch-model-notes.html",
        "实现模型补充",
        "实现模型和微架构背景，不构成 ISA 行为承诺。",
    ),
}

_VERSION_GAPS = {
    "cube-block": "正文按 v0.58 解释显式 Local 目的 Tile；0.59.1 的具体 CUBE selector、类型和形状限制以当前 Tile operation 目录为准。",
    "tlsu-block": "正文列举 v0.58 TLSU 操作和内存模型；0.59.1 增补的 operation 与约束以当前目录和对应指令页为准。",
    "tepl-carrier": "正文引用 v0.58 pto_ops.json；本手册使用 0.59.1 的 79 个已发布 TEPL selector，旧路径只用于解释载体结构。",
    "exception-model": "正文保留 v0.55 拼写勘误和当时尚未发布的 v0.58 首次使用路由说明；0.59.1 的异常编码与 Sail 行为以当前发布源为准。",
}


def _slug_route(key: str) -> str:
    return "arch-ssr-overview.html" if key == "ssr" else f"arch-{key}.html"


@lru_cache(maxsize=None)
def _tagged_paths(prefix: str) -> tuple[str, ...]:
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", REVIEWED_COMMIT, prefix],
        cwd=REPO_ROOT,
        text=True,
    )
    return tuple(path for path in out.splitlines() if path.endswith(".md"))


def _extra_pages(existing: set[str]) -> list[ArchitecturePage]:
    result = [
        ArchitecturePage(
            "core-state",
            "arch-core-state.html",
            "核心状态",
            "state",
            "说明核心可见状态及其组成。",
            "docs/zh/isa/arch/corestate.md",
        ),
        ArchitecturePage(
            "arch-exception",
            "arch-exception-overview.html",
            "架构异常概览",
            "system",
            "说明架构异常类别和入口状态。",
            "docs/zh/isa/arch/exception.md",
        ),
    ]
    for prefix, collection, label in (
        ("docs/zh/isa/register/common", "state", "寄存器"),
        ("docs/zh/isa/register/ssr", "ssr", "系统寄存器历史说明"),
        ("docs/zh/isa/datatype", "datatype", "数据类型"),
        ("docs/zh/isa/model", "implementation", "实现模型"),
    ):
        for path in _tagged_paths(prefix):
            if path in existing:
                continue
            if path in {
                "docs/zh/isa/register/common/vgpr.md",
                "docs/zh/isa/blockIntro/vec_block/intro.md",
            }:
                continue
            stem = path.rsplit("/", 1)[-1].removesuffix(".md")
            key = f"{collection}-{stem.lower().replace('_', '-')}"
            status = (
                "implementation-only"
                if collection == "implementation"
                else "historical-register-note"
                if collection == "ssr"
                else "tagged-original"
            )
            note = (
                "实现材料；不得据此增加 ISA 承诺。"
                if collection == "implementation"
                else "旧中文说明；规范值以 0.59.1 机器目录为准。"
                if collection == "ssr"
                else "发布 tag 中文原文。"
            )
            result.append(
                ArchitecturePage(
                    key,
                    _slug_route(key),
                    stem,
                    collection,
                    f"{label}章节：{stem}。",
                    path,
                    status,
                    note,
                )
            )
    return result


def architecture_pages() -> tuple[ArchitecturePage, ...]:
    pages = [
        ArchitecturePage(
            "architecture",
            "architecture.html",
            "架构与执行模型",
            "index",
            "按执行模型、架构状态和系统边界组织原始中文章节。",
            version_note="页面正文来自 LinxISA 0.59.1 发布 tag；旧页面中的版本化编码须与当前目录交叉核对。",
        )
    ]
    for collection, (route, title, summary) in _COLLECTIONS.items():
        pages.append(
            ArchitecturePage(f"{collection}-index", route, title, "index", summary)
        )
    for key, title, collection, summary, path, illustration in _CHAPTERS:
        status = (
            "contextual-original"
            if path.startswith("docs/zh/memory/")
            else "tagged-original"
        )
        note = _VERSION_GAPS.get(key) or (
            "实现背景材料；不作为 0.59.1 规范替代。"
            if status == "contextual-original"
            else "发布 tag 中的中文原文；编码、保留值和 Tile 规则以 0.59.1 机器目录为准。"
        )
        pages.append(
            ArchitecturePage(
                key,
                _slug_route(key),
                title,
                collection,
                summary,
                path,
                status,
                note,
                illustration,
            )
        )
    pages.extend(_extra_pages({page.source_path for page in pages if page.source_path}))
    if len({page.route for page in pages}) != len(pages):
        raise ValueError(
            "architecture chapter and collection route names must be disjoint"
        )
    return tuple(pages)


def architecture_routes() -> dict[str, str]:
    return {
        page.source_path: page.route
        for page in architecture_pages()
        if page.source_path
    }


def architecture_collections() -> dict[str, tuple[ArchitecturePage, ...]]:
    pages = architecture_pages()
    return {
        key: tuple(page for page in pages if page.collection == key)
        for key in _COLLECTIONS
    }


def render_architecture_page(
    page: ArchitecturePage, *, document_routes: dict[str, str] | None = None
) -> MarkdownFragment | None:
    if page.source_path is None:
        return None
    routes = architecture_routes()
    routes.update(document_routes or {})
    return render_article(
        page.source_path, current_page=page.route, document_routes=routes
    )


def validate_architecture_sources() -> list[str]:
    errors = []
    routes = architecture_routes()
    if len(routes) != len(set(routes.values())):
        errors.append("architecture routes are not unique")
    for page in architecture_pages():
        if not re.search(r"[\u4e00-\u9fff]", page.summary):
            errors.append(f"{page.key}: summary is not Chinese")
        if page.source_path:
            if any(
                token in page.source_path
                for token in ("/archive/", "/generated/", "/instructions/")
            ):
                errors.append(f"{page.key}: generated/archive source selected")
            try:
                text = tagged_bytes(page.source_path).decode("utf-8")
                if not text.strip():
                    errors.append(f"{page.key}: empty source")
            except Exception as exc:
                errors.append(f"{page.key}: missing source: {exc}")
    return errors


def silicon_canvas_targets() -> tuple[ArchitecturePage, ...]:
    return tuple(page for page in architecture_pages() if page.illustration)


def _historical_register_source(name: str) -> str | None:
    aliases = {
        "THREAD_PTR": "TP",
        "GLOBAL_PTR": "GP",
        "CORE_STATE": "CSTATE",
        "CORE_FEATURE": "LCFR",
        "CORE_FEATURE_ENABLE": "LCFR_EN",
    }
    stem = re.sub(r"\d+$", "", name.removesuffix("_ACRn"))
    stem = aliases.get(stem, stem)
    if stem.startswith("EBARG"):
        stem = "EBARG"
    if stem.startswith("MSGB"):
        stem = "MSGB"
    candidates = {
        p.rsplit("/", 1)[-1].removesuffix(".md").upper(): p
        for p in _tagged_paths("docs/zh/isa/register/ssr")
    }
    return candidates.get(stem.upper())


def register_catalog_records() -> tuple[SystemRegisterRecord, ...]:
    routes = architecture_routes()
    result = []
    for row in tagged_json("isa/v0.59/state/pto_system_registers.json")["registers"]:
        address = str(row.get("address") or row.get("low_index"))
        source = _historical_register_source(str(row["name"]))
        result.append(
            SystemRegisterRecord(
                f"{row['scope']}:{row['name']}:{address}",
                str(row["name"]),
                address,
                str(row["access"]),
                str(row["scope"]),
                source,
                routes.get(source) if source else None,
            )
        )
    return tuple(result)


def register_catalog_html(allowed_routes=None) -> str:
    rows = []
    for item in register_catalog_records():
        old = (
            f'<a href="{escape(item.historical_route)}">历史说明</a>'
            if item.historical_route and (allowed_routes is None or item.historical_route in allowed_routes)
            else "—"
        )
        rows.append(
            f'<tr data-register-key="{escape(item.key, quote=True)}"><td><code>{escape(item.name)}</code></td><td><code>{escape(item.address)}</code></td><td>{escape(item.access)}</td><td>{escape(item.scope)}</td><td>{old}</td></tr>'
        )
    return (
        '<table class="system-register-catalog"><thead><tr><th>名称</th><th>地址/低位索引</th><th>访问</th><th>作用域</th><th>旧中文页</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>"
    )


__all__ = [
    "ArchitecturePage",
    "architecture_pages",
    "architecture_routes",
    "architecture_collections",
    "render_architecture_page",
    "validate_architecture_sources",
    "silicon_canvas_targets",
    "SystemRegisterRecord",
    "register_catalog_records",
    "register_catalog_html",
]
