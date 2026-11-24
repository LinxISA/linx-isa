#!/usr/bin/env python3
"""Select reader material that remains active in the LinxISA 0.59.2 manual.

The 0.59.2 catalog retains the obsolete encodings so a decoder can identify
them.  That inventory must not make the older instruction and block tutorials
look like supported programming material.  This module keeps that editorial
selection separate from catalog filtering and from the Markdown renderer.
"""

from __future__ import annotations

from functools import lru_cache
import re
from typing import Any, Iterable, Mapping


OBSOLETE_STATE = "obsolete"

# These roots describe the retired two-level vector and memory-block model.
# Exact instruction articles are normally removed by catalog filtering.  The
# roots also cover family tutorials that have no one-to-one catalog row.
OBSOLETE_SOURCE_PARTS = (
    "/inst/misa_v/",
    "/blockIntro/vecinstrs/",
    "/blockIntro/vec_block/",
    "/blockIntro/mem_block/",
)

OBSOLETE_SOURCE_FILES = frozenset(
    {
        "docs/zh/isa/header/B.TEXT.md",
        "docs/zh/isa/header/BSTART.MPAR.md",
        "docs/zh/isa/header/BSTART.MSEQ.md",
        "docs/zh/isa/header/BSTART.VPAR.md",
        "docs/zh/isa/header/BSTART.VSEQ.md",
        "docs/zh/isa/header/C.BSTART.MPAR.md",
        "docs/zh/isa/header/C.BSTART.MSEQ.md",
        "docs/zh/isa/header/C.BSTART.VPAR.md",
        "docs/zh/isa/header/C.BSTART.VSEQ.md",
    }
)

# These phrases name the removed programming model even when a page does not
# spell one of its opcodes.  They are intentionally narrower than generic
# words such as "vector", "lane" or "block", which remain valid for Tile VEC.
OBSOLETE_CONCEPT = re.compile(
    r"分离块|向量数据块|访存数据块|(?:Decoupled|Memory|Vector)\s+Block|"
    r"(?<![A-Za-z0-9_.])(?:MSEQ|MPAR|VSEQ|VPAR)(?![A-Za-z0-9_.])",
    re.I,
)


