"""Offline cross-references and scalar notation for the current programming manual."""

import re
from urllib.parse import unquote, urlsplit

from manual_markdown import (
    _resolve_local,
    document_namespace,
    support_asset_path,
    support_document_path,
)

GLOSSARY = "docs/zh/isa/inst/LibPseudoCode.md"
GLOSSARY_TEXT = """# 标量指令中的符号

## 无符号解释 {#locationA}

`UInt(x)` 把固定位宽的比特串按无符号整数解释。例如，八位值 `0xff` 的无符号值是 255。

## Reg5 源与目标 {#locationB}

作为源时，编码 0 读零；1 至 23 选择通用寄存器；24 至 27、28 至 31 分别选择 T、U 队列的第 1 至第 4 个已有结果，1 表示最新一项。读取队列源不会移除这项结果。使用 Reg5 的指令按自身定义检查源是否可读。

作为通用 Reg5 目标时，1 至 23 写通用寄存器，30 将结果压入 U 队列，31 将结果压入 T 队列，0 和 24 至 29 丢弃结果。结果位宽及字结果的扩展方式见每条指令的执行说明。

## 逻辑左移 {#locationE}

逻辑左移把零填入空出的低位，并截去超出结果位宽的高位。

## 符号扩展 {#locationF}

`SignExtend(x)` 保留源的全部位，将源的最高位复制到新增的高位。例如，将八位 `0x80` 扩展到 64 位得到 `0xffffffffffffff80`。

## 零扩展 {#locationG}

`ZeroExtend(x)` 保留源的全部位，新增的高位全部填零。同一个八位值 `0x80` 零扩展到 64 位仍为 `0x80`。

## 按位取反 {#locationH}

`Not(x)` 把给定位宽内的每一位翻转。

## 取相反数 {#locationI}

`Negative(x)` 在给定位宽内取二进制补码的相反数，等效于逐位取反再加一。
"""
# Match only Markdown links. Leave assembly brackets and code examples intact.
_LINK = re.compile(r"(!?)\[((?:\\.|[^\[\]\n]|\[[^\]\n]*\])*)\]\(([^)\s]+)\)")


def reader_links(path, markdown, routes, *, download=False):
    """Drop unrouted cross-references; make the downloadable manuscript usable offline."""

    def replace(match):
        image, label, raw = match.groups()
        target = urlsplit(raw)
        if target.scheme or not target.path:
            return match[0]
        source = _resolve_local(path, target.path)
        if source is None:
            return "" if image else label
        if image or not source.endswith(".md"):
            route = support_asset_path(source)
        elif source == GLOSSARY:
            route = support_document_path(source)
        else:
            route = routes.get(source)
        if not route:
            return label
        if not download:
            return match[0]
        fragment = ""
        if target.fragment:
            fragment = (
                "#" + document_namespace(source) + "--" + unquote(target.fragment)
            )
        return f"{image}[{label}](../{route}{fragment})"

    return "".join(
        part if part.startswith("```") else _LINK.sub(replace, part)
        for part in re.split(r"(```[^\n]*\n[\s\S]*?```)", markdown)
    )
