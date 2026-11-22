"""Reader-facing copy edits reviewed against the pinned humanizer-zh guidance.

These are literal edits to observed prose, not a word blacklist or an
authorship detector. The tagged Markdown, code, links and table data remain
available unchanged. Only ordinary paragraph/list text can take an edit.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import re

from manual_tag import tagged_bytes

SKILL_COMMIT = "f4518a8eab97b8bfebc66a89d34320a89bef6930"
SKILL_SHA256 = "95627fd4437d886f98032ccc62d79136e6310f1fc04e354bb86431795ff206df"
SKILL_URL = f"https://github.com/op7418/humanizer-zh/blob/{SKILL_COMMIT}/SKILL.md"


@dataclass(frozen=True)
class Edit:
    key: str
    before: str
    after: str
    source: str = ""


# Preserve optionality, bit widths, assignment order and the distinction
# between permission to release a register and an actual hardware release.
EDITS = (
    Edit(
        "source-range",
        "可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果",
        "可选择全局寄存器 R0-R23，也可读取 T 队列或 U 队列中前序 1-4 条指令的输出结果",
    ),
    Edit("destination-range", "可以索引全局寄存器R1-R23", "可选择全局寄存器 R1-R23"),
    Edit(
        "queue-destination",
        "分别表示块内的T和U寄存器队列",
        "分别表示块内的 T 队列和 U 队列",
    ),
    Edit(
        "destination-selector",
        "表示三种可选的目的寄存器，编码于RegDst域。其中：",
        "用 RegDst 字段选择目标，三种写法如下：",
    ),
    Edit("optional-source", "首先可以有选择的对右源操作数", "可先按需对右源操作数"),
    Edit("arithmetic-typo", "忽略算数溢出", "忽略算术溢出"),
    Edit("block-body", "可用于任意类型的块指令块体中", "可用在任意类型的块体中"),
    Edit(
        "source-suffix",
        "索引范围同SrcL。SrcR可以选择带后缀，分别表示：",
        "索引范围与 SrcL 相同。SrcR 的可选后缀如下：",
    ),
    Edit(
        "keep-vector-source",
        "当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。",
        "源为向量寄存器时可加此后缀。加后缀时，硬件在本指令提交后必须保留该寄存器；省略时，硬件可以释放它。",
    ),
    Edit(
        "memory-copy",
        "从源内存地址的起始位置开始拷贝若干个字节到目标内存地址中。",
        "从源地址开始，将指定字节数的数据复制到目标地址。",
        "docs/zh/isa/header/templateblock/MCOPY.md",
    ),
    Edit(
        "copy-alignment",
        "在产生搬移指令前需要注意的是，源地址和目的地址的起始位置会有六种不同的字节对齐情况。每种场景下，我们都希望使用尽可能少的指令序列完成数据搬移，因此产生的指令序列有所不同。源和目的地址对齐情况如下所示：",
        "源地址与目标地址有六种字节对齐组合。为尽量减少搬移指令，各组合采用不同的指令序列，如下所示：",
        "docs/zh/isa/header/templateblock/MCOPY.md",
    ),
    Edit(
        "block-execution-order",
        "基于灵犀指令集架构实现的处理器以块指令为单位执行程序。顺序执行的处理器需要按照程序语义的顺序一条条执行块指令。而乱序执行的处理器，可乱序执行块指令但要顺序提交。",
        "灵犀处理器以块为单位执行程序。顺序处理器按程序顺序执行各块；乱序处理器可改变块的执行顺序，但仍须按程序顺序提交。",
        "docs/zh/isa/arch/execute.md",
    ),
    Edit(
        "branch-lead",
        "在灵犀指令集中，控制流的灵活管理是实现高效并行计算的关键。块指令提供了7种不同的跳转方式，每种方式针对特定场景设计，共同构建了完整的控制流体系。",
        "块指令提供七种跳转方式。各方式如何选择后继块，见下文。",
        "docs/zh/isa/arch/branch.md",
    ),
    Edit(
        "branch-summary",
        "这些跳转方式共同构建了灵犀指令集灵活高效的控制流系统，使程序员能够在保持代码简洁性的同时实现复杂的跳转控制逻辑。",
        "",
        "docs/zh/isa/arch/branch.md",
    ),
    Edit(
        "branch-applicability",
        "并不是所有类型的块都支持以上7种块类型，允许某种块类型仅支持一种或几种跳转方式，具体根据块类型特点而定。",
        "具体可用的跳转方式取决于块类型。有些块只支持其中一种或几种。",
        "docs/zh/isa/arch/branch.md",
    ),
    Edit(
        "control-core",
        "作为系统顶层的控制中枢，BCC主要承担以下两个关键功能：",
        "BCC 负责两项工作：",
        "docs/zh/isa/arch/corestate.md",
    ),
    Edit(
        "commit-command",
        "该类指令不仅定义积累状态，还起到提交前一个块指令的作用。",
        "这类指令定义积累状态，同时提交前一个块。",
        "docs/zh/isa/header/Intro.md",
    ),
)

# Inline literals and markup are never the target of a prose substitution.
PROTECTED = re.compile(
    r"(`+[^`\n]*`+|!?(?:\[(?:\\.|[^\]])*\]\([^)]*\))|<[^>\n]+>|\$[^$\n]+\$)"
)


def edit_markdown(path: str, original: str) -> tuple[str, tuple[tuple[str, int], ...]]:
    if not path.startswith("docs/zh/") or not path.endswith(".md"):
        return original, ()
    rules = [
        r for r in EDITS if (not r.source or r.source == path) and r.before in original
    ]
    if not rules:
        return original, ()
    out = []
    hits: Counter[str] = Counter()
    fence = ""
    lines = original.splitlines(keepends=True)
    frontmatter = bool(
        lines
        and lines[0].strip() == "---"
        and any(l.strip() in ("---", "...") for l in lines[1:])
    )
    table = False
    for i, line in enumerate(lines):
        if frontmatter:
            out.append(line)
            if i and line.strip() in ("---", "..."):
                frontmatter = False
            continue

        body = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", body)
        closing = (
            marker
            and fence
            and marker[1].startswith(fence)
            and not body[marker.end() :].strip()
        )
        if (marker and not fence) or closing:
            fence = "" if closing else marker[1]
            out.append(line)
            continue
        if (
            not fence
            and "|" in line
            and i + 1 < len(lines)
            and re.fullmatch(r"[ |:\t-]+", lines[i + 1].rstrip("\r\n"))
            and "-" in lines[i + 1]
        ):
            table = True
        elif "|" not in line:
            table = False
        indented_code = line.startswith(("    ", "\t")) and not body.startswith(
            ("- ", "* ", "+ ")
        )
        if (
            fence
            or table
            or indented_code
            or not body
            or body.startswith(("#", "|", "<", "!!!", "![", "$$"))
        ):
            out.append(line)
            continue
        parts = PROTECTED.split(line)
        for i in range(0, len(parts), 2):
            for rule in rules:
                count = parts[i].count(rule.before)
                if count:
                    parts[i] = parts[i].replace(rule.before, rule.after)
                    hits[rule.key] += count
        out.append("".join(parts))
    return "".join(out), tuple(sorted(hits.items()))


@lru_cache(maxsize=None)
def edit_article(path: str) -> tuple[str, tuple[tuple[str, int], ...]]:
    return edit_markdown(path, tagged_bytes(path).decode("utf-8"))