ACTIVE_REPLACEMENTS = {
    "docs/zh/isa/arch/bisa.md": """# 块指令与生命周期

Linx 程序以块作为配置、提交和恢复边界。块头建立块类型、控制流参数以及本次操作需要的属性和资源绑定；块体中的标量指令按当前块类型检查适用性；`BSTOP` 或下一条 `BSTART` 形成提交边界。

## 当前块类型

- `BSTART.STD` 建立整型标量块。
- `BSTART.FP` 建立浮点标量块。
- `BSTART.SYS` 建立系统块。
- `BSTART.TEPL` 及其 `BSTART.VEC`、`BSTART.SFU` 规范别名选择 Tile VEC 或 SFU 操作。
- TLSU 和 CUBE 操作由各自的 Tile 操作块头选择。

Tile 块可以先登记 `B.DIM`、`B.DATR`、`B.IOR`、`B.IOT`、`B.IOS` 等配置与绑定。进入块体后，普通标量指令仍保持当前 Tile 块类型，并按该操作的适用条件执行。完整操作在提交边界读取已经登记的块头状态。

## 控制状态

`BPC` 记录当前块起点，`TPC` 指向当前块内的指令。块头中的转移类型决定下一个块地址；提交前产生的异常按当前块的恢复状态处理。具体目标计算和返回地址写回以对应块头指令页为准。
""",
    "docs/zh/isa/arch/branch.md": """# 块间控制流

块头决定当前块完成后的控制流。控制流参数在块头执行时记录，在块提交边界生效。

## 转移类型 {#branch}

- **FALL**：顺延到编码规定的下一块地址。
- **DIRECT**：使用 PC 相对的直接目标。
- **CALL**：选择调用目标。是否写入 `ra` 由具体块头形式决定。
- **COND**：根据块内设置的提交条件选择目标或顺延路径。
- **IND**：从架构寄存器状态读取间接目标。
- **ICALL**：组合间接目标与调用返回状态。
- **RET**：使用已保存的返回状态。

`HL.BSTART.CALL` 分别编码调用目标和返回目标。`L.BSTART.FP/STD CALL` 本身保留 `ra`；需要返回的代码须先用 `SETRET` 或 `C.SETRET` 建立返回地址。每个形式的 PC 基准、立即数字段和对齐要求见对应指令页。
""",
    "docs/zh/isa/arch/execute.md": """# 块指令执行模型

## 建立块

执行 `BSTART` 时，处理器结束上一块并初始化新的块描述符。块头命令在进入块体前登记维度、数据类型、标量寄存器和 Tile 绑定。相同属性被重复设置、绑定数量不合法或资源不可用时，必须在相应架构效果之前报告异常。

## 执行块体

第一条普通标量指令使块进入块体阶段。之后再执行块头配置命令会触发块控制异常，规范明确规定为零参与者的空操作除外。普通标量指令先按当前块类型检查适用性，再读取操作数和产生效果。Tile 操作的完整效果在提交时读取已经闭合的块描述符。

`TPC` 按成功执行的指令长度推进，`BPC` 保持当前块起点。T、U 临时队列和显式目的寄存器的发布顺序由具体指令定义。

## 提交与异常

`BSTOP` 或下一条 `BSTART` 形成提交边界。提交前先完成合法性、资源和地址预检；失败时按具体操作的异常规则保留或撤销效果。成功提交后，控制流使用块头记录的下一块目标继续执行。
""",
    "docs/zh/isa/arch/executemachine.md": """# 块指令执行机制

当前执行机制由块头配置阶段、标量块体阶段和提交阶段组成。块头配置写入当前块描述符；第一条普通标量指令关闭配置阶段；提交阶段执行 Tile 操作、发布结果并选择下一块地址。

配置、块体和提交共享同一个块身份。实现可以并行准备操作数或调度执行资源，但必须保持规范要求的操作数快照、异常先后和结果发布顺序。实现细节不得产生额外的架构寄存器、隐式累加器或软件可见入口。
""",
    "docs/zh/isa/arch/constraints.md": """# LinxISA 0.59.2 架构约束

## 块生命周期

块头配置只能在块体开始前执行。第一条普通标量指令关闭配置阶段；之后出现块头配置命令会触发块控制异常，规范声明为零参与者空操作的形式除外。`BSTOP` 或下一条 `BSTART` 形成提交边界。

Tile 操作的输入、目的、布局、类型、维度和资源绑定必须在第一个架构效果前完成检查。TLSU 和 CUBE 块按各自操作页定义合法性；它们的显式 Local、Shared Tile 绑定不继承旧的块结构限制。

## 状态与寄存器

- 每个 Tile 结果由一个显式目的产生，可以被零个或多个后续操作读取。
- `reuse` 和最后使用标记控制资源生命周期，不改变数据语义。
- T、U 是标量块内临时队列；Local、Shared Tile 的身份与大小由绑定命令定义。
- 带累加的矩阵操作读取显式 Local 输入 C，并写入显式目的 D。

## 指令合法性

每条指令只能在其发布定义允许的块类型中执行。操作数选择、别名、双目的写回顺序、访存对齐和异常原子性均以对应指令页为准。保留编码和未实现形式必须在读取操作数或产生架构效果前拒绝。
""",
    "docs/zh/isa/arch/exception.md": """# 中断和异常

中断是指令流水线外的异步事件，异常是当前指令检测到的同步事件。两者都通过当前 ACR 的路由状态选择处理入口，并保存恢复所需的块与指令位置。

## 块状态

成功执行的块在提交边界发布结果。异常指令按其定义保留或撤销效果，并把当前 BPC、TPC、BARG 和异常参数保存到发布版系统寄存器目录指定的位置。标量 T、U 或 Tile 数据是否由软件进一步保存，由异常处理环境决定。

## 异常与陷出

处理器在进入服务请求前记录异常号和参数，切换到目标 ACR，并从该 ACR 的异常基址开始执行。恢复时使用已保存的块地址、指令地址和块参数。主动修复路径只适用于规范明确允许接管的异常。
""",
    "docs/zh/isa/exception/acr_switch.md": """# ACR 切换

外部中断、同步异常以及 `ACRE`、`ACRC` 和系统调用块可以改变当前 ACR。切换同时更新异常路由、当前执行状态和后续取指位置。

## ACR_ENTER

`ACRE` 在块提交时请求进入目标 ACR。处理器检查目标关系，从目标上下文恢复 CSTATE、BPC 和按指令选择的 BARG 状态，再从恢复位置继续执行。

## SERVICE_REQUEST

`ACRC`、同步异常和异步中断可以发起服务请求。处理器把当前 CSTATE、BPC、TPC、BARG、异常号和参数保存到目标 ACR 的系统寄存器，随后清理当前块参数并把 BPC 设置为该 ACR 的异常入口。整个架构状态切换作为一个不可分割的过程完成。

浮点标志、异常号、参数和返回所需状态的具体字段以 0.59.2 系统寄存器目录及对应指令页为准。
""",
    "docs/zh/isa/register/common/intro.md": """# 架构状态

## 全局状态

全局状态包括通用寄存器、系统寄存器、程序计数、内存以及 Local、Shared Tile 状态。异常上下文保存恢复所需的块地址、指令地址和块参数。

## 块状态

每个活动块有独立的块描述符，记录块类型、下一块目标、维度、数据属性、标量绑定与 Tile 绑定。标量 T、U 队列提供块内临时结果。Tile 操作使用显式 Local 或 Shared 源和目的；带累加的操作显式读取累加源并写入显式目的。

## 状态提交

指令按各自定义读取源快照并发布结果。块头配置在进入块体前完成，Tile 操作在提交边界读取完整描述符。异常和恢复只使用规范列出的状态，不引入隐藏软件可见状态。
""",
    "docs/zh/isa/blockIntro/tlsu_block/intro.md": """# TLSU 数据搬运块

TLSU 在全局内存与 Tile 寄存器之间执行数据搬运、预取、gather、scatter、掩码访问和索引原子操作。每个操作由发布目录中的 TLSU Tile 选择器和完整块描述符确定。

## 配置与绑定

`BSTART.TLOAD`、`BSTART.TSTORE`、`BSTART.TMOV`、`BSTART.TPREFETCH` 及索引传输块头选择具体操作。`B.DIM` 给出有效形状，`B.DATR` 给出数据属性，`B.IOR` 绑定标量地址参数，`B.IOT` 或 `B.IOS` 绑定 Tile 源和目的。

## 执行边界

操作在产生第一个架构效果前完成块描述符、布局、类型、资源和地址预检。执行掩码未启用的位置不产生地址或内存效果。具体对齐、错误原子性、重复地址顺序和目标发布规则见每个 Tile 操作页。
""",
}


