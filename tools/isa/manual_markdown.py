#!/usr/bin/env python3
"""Safe, tag-backed Markdown rendering for the offline ISA manual."""

from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from html import escape
from html.parser import HTMLParser
from pathlib import PurePosixPath
import hashlib, posixpath
import subprocess
from typing import Callable, Mapping
from urllib.parse import quote, unquote, urlsplit, urlunsplit
import markdown
from manual_editorial import edit_article
from manual_tag import REPO_ROOT, REVIEWED_COMMIT, tagged_bytes
from manual_revision import is_removed_form

EXTENSIONS = [
    "admonition",
    "footnotes",
    "tables",
    "toc",
    "pymdownx.highlight",
    "pymdownx.superfences",
    "pymdownx.tabbed",
    "pymdownx.smartsymbols",
    "attr_list",
    "md_in_html",
]
REMOTE = {"http", "https", "mailto"}
DROP = {"script", "style", "iframe", "object", "embed", "form", "input", "button"}
VOID = {"br", "hr", "img"}


@dataclass(frozen=True)
class MarkdownFragment:
    html: str
    documents: tuple[str, ...]
    assets: tuple[str, ...]
    external_links: tuple[str, ...]


@dataclass(frozen=True)
class SupportBundle:
    source_paths: dict[str, str]
    fragments: dict[str, str]
    assets: dict[str, bytes]
    external_links: tuple[str, ...]


def document_namespace(path: str) -> str:
    stem = (
        "".join(
            c if c.isalnum() else "-" for c in PurePosixPath(path).stem.lower()
        ).strip("-")
        or "doc"
    )
    return f"src-{stem}-{hashlib.sha256(path.encode()).hexdigest()[:8]}"


def support_document_path(path: str) -> str:
    return (
        "support/"
        + quote(path.removesuffix(".md").replace("/", "--"), safe="-_.")
        + ".html"
    )


def support_asset_path(path: str) -> str:
    return "support-assets/" + quote(path.replace("/", "--"), safe="-_.")


def pinned_source_url(path: str, fragment: str = "") -> str:
    url = f"https://github.com/LinxISA/linx-isa/blob/{REVIEWED_COMMIT}/{quote(path, safe='/.-_')}"
    return url + (f"#{fragment}" if fragment else "")


@lru_cache(maxsize=1)
def _repository_paths() -> tuple[str, ...]:
    output = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", REVIEWED_COMMIT],
        cwd=REPO_ROOT,
        text=True,
    )
    return tuple(output.splitlines())


@lru_cache(maxsize=None)
def _resolve_local(source: str, raw_path: str) -> str | None:
    target = posixpath.normpath(
        posixpath.join(posixpath.dirname(source), unquote(raw_path))
    )
    paths = _repository_paths()
    if target in set(paths):
        return target
    lower = {path.lower(): path for path in paths}
    if target.lower() in lower:
        return lower[target.lower()]
    if target.startswith("docs/isa/"):
        mirror = "docs/zh/" + target.removeprefix("docs/")
        if mirror.lower() in lower:
            return lower[mirror.lower()]
    parts = PurePosixPath(target).parts
    for count in (4, 3, 2, 1):
        if len(parts) < count:
            continue
        suffix = "/".join(parts[-count:]).lower()
        matches = [path for path in paths if path.lower().endswith("/" + suffix)]
        if len(matches) == 1:
            return matches[0]
    return None


class _SafeHTML(HTMLParser):
    def __init__(
        self,
        source: str,
        namespace: str,
        follow: Callable[[str, str], bool],
        current_page: str,
        routes: Mapping[str, str],
        omit_title: bool,
    ):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.namespace = namespace
        self.follow = follow
        self.current_page = current_page
        self.routes = routes
        self.omit_title = omit_title
        self.out = []
        self.documents = set()
        self.assets = set()
        self.external = set()
        self.drop = 0
        self.first_h1 = True
        self.drop_title = 0

    def relative(self, target: str) -> str:
        return posixpath.relpath(target, posixpath.dirname(self.current_page) or ".")

    def link(self, raw: str, image: bool):
        p = urlsplit(raw)
        if p.scheme:
            if p.scheme.lower() not in REMOTE:
                return "#unsafe-link", {}
            self.external.add(raw)
            return raw, {}
        if p.netloc:
            return "#unsafe-link", {}
        if not p.path:
            return urlunsplit(
                (
                    "",
                    "",
                    "",
                    p.query,
                    f"{self.namespace}--{p.fragment}" if p.fragment else "",
                )
            ), {}
        candidate = posixpath.normpath(
            posixpath.join(posixpath.dirname(self.source), unquote(p.path))
        )
        stem = PurePosixPath(candidate).stem.upper().replace("_", ".")
        removed_target = (
            not image
            and (
                is_removed_form(stem)
                or candidate.endswith("/register/common/vgpr.md")
                or "/blockIntro/vec_block/" in candidate
            )
        )
        if removed_target:
            return "", {
                "class": "removed-local-reference",
                "title": "该目标不属于本次 0.59.1 修订；保留引用文字。",
            }
        target = _resolve_local(self.source, p.path)
        if target is None:
            return "", {
                "class": "missing-local-reference",
                "title": f"发布 tag 中没有可解析的本地目标：{p.path}",
            }
        if target.lower().endswith(".md") and not image:
            if target in self.routes:
                frag = (
                    f"{document_namespace(target)}--{p.fragment}" if p.fragment else ""
                )
                return urlunsplit(
                    ("", "", self.relative(self.routes[target]), p.query, frag)
                ), {}
            if self.follow(self.source, target):
                self.documents.add(target)
                frag = (
                    f"{document_namespace(target)}--{p.fragment}" if p.fragment else ""
                )
                return urlunsplit(
                    (
                        "",
                        "",
                        self.relative(support_document_path(target)),
                        p.query,
                        frag,
                    )
                ), {}
            return "", {
                "class": "unbundled-local-reference",
                "title": f"本地参考未纳入当前离线支持包：{target}",
                "data-local-source": target,
            }
        self.assets.add(target)
        return self.relative(support_asset_path(target)), {}

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.drop_title:
            return
        if tag in DROP:
            self.drop += 1
            return
        if self.drop:
            return
        if tag == "h1" and self.first_h1 and self.omit_title:
            self.first_h1 = False
            self.drop_title = 1
            return
        if tag == "h1":
            tag = "h2"
            self.first_h1 = False
        clean = {}
        for k, v in attrs:
            k = k.lower()
            v = v or ""
            if k.startswith("on") or k == "style":
                continue
            if k == "id":
                clean[k] = f"{self.namespace}--{v}"
            elif k in {"href", "src"}:
                v, extra = self.link(v, tag == "img")
                if v:
                    clean[k] = v
                clean.update(extra)
            elif k in {
                "class",
                "title",
                "alt",
                "width",
                "height",
                "role",
                "start",
                "colspan",
                "rowspan",
            } or k.startswith(("aria-", "data-")):
                clean[k] = v
        self.out.append(
            "<"
            + tag
            + "".join(f' {k}="{escape(v, quote=True)}"' for k, v in clean.items())
            + ">"
        )

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "h1" and self.drop_title:
            self.drop_title = 0
            return
        if self.drop_title:
            return
        if tag in DROP:
            if self.drop:
                self.drop -= 1
            return
        if self.drop:
            return
        if tag == "h1":
            tag = "h2"
        if tag not in VOID:
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.drop and not self.drop_title:
            self.out.append(escape(data))


