"""Offline navigation and release notes alongside the authored architecture chapters."""

from hashlib import sha256
from html import escape

from manual_v0591_chapters import ACTIVE_REPLACEMENTS
from manual_architecture import (
    architecture_pages,
    architecture_collections,
)
from manual_tag import tagged_bytes


def anchor(route, text):
    return f'<a href="{escape(route, quote=True)}">{escape(text)}</a>'


def architecture_bodies(library, chapters=None, *, edition="0.59.1"):
    chapters = architecture_pages() if chapters is None else chapters
    by_collection = {
        key: [p for p in chapters if p.collection == key]
        for key in architecture_collections()
    }
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
        source = (
            library.source_text(path).encode()
            if library.source_text
            else tagged_bytes(path)
        )
        if library.source_text:
            source = library.download_source(path, source.decode()).encode()
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

        rewritten = path in ACTIVE_REPLACEMENTS
        status = "release-reviewed" if rewritten else chapter.status
        body += original
        results[chapter.route] = (chapter.title, body)
        audit[chapter.route] = {
            "source_path": path,
            "source_sha256": sha256(library.original_source(path)).hexdigest(),
            **({"reader_sha256": digest} if library.source_text else {}),
            "rendered_sha256": sha256(content.encode()).hexdigest(),
            "status": status,
            "collection": chapter.collection,
        }
    return results, audit
