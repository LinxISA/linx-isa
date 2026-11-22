"""Offline navigation and release notes alongside the authored architecture chapters."""

from hashlib import sha256
from html import escape

from manual_architecture import (
    architecture_pages,
    architecture_collections,
    register_catalog_html,
)
from manual_editorial import edit_article
from manual_tag import tagged_bytes


def anchor(route, text):
    return f'<a href="{escape(route, quote=True)}">{escape(text)}</a>'


# These notes distinguish reviewable current rules from historical examples.
# They are visible before the source where a historic table could mislead RTL.
DIFFERENCES = {
    "tile-registers": (
        "本版的 Tile 绑定",
        [
            "本地源和重命名目标通过 B.IOT 绑定。T、U、M、N 表示本地命名队列；本版 Local 目标 SizeCode 1–10 表示 128 B 至 64 KiB。",
            "B.IOS 的共享源或目标按 S0–S63 的绝对编号选择。Shared 目标 SizeCode 1–12 表示 128 B 至 256 KiB。两组范围分别描述绑定命令能编码的大小。",
            "矩阵累加显式读取本地 Tile C，结果写入显式目标 D。下方原页的“32 个通用寄存器 + ACC/S”和单一容量范围属于旧模型。",
        ],
        [
            ("op-b-iot.html", "B.IOT"),
            ("op-b-ios.html", "B.IOS"),
            ("tile-tmatmul-acc.html", "TMATMUL_ACC"),
        ],
        True,
    ),
    "constraints": (
        "旧约束中的矩阵累加器",
        [
            "原页 A9.6、A9.7 和 B10 使用隐式 ACC 的分配与释放规则。本版 CUBE 指令以显式本地 Tile 指定累加源和结果；实现累加路径时请使用操作页的 C、D 绑定。",
        ],
        [
            ("arch-cube-block.html", "矩阵块"),
            ("tile-tmatmul-acc.html", "带累加的矩阵乘法"),
        ],
        True,
    ),
    "core-state": (
        "Janus Core 的历史实现示例",
        [
            "下表按早期 Janus Core 的 BCC、VEC、TMU、CUBE 单元列举状态，其中包括旧式 SCR 和隐式 ACC。本版 Tile 操作按 VEC、SFU、TLSU 和 CUBE 分类；寄存器号和 Tile 大小请查本版绑定命令。",
        ],
        [
            ("arch-state.html", "架构状态目录"),
            ("arch-tile-registers.html", "本版 Tile 绑定"),
            ("tile.html", "Tile 操作"),
        ],
        True,
    ),
    "predicate": (
        "谓词位与元素宽度",
        [
            "原页按通道说明 P 寄存器。对发布版 Sail 以两个 32 位通道承载一个 64 位元素的路径，第 i 个元素使用谓词位 2×i。非活动通道的结果按具体操作核对。",
        ],
        [("op-v-cmp-and.html", "V.CMP.AND"), ("op-v-add.html", "V.ADD")],
        False,
    ),
}


def architecture_bodies(library):
    chapters = architecture_pages()
    by_collection = architecture_collections()
    indexes = {
        p.key.removesuffix("-index"): p for p in chapters if p.key.endswith("-index")
    }
    results, audit = {}, {}
    for chapter in chapters:
        if chapter.key == "architecture":
            overview = (
                "<p>先确定指令能读取和更新哪些状态，再沿块执行流程查明结果何时提交。"
                "系统寄存器的地址和访问属性可在发布版寄存器表中查找。</p>"
                '<ul class="chapter-index">'
                + "".join(
                    f"<li>{anchor(p.route, p.title)}<span>{escape(p.summary)}</span></li>"
                    for p in indexes.values()
                )
                + "</ul>"
            )
            results[chapter.route] = (chapter.title, overview)
            continue
        if not chapter.source_path:
            collection = chapter.key.removesuffix("-index")
            listing = (
                '<ul class="chapter-index">'
                + "".join(
                    f"<li>{anchor(p.route, p.title)}<span>{escape(p.summary)}</span></li>"
                    for p in by_collection[collection]
                )
                + "</ul>"
            )
            if collection == "ssr":
                listing = (
                    '<h2 id="system-registers">0.59.1 系统寄存器目录</h2>'
                    "<p>下表保留发布目录中的地址或低位索引、读写权限和作用域。历史中文页用于查阅设计背景。</p>"
                    '<div class="table-scroll">'
                    + register_catalog_html()
                    + "</div><h2>中文站各寄存器说明</h2>"
                    + listing
                )
            if collection == "state":
                listing = (
                    "<p>"
                    + anchor(
                        "arch-ssr.html#system-registers", "查阅 100 项系统寄存器定义"
                    )
                    + "</p>"
                    + listing
                )
            results[chapter.route] = (
                chapter.title,
                "<p>" + escape(chapter.summary) + "</p>" + listing,
            )
            continue

        path = chapter.source_path
        source = tagged_bytes(path)
        digest = sha256(source).hexdigest()
        raw_path = f"article-source/{digest}.md"
        library.files[raw_path] = source
        content = library.fragments[path]
        original = (
            '<section class="authored-reader" data-source-path="' + escape(path) + '">'
            '<p class="article-source">正文来源 · ' + anchor(raw_path, path) + "</p>"
            "<!-- authored:start -->" + content + "<!-- authored:end --></section>"
        )
        group = indexes[chapter.collection]
        body = (
            '<p class="meta">'
            + anchor("architecture.html", "架构目录")
            + " / "
            + anchor(group.route, group.title)
            + "</p>"
        )
        status = chapter.status
        if chapter.key in DIFFERENCES:
            label, notes, links, historical = DIFFERENCES[chapter.key]
            body += (
                f'<section class="edition-difference"><h2>{escape(label)}</h2>'
                + "".join("<p>" + escape(n) + "</p>" for n in notes)
                + "<p>"
                + " · ".join(anchor(r, t) for r, t in links)
                + "</p></section>"
            )
            if historical:
                status = "historical-conflict"
                original = (
                    '<details class="historical-article"><summary>查看历史中文原页</summary>'
                    + original
                    + "</details>"
                )
        elif chapter.version_note and (
            status != "tagged-original"
            or chapter.key
            in {"tlsu-block", "cube-block", "tepl-carrier", "exception-model"}
        ):
            body += (
                '<p class="version-context">' + escape(chapter.version_note) + "</p>"
            )
        body += original
        results[chapter.route] = (chapter.title, body)
        audit[chapter.route] = {
            "source_path": path,
            "source_sha256": digest,
            "rendered_sha256": sha256(content.encode()).hexdigest(),
            "status": status,
            "prose_edits": dict(edit_article(path)[1]),
            "collection": chapter.collection,
        }
    return results, audit