def render_markdown_text(
    path: str,
    markdown_text: str,
    *,
    current_page: str,
    namespace: str | None = None,
    follow_document: Callable[[str, str], bool] | None = None,
    document_routes: Mapping[str, str] | None = None,
    omit_title: bool = True,
) -> MarkdownFragment:
    path = str(PurePosixPath(path))
    namespace = namespace or document_namespace(path)
    follow = follow_document or (lambda _s, _t: True)
    if not path.endswith(".md"):
        raise ValueError(f"Markdown source must end in .md: {path}")
    md = markdown.Markdown(
        extensions=EXTENSIONS,
        extension_configs={
            "toc": {"permalink": True, "toc_depth": 3},
            "pymdownx.highlight": {"anchor_linenums": True},
            "pymdownx.tabbed": {"alternate_style": True},
        },
    )
    safe = _SafeHTML(
        path, namespace, follow, current_page, document_routes or {}, omit_title
    )
    safe.feed(md.convert(markdown_text))
    safe.close()
    return MarkdownFragment(
        "".join(safe.out),
        tuple(sorted(safe.documents)),
        tuple(sorted(safe.assets)),
        tuple(sorted(safe.external)),
    )


def render_tagged_markdown(
    path: str,
    *,
    current_page: str,
    namespace: str | None = None,
    follow_document: Callable[[str, str], bool] | None = None,
    document_routes: Mapping[str, str] | None = None,
    omit_title: bool = True,
) -> MarkdownFragment:
    return render_markdown_text(
        path,
        edit_article(path)[0],
        current_page=current_page,
        namespace=namespace,
        follow_document=follow_document,
        document_routes=document_routes,
        omit_title=omit_title,
    )


def render_article(
    path: str,
    *,
    current_page: str,
    follow_document: Callable[[str, str], bool] | None = None,
    document_routes: Mapping[str, str] | None = None,
) -> MarkdownFragment:
    return render_tagged_markdown(
        path,
        current_page=current_page,
        follow_document=follow_document,
        document_routes=document_routes,
        omit_title=True,
    )


def build_support_bundle(
    entries: list[str] | tuple[str, ...],
    *,
    max_documents: int | None = None,
    source_text: Callable[[str], str | None] | None = None,
    follow_document: Callable[[str, str], bool] | None = None,
    document_routes: Mapping[str, str] | None = None,
) -> SupportBundle:
    pending = list(dict.fromkeys(entries))
    seen = set()
    source_paths = {}
    fragments = {}
    assets = {}
    external = set()
    while pending:
        path = pending.pop(0)
        if path in seen:
            continue
        if max_documents is not None and len(seen) >= max_documents:
            raise ValueError(f"support document graph exceeds {max_documents} files")
        markdown = source_text(path) if source_text else edit_article(path)[0]
        if markdown is None:
            continue
        f = render_markdown_text(path, markdown, current_page=support_document_path(path),
                                 follow_document=follow_document, document_routes=document_routes, omit_title=False)
        seen.add(path)
        source_paths[support_document_path(path)] = path
        fragments[support_document_path(path)] = f.html
        pending.extend(x for x in f.documents if x not in seen)
        for a in f.assets:
            assets[support_asset_path(a)] = tagged_bytes(a)
        external.update(f.external_links)
    return SupportBundle(source_paths, fragments, assets, tuple(sorted(external)))


__all__ = [
    "MarkdownFragment",
    "SupportBundle",
    "render_tagged_markdown",
    "render_article",
    "build_support_bundle",
    "document_namespace",
    "support_document_path",
    "support_asset_path",
]
