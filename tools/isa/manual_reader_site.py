"""Place the repository's authored Chinese articles into the flat ISA site."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from html import escape
from pathlib import PurePosixPath
import re

from manual_markdown import build_support_bundle, render_article, support_asset_path
from manual_tag import tagged_bytes


class ArticleLibrary:
    def __init__(self, articles):
        self.articles = articles
        destinations = defaultdict(list)
        for name, (mnemonic, article) in articles.items():
            if article is not None:
                # A grouped article may serve several encodings. Its links go
                # to the page bearing its own name whenever that page exists.
                matches = PurePosixPath(article.source_path).stem.upper() == mnemonic
                destinations[article.source_path].append((not matches, name))
        self.routes = {path: min(options)[1] for path, options in destinations.items()}
        self.fragments = {}
        self.files = {}
        self.audit = {}
        dependencies = set()
        for path, destination in sorted(self.routes.items()):
            fragment = render_article(
                path, current_page=destination, document_routes=self.routes
            )
            self.fragments[path] = fragment.html
            dependencies.update(fragment.documents)
            for asset in fragment.assets:
                self.files[support_asset_path(asset)] = tagged_bytes(asset)
        support = build_support_bundle(
            sorted(dependencies - self.routes.keys()), document_routes=self.routes
        )
        self.files.update(support.assets)
        self.support = support.fragments

    def render(self, filename, *, source_context="", conflict=False):
        item = self.articles.get(filename)
        if not item or not item[1]:
            return ""
        _, article = item
        path = article.source_path
        fragment = self.fragments[path]
        source = tagged_bytes(path)
        digest = sha256(source).hexdigest()
        raw = f"article-source/{digest}.md"
        self.files[raw] = source
        self.audit[filename] = {
            "source_path": path,
            "source_sha256": digest,
            "classification": "conflicting-current"
            if conflict
            else article.classification,
            "rendered_sha256": sha256(fragment.encode()).hexdigest(),
            "source_asset": raw,
        }
        label = f'<p class="article-source">中文站原文 · <a href="{raw}">{escape(article.title)}</a></p>'
        context = (
            f'<p class="version-context">{escape(source_context)}</p>'
            if source_context
            else ""
        )
        body = (
            f'<section class="authored-reader" data-source-path="{escape(path)}">{label}{context}'
            "<!-- authored:start -->" + fragment + "<!-- authored:end --></section>"
        )
        if conflict:
            return (
                '<details class="historical-article"><summary>对照中文站原页（含旧版汇编和编码）</summary>'
                + body
                + "</details>"
            )
        return body


def authored_synopsis(article, default):
    if not article or not article.intro:
        return default
    # Preserve the source wording. Stop before any pseudocode or figures that
    # happen to share the explanation section on a Tile page.
    # Titles often have an English long name in parentheses, followed by the
    # actual Chinese explanation. Index just the explanation; the complete
    # bilingual heading remains unmodified inside the original article.
    text = article.intro.split("。")[0].strip()
    gloss = re.match(
        r"^[^()（）]{1,90}[（(][A-Za-z][A-Za-z0-9 ,/+:._’'–-]+[）)]\s*(.+)$", text
    )
    if gloss and re.search(r"[一-鿿]", gloss[1]):
        text = gloss[1]

    for marker in ("实现伪代码", "实现示意图", "![", "```", " { width="):
        text = text.split(marker, 1)[0].strip()
    return text + "。" if text else default