def obsolete_mnemonics(catalog: Mapping[str, Any]) -> frozenset[str]:
    """Return the exact obsolete mnemonic inventory from a 0.59.2 catalog."""
    rows = catalog.get("instructions")
    if not isinstance(rows, list):
        raise ValueError("catalog instructions must be a list")
    names = {
        str(row["mnemonic"])
        for row in rows
        if isinstance(row, dict)
        and row.get("architecture_status", {}).get("state") == OBSOLETE_STATE
    }
    if len(names) != 193:
        raise ValueError(f"expected 193 obsolete mnemonics, found {len(names)}")
    return frozenset(names)


def active_rows(catalog: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Return catalog rows that remain part of the programming manual."""
    rows = catalog.get("instructions")
    if not isinstance(rows, list):
        raise ValueError("catalog instructions must be a list")
    active = tuple(
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("architecture_status", {}).get("state") != OBSOLETE_STATE
    )
    if len(rows) - len(active) != 193:
        raise ValueError("manual row selection did not remove exactly 193 forms")
    return active


def _obsolete_pattern(names: Iterable[str]) -> re.Pattern[str]:
    # Longest first prevents a shorter family spelling from hiding a suffix.
    alternatives = "|".join(
        re.escape(name) for name in sorted(names, key=len, reverse=True)
    )
    return re.compile(rf"(?<![A-Za-z0-9_.])(?:{alternatives})(?![A-Za-z0-9_.])", re.I)


@lru_cache(maxsize=4)
def _cached_pattern(names: tuple[str, ...]) -> re.Pattern[str]:
    return _obsolete_pattern(names)


def source_mentions_obsolete(markdown: str, names: Iterable[str]) -> bool:
    """Whether prose or code names an obsolete catalog mnemonic."""
    ordered = tuple(sorted(set(names)))
    if not ordered:
        return False
    return bool(_cached_pattern(ordered).search(markdown))


def obsolete_mentions(text: str, names: Iterable[str]) -> tuple[str, ...]:
    """Return obsolete mnemonic and programming-model terms visible in text."""
    ordered = tuple(sorted(set(names)))
    hits = {
        match.group(0).upper()
        for match in (_cached_pattern(ordered).finditer(text) if ordered else ())
    }
    hits.update(match.group(0) for match in OBSOLETE_CONCEPT.finditer(text))
    return tuple(sorted(hits))


def _filter_mixed_markdown(text: str, names: Iterable[str]) -> str:
    """Drop conflicting prose, fences, table rows or list items locally."""
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.lstrip().startswith("```"):
            end = index + 1
            while end < len(lines) and not lines[end].lstrip().startswith("```"):
                end += 1
            end = min(end + 1, len(lines))
            block = "".join(lines[index:end])
            if not obsolete_mentions(block, names):
                kept.extend(lines[index:end])
            index = end
            continue
        if line.startswith(("|", "- ", "* ", "+ ")):
            if not obsolete_mentions(line, names):
                kept.append(line)
            index += 1
            continue
        if not line.strip() or re.match(r"^#{1,6}\s", line):
            kept.append(line)
            index += 1
            continue
        end = index + 1
        while (
            end < len(lines)
            and lines[end].strip()
            and not re.match(r"^#{1,6}\s", lines[end])
            and not lines[end].startswith(("|", "- ", "* ", "+ ", "```"))
        ):
            end += 1
        block = "".join(lines[index:end])
        if not obsolete_mentions(block, names):
            kept.extend(lines[index:end])
        index = end

    # Remove headings with no remaining body before the next same/higher-level
    # heading. Blank lines are ignored while deciding whether a body remains.
    changed = True
    while changed:
        changed = False
        for index, line in enumerate(kept):
            match = re.match(r"^(#{2,6})\s", line)
            if not match:
                continue
            level = len(match.group(1))
            body = False
            for candidate in kept[index + 1 :]:
                heading = re.match(r"^(#{1,6})\s", candidate)
                if heading and len(heading.group(1)) <= level:
                    break
                if candidate.strip() and not heading:
                    body = True
                    break
            if not body:
                kept.pop(index)
                changed = True
                break
    result = "".join(kept)
    return re.sub(r"\n{3,}", "\n\n", result).strip() + "\n" if result.strip() else ""


def active_markdown(
    path: str, markdown: str, obsolete_names: Iterable[str]
) -> str | None:
    """Return a coherent 0.59.2 article or None for a wholly retired topic."""
    if path in ACTIVE_REPLACEMENTS:
        revised = ACTIVE_REPLACEMENTS[path].strip() + "\n"
    else:
        normalized = "/" + path.replace("\\", "/").lstrip("/")
        if path in OBSOLETE_SOURCE_FILES or any(
            part in normalized for part in OBSOLETE_SOURCE_PARTS
        ):
            return None
        if not obsolete_mentions(markdown, obsolete_names):
            return markdown
        revised = _filter_mixed_markdown(markdown, obsolete_names)
    if not revised or obsolete_mentions(revised, obsolete_names):
        return None
    return revised


def source_is_active(path: str, markdown: str, obsolete_names: Iterable[str]) -> bool:
    """Return true when a tagged Chinese page is safe to bundle as guidance.

    A complete document is withheld when it teaches any retired mnemonic.  We
    deliberately avoid deleting individual table rows or code lines because
    that can leave a false or internally inconsistent explanation behind.
    """
    return active_markdown(path, markdown, obsolete_names) is not None


def active_architecture_pages(
    pages: Iterable[Any], source_text: Mapping[str, str], obsolete_names: Iterable[str]
) -> tuple[Any, ...]:
    """Filter authored chapters while retaining generated collection indexes."""
    selected = []
    for page in pages:
        path = getattr(page, "source_path", None)
        if path is None:
            selected.append(page)
            continue
        if path not in source_text:
            raise ValueError(f"missing architecture source text: {path}")
        if active_markdown(path, source_text[path], obsolete_names) is not None:
            selected.append(page)
    return tuple(selected)


def obsolete_source_paths(
    paths: Iterable[str], source_text: Mapping[str, str], obsolete_names: Iterable[str]
) -> tuple[str, ...]:
    """Return a stable audit inventory of source pages withheld from the manual."""
    return tuple(
        sorted(
            path
            for path in paths
            if not source_is_active(path, source_text[path], obsolete_names)
        )
    )


__all__ = [
    "OBSOLETE_SOURCE_FILES",
    "OBSOLETE_SOURCE_PARTS",
    "active_architecture_pages",
    "active_markdown",
    "active_rows",
    "obsolete_mentions",
    "obsolete_mnemonics",
    "obsolete_source_paths",
    "source_is_active",
    "source_mentions_obsolete",
]
