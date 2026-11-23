#!/usr/bin/env python3
"""Index human-authored Chinese ISA articles from the reviewed v0.59.1 tag.

The returned material is explanatory source language. Compatibility metadata
prevents an older article from being presented as the current normative
contract merely because its filename or mnemonic still exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re
import subprocess
from typing import Any, Mapping

try:
    from manual_tag import (
        REPO_ROOT,
        REVIEWED_COMMIT,
        tagged_bytes,
        tagged_json,
        verified_tag_commit,
    )
except ModuleNotFoundError:
    from tools.isa.manual_tag import (
        REPO_ROOT,
        REVIEWED_COMMIT,
        tagged_bytes,
        tagged_json,
        verified_tag_commit,
    )

try:
    from manual_index_notes import index_note
    from manual_index_families import family_index_synopsis
    from manual_reader import _plain_markdown
except ModuleNotFoundError:
    from tools.isa.manual_index_notes import index_note
    from tools.isa.manual_index_families import family_index_synopsis
    from tools.isa.manual_reader import _plain_markdown

ROOT = "docs/zh/isa/inst/"
FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
OPERAND_NAMES = {
    "SrcL",
    "SrcR",
    "SrcD",
    "SrcD1",
    "SrcA",
    "SrcP",
    "SrcZero",
    "RegSrc",
    "RegSrc0",
    "RegSrc1",
    "RegSrc2",
    "RegDst",
    "RegDst0",
    "RegDst1",
    "Rd",
    "Dst",
    "Dst0",
    "Dst1",
    "simm",
    "uimm",
    "shamt",
}


@dataclass(frozen=True)
class AuthoredSection:
    heading: str
    markdown: str


@dataclass(frozen=True)
class AuthoredArticle:
    source_family: str
    source_path: str
    source_url: str
    title: str
    sections: tuple[AuthoredSection, ...]
    intro: str
    examples: tuple[str, ...]
    headings: tuple[str, ...]
    associated_form_ids: tuple[str, ...]
    associated_groups: tuple[str, ...]
    classification: str
    reasons: tuple[str, ...]
    current_view: tuple[str, ...]


def _paths() -> tuple[str, ...]:
    verified_tag_commit()
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "--full-tree", REVIEWED_COMMIT, ROOT],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = tuple(path for path in result.stdout.splitlines() if path.endswith(".md"))
    if not paths:
        raise ValueError(
            "reviewed tag contains no human-authored instruction source inventory"
        )
    return paths


def _tree_paths(root: str) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "--full-tree", REVIEWED_COMMIT, root],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = tuple(path for path in result.stdout.splitlines() if path.endswith(".md"))
    if not paths:
        raise ValueError(f"reviewed tag contains no Markdown sources under {root}")
    return paths


def _parse(markdown: str) -> tuple[str, tuple[AuthoredSection, ...], tuple[str, ...]]:
    matches = list(HEADING.finditer(markdown))
    if not matches or len(matches[0].group(1)) != 1:
        raise ValueError("authored article has no H1 title")
    title = matches[0].group(2).strip()
    sections: list[AuthoredSection] = []
    headings = [match.group(2).strip() for match in matches]
    level_two = [match for match in matches[1:] if len(match.group(1)) == 2]
    for index, match in enumerate(level_two):
        end = (
            level_two[index + 1].start()
            if index + 1 < len(level_two)
            else len(markdown)
        )
        sections.append(
            AuthoredSection(match.group(2).strip(), markdown[match.end() : end].strip())
        )
    return title, tuple(sections), tuple(headings)


def _plain_intro(sections: tuple[AuthoredSection, ...], markdown: str) -> str:
    section = next(
        (item for item in sections if item.heading in {"说明", "简介", "功能说明"}),
        None,
    )
    if section is not None:
        prose = section.markdown
    else:
        # Some authored articles begin their explanation immediately after H1
        # (HL.CCAT is one); their first H2 already starts the assembly syntax.
        lines = markdown.splitlines()
        title = next((i for i, line in enumerate(lines) if line.startswith("# ")), None)
        if title is None:
            return ""
        end = next(
            (i for i in range(title + 1, len(lines)) if lines[i].startswith("#")),
            len(lines),
        )
        prose = "\n".join(lines[title + 1 : end])
        if any(
            term in prose
            for term in ("非规范导航页", "英文原页", "机器生成附录", "本文档介绍了")
        ):
            return ""
    prose = FENCE.sub("", prose)
    prose = re.sub(r"!\[[^]]*\]\([^)]*\)(?:\{[^}]*\})?", "", prose)
    return _plain_markdown(prose)


def _assembly(section: AuthoredSection | None) -> str:
    if section is None:
        return ""
    blocks = FENCE.findall(section.markdown)
    if not blocks:
        return ""
    return next((line.strip() for line in blocks[0].splitlines() if line.strip()), "")


def _canon_asm(value: str) -> str:
    value = value.lower().replace("−", "-")
    return re.sub(r"\s+", "", value)


def _field_names(row: Mapping[str, Any]) -> set[str]:
    return {
        str(field["name"])
        for part in row.get("encoding", {}).get("parts", [])
        for field in part.get("fields", [])
    }


def _authored_operands(assembly: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_]*", assembly)
        if token in OPERAND_NAMES
    }


def _operand_is_current(name: str, fields: set[str]) -> bool:
    aliases = {"Rd": "RegDst", "Dst": "RegDst", "Dst0": "RegDst0", "Dst1": "RegDst1"}
    name = aliases.get(name, name)
    if name in {"simm", "uimm"}:
        return any("imm" in field.lower() for field in fields)
    if name == "SrcP" and "SrcZero" in fields:
        return True
    return name in fields


@lru_cache(maxsize=1)
def _catalog_rows() -> tuple[dict[str, Any], ...]:
    return tuple(
        row
        for row in tagged_json("isa/v0.59/linxisa-v0.59.json")["instructions"]
        if not row.get("pto_scope")
    )


@lru_cache(maxsize=1)
def _by_mnemonic() -> dict[str, tuple[dict[str, Any], ...]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in _catalog_rows():
        grouped.setdefault(str(row["mnemonic"]), []).append(row)
    return {key: tuple(value) for key, value in grouped.items()}


@lru_cache(maxsize=1)
def _path_by_stem() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in _paths():
        stem = path.rsplit("/", 1)[-1][:-3]
        if stem in out:
            raise ValueError(f"ambiguous authored filename stem: {stem}")
        out[stem] = path
    return out


@lru_cache(maxsize=1)
def _support_path_by_stem() -> dict[str, str]:
    paths = [
        *_tree_paths("docs/zh/isa/header/"),
        *_tree_paths("docs/zh/isa/header/templateblock/"),
    ]
    ranked: dict[str, tuple[int, str]] = {}
    for path in paths:
        if "/tileblock/" in path:
            continue
        stem = path.rsplit("/", 1)[-1][:-3]
        rank = 0 if "/templateblock/" in path else 1
        if stem not in ranked or rank < ranked[stem][0]:
            ranked[stem] = (rank, path)
    return {stem: value[1] for stem, value in ranked.items()}


def _source_for_mnemonic(mnemonic: str) -> tuple[str, str] | None:
    if mnemonic in _path_by_stem():
        return mnemonic, _path_by_stem()[mnemonic]
    if mnemonic in _support_path_by_stem():
        return mnemonic, _support_path_by_stem()[mnemonic]
    aliases = {"C.B.DIMI": "C.B.DIM", "C.BSTOP": "BSTOP", "L.BSTOP": "BSTOP"}
    if mnemonic.startswith("C.BSTART."):
        aliases[mnemonic] = "C.BSTART"
    if mnemonic.startswith("HL.BSTART"):
        aliases[mnemonic] = "HL.BSTART"
    if mnemonic.startswith("L.BSTART."):
        aliases[mnemonic] = "L.BSTART"
    if mnemonic in {"BSTART.MPAR", "BSTART.MSEQ", "BSTART.VPAR", "BSTART.VSEQ"}:
        aliases[mnemonic] = "BSTART"
    if ".U.BRG" in mnemonic:
        aliases[mnemonic] = mnemonic.replace(".U.BRG", ".BRG")
    stem = aliases.get(mnemonic)
    if stem in _path_by_stem():
        return stem, _path_by_stem()[stem]
    if stem in _support_path_by_stem():
        return stem, _support_path_by_stem()[stem]
    if mnemonic.startswith("BSTART.MGATHER"):
        return "MGATHER", "docs/zh/isa/header/tileblock/MGATHER.md"
    if mnemonic.startswith("BSTART.MSCATTER"):
        return "MSCATTER", "docs/zh/isa/header/tileblock/MSCATTER.md"
    if mnemonic.startswith("BSTART."):
        operation = mnemonic.removeprefix("BSTART.")
        if operation in _tile_path_by_stem():
            return operation, _tile_path_by_stem()[operation]
    explicit = {
        "BSTART.GMOV": ("TLSU 块头", "docs/zh/isa/blockIntro/tlsu_block/header.md"),
        "BSTART.ICALL": ("分支与调用", "docs/zh/isa/arch/branch.md"),
        "BSTART.TEPL": ("BSTART", "docs/zh/isa/header/BSTART.md"),
        "PRF": ("预取", "docs/zh/isa/blockIntro/std_block/prefetch.md"),
        "PRFI.U": ("预取", "docs/zh/isa/blockIntro/std_block/prefetch.md"),
        "TLB.IA": ("TLB 维护", "docs/zh/isa/blockIntro/sys_block/tlb.md"),
        "TLB.IALL": ("TLB 维护", "docs/zh/isa/blockIntro/sys_block/tlb.md"),
        "TLB.IAV": ("TLB 维护", "docs/zh/isa/blockIntro/sys_block/tlb.md"),
        "TLB.IV": ("TLB 维护", "docs/zh/isa/blockIntro/sys_block/tlb.md"),
    }
    if mnemonic in explicit:
        return explicit[mnemonic]
    return None


def _classify(
    row: Mapping[str, Any], title: str, authored_asm: str, source_stem: str
) -> tuple[str, tuple[str, ...]]:
    reasons: list[str] = []
    if source_stem != row["mnemonic"]:
        reasons.append(
            f"当前助记符关联到原文分组或替代拼写 {source_stem}，仅按原作者语境展示。"
        )
    fields = _field_names(row)
    authored_fields = _authored_operands(authored_asm)
    extra = sorted(
        name for name in authored_fields if not _operand_is_current(name, fields)
    )
    if extra and source_stem == row["mnemonic"]:
        reasons.append("原文汇编含有当前编码不存在的操作数：" + ", ".join(extra))
        return "conflicting-current", tuple(reasons)
    if row["mnemonic"] in {"HL.SETC.LTI", "HL.SETC.ORI", "V.LD.MIN"}:
        return "conflicting-current", ("中文原页的比较条件或运算名称与发布定义不同。",)
    if row["mnemonic"] in {"HL.CCAT", "HL.CCATW"}:
        return "conflicting-current", (
            "中文原页写成循环左移，两个目标的高低顺序也与发布版相反。",
        )
    if row["mnemonic"] in {"V.CMP.AND", "V.CMP.ANDI"}:
        reasons.extend(
            (
                "原文先做按位 AND 再判断结果是否非零；v0.59.1 发布版 Sail 模型 先把两个输入分别判为零/非零，再做布尔 AND。输入 1 与 2 可区分两者：原文结果为 0，发布版 Sail 模型 结果为 1。",
                "原文把非活动通道 写为 0；v0.59.1 发布版 Sail 模型 对该 lane 产生未指定值。",
            )
        )
        return "conflicting-current", tuple(reasons)
    if row["mnemonic"] == "V.REV":
        reasons.append(
            "原文按 M/N 描述位域内分组翻转；v0.59.1 发布版 Sail 模型 固定对每个 32 位 lane 做字节序反转，并忽略 immr/imml。"
        )
        return "conflicting-current", tuple(reasons)
    if title != row["mnemonic"]:
        reasons.append(f"原文 H1 为 {title}，当前目录助记符为 {row['mnemonic']}")
    if (
        authored_asm
        and _canon_asm(authored_asm) == _canon_asm(str(row["asm"]))
        and not reasons
    ):
        return "syntax-compatible-original", (
            "原文汇编语法与当前目录形式一致；这只证明写法兼容，语义仍以 v0.59.1 规范为准。",
        )
    if authored_asm:
        reasons.append("原文汇编写法与当前目录形式未能逐字一致，按历史语境展示。")
    else:
        reasons.append("原文没有可机械核对的汇编语法，按历史语境展示。")
    return "contextual-original", tuple(reasons)


def _current_view(row: Mapping[str, Any], classification: str) -> tuple[str, ...]:
    if row["mnemonic"] == "DC.IALL":
        return (
            "v0.59.1 当前形式为固定机器字 0x0010602b，汇编语法是 dc.iall。",
            "当前形式没有 SrcL 或其他显式操作数；旧文中的寄存器语法和示例不可用于当前编码。",
            "该指令仅在系统块内合法，成功时记录 Maintenance_DC_IALL、递增数据缓存维护计数并令 TPC 前进 4 字节。",
        )
    if row["mnemonic"] in {"HL.SETC.LTI", "HL.SETC.ORI", "V.LD.MIN"}:
        return (family_index_synopsis(row["mnemonic"]),)
    if row["mnemonic"] in {"HL.CCAT", "HL.CCATW"}:
        return (index_note(row),)
    if row["mnemonic"] in {"V.CMP.AND", "V.CMP.ANDI"}:
        right = "符号扩展后的 simm12" if row["mnemonic"].endswith("ANDI") else "SrcR"
        return (
            f"v0.59.1 发布版 Sail 模型 对每个活动通道 计算 (SrcL != 0) AND ({right} != 0)，并写入 0 或 1。",
            "判别例 SrcL=1、右输入=2 的结果为 1；这与旧文的按位与结果 0 不同。",
            "非活动通道 的结果在 发布版 Sail 模型 中未指定，不应沿用旧文的写零说明。",
        )
    if row["mnemonic"] == "V.REV":
        return (
            "v0.59.1 发布版 Sail 模型 对每个活动 32 位 lane 执行完整字节序反转（bswap32）。",
            "当前 Sail 忽略编码中的 immr/imml；旧文的 M/N 位域翻转和合法性表仅保留为历史说明，不能作为当前模型行为。",
            "非活动通道 的结果在 发布版 Sail 模型 中未指定。",
        )
    if classification == "conflicting-current":
        return (f"当前规范汇编：{row['asm']}",)
    return ()


@lru_cache(maxsize=None)
def _article_for_mnemonic(mnemonic: str, row_id: str) -> AuthoredArticle | None:
    source = _source_for_mnemonic(mnemonic)
    if source is None:
        return None
    source_stem, path = source
    markdown = tagged_bytes(path).decode("utf-8")
    title, sections, headings = _parse(markdown)
    syntax = next(
        (section for section in sections if section.heading.rstrip("：") == "汇编语法"),
        None,
    )
    authored_asm = _assembly(syntax)
    rows = _by_mnemonic().get(mnemonic, ())
    row = next((item for item in rows if item["id"] == row_id), None)
    if row is None:
        return None
    classification, reasons = _classify(row, title, authored_asm, source_stem)
    example_section = next(
        (
            section
            for section in sections
            if "索引模式" in section.heading or "示例" in section.heading
        ),
        None,
    )
    examples = (
        tuple(block.strip() for block in FENCE.findall(example_section.markdown))
        if example_section
        else ()
    )
    return AuthoredArticle(
        source_family="instruction",
        source_path=path,
        source_url=f"https://github.com/LinxISA/linx-isa/blob/{REVIEWED_COMMIT}/{path}",
        title=title,
        sections=sections,
        intro=_plain_intro(sections, markdown),
        examples=examples,
        headings=headings,
        associated_form_ids=tuple(str(item["id"]) for item in rows),
        associated_groups=tuple(sorted({str(item.get("group", "")) for item in rows})),
        classification=classification,
        reasons=reasons,
        current_view=_current_view(row, classification),
    )


def authored_for(
    row: Mapping[str, Any], catalog: Mapping[str, Any] | None = None
) -> AuthoredArticle | None:
    """Return the reviewed-tag Chinese article associated with one current form."""
    del catalog
    return _article_for_mnemonic(str(row["mnemonic"]), str(row["id"]))


@lru_cache(maxsize=1)
def _tile_path_by_stem() -> dict[str, str]:
    return {
        path.rsplit("/", 1)[-1][:-3]: path
        for path in _tree_paths("docs/zh/isa/header/tileblock/")
    }


def _tile_stem(name: str) -> str | None:
    paths = _tile_path_by_stem()
    candidates = [name]
    candidates.append(
        name.replace("_MX_", "MX.")
        .replace("_MX", "MX")
        .replace("_BIAS", ".BIAS")
        .replace("_ACC", ".ACC")
    )
    if name.startswith("MGATHER_"):
        candidates.append("MGATHER")
    if name.startswith("MSCATTER_"):
        candidates.append("MSCATTER")
    return next((candidate for candidate in candidates if candidate in paths), None)


@lru_cache(maxsize=1)
def _tile_ops() -> dict[str, dict[str, Any]]:
    return {
        row["name"]: row
        for row in tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
    }


@lru_cache(maxsize=None)
def authored_tile(name: str) -> AuthoredArticle | None:
    """Return a contextual original Linx Tile article for one published TileOp."""
    op = _tile_ops().get(name)
    stem = _tile_stem(name)
    if op is None or stem is None:
        return None
    path = _tile_path_by_stem()[stem]
    markdown = tagged_bytes(path).decode("utf-8")
    title, sections, headings = _parse(markdown)
    example_section = next(
        (
            section
            for section in sections
            if "示例" in section.heading or "索引模式" in section.heading
        ),
        None,
    )
    examples = (
        tuple(block.strip() for block in FENCE.findall(example_section.markdown))
        if example_section
        else ()
    )
    reasons = [
        "该页面是原始 Linx Tile 说明，用于理解数据流、示例和图示；v0.59.1 的操作数、布局、合法性与异常仍以发布版 PTO ASL 为准。"
    ]
    if stem != name:
        reasons.append(
            f"当前操作 {name} 关联到历史分组页面 {stem}，页面中的具体选择子与布局不得直接视为当前编码。"
        )
    return AuthoredArticle(
        source_family="tileblock",
        source_path=path,
        source_url=f"https://github.com/LinxISA/linx-isa/blob/{REVIEWED_COMMIT}/{path}",
        title=title,
        sections=sections,
        intro=_plain_intro(sections, markdown),
        examples=examples,
        headings=headings,
        associated_form_ids=(
            f"tile:{op['engine']}:{op.get('mode', '-')}:{op['function']}:{name}",
        ),
        associated_groups=(
            str(op["classification"]),
            str(op["engine"]),
            str(op["command_mnemonic"]),
        ),
        classification="contextual-original",
        reasons=tuple(reasons),
        current_view=(
            f"当前引擎：{op['engine']}；编码载体：{op['command_mnemonic']}；选择子：{op.get('selector') or 'Function=' + str(op['function'])}。",
        ),
    )


def source_inventory() -> tuple[tuple[str, str, bool], ...]:
    """Return (path, title, exact-current-stem) for every tagged inst article."""
    current = set(_by_mnemonic())
    rows = []
    for stem, path in sorted(_path_by_stem().items()):
        title, _, _ = _parse(tagged_bytes(path).decode("utf-8"))
        rows.append((path, title, stem in current))
    return tuple(rows)


def tile_source_inventory() -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    """Return each tagged tileblock article and the published TileOps using it."""
    reverse: dict[str, list[str]] = {}
    for name in _tile_ops():
        article = authored_tile(name)
        if article:
            reverse.setdefault(article.source_path, []).append(name)
    rows = []
    for path in sorted(_tree_paths("docs/zh/isa/header/tileblock/")):
        try:
            title, _, _ = _parse(tagged_bytes(path).decode("utf-8"))
        except ValueError:
            title = path.rsplit("/", 1)[-1][:-3]
        rows.append((path, title, tuple(sorted(reverse.get(path, [])))))
    return tuple(rows)


def coverage_report() -> dict[str, Any]:
    rows = list(_catalog_rows())
    articles = [authored_for(row) for row in rows]
    classifications: dict[str, int] = {}
    for article in articles:
        if article:
            classifications[article.classification] = (
                classifications.get(article.classification, 0) + 1
            )
    missing_mnemonics = sorted(
        {row["mnemonic"] for row, article in zip(rows, articles) if article is None}
    )
    tile_missing = sorted(name for name in _tile_ops() if authored_tile(name) is None)
    return {
        "instruction_source_articles": len(source_inventory()),
        "instruction_forms": len(rows),
        "mapped_instruction_forms": sum(article is not None for article in articles),
        "mapped_instruction_mnemonics": len(
            {row["mnemonic"] for row, article in zip(rows, articles) if article}
        ),
        "classification_counts": dict(sorted(classifications.items())),
        "missing_instruction_mnemonics": missing_mnemonics,
        "tile_source_articles": len(tile_source_inventory()),
        "tile_operations": len(_tile_ops()),
        "mapped_tile_operations": sum(
            authored_tile(name) is not None for name in _tile_ops()
        ),
        "missing_tile_operations": tile_missing,
    }


__all__ = [
    "AuthoredArticle",
    "AuthoredSection",
    "authored_for",
    "authored_tile",
    "coverage_report",
    "source_inventory",
    "tile_source_inventory",
]
