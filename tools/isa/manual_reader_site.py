"""Place the repository's authored Chinese articles into the flat ISA site."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from html import escape
from pathlib import PurePosixPath
import re

from manual_editorial import edit_article
from manual_markdown import (
    build_support_bundle,
    render_markdown_text,
    support_asset_path,
)
from manual_tag import tagged_bytes
from manual_v0592_edition import read as released_v0592_bytes


class ArticleLibrary:
    def __init__(
        self, articles, chapter_routes=None, *, revisions=None, source_text=None
    ):
        self.articles = articles
        self.revisions = revisions or {}
        self.original_source = released_v0592_bytes if source_text else tagged_bytes
        self.source_text = source_text
        self.follow = (
            (lambda source, target: source_text(target) is not None)
            if source_text
            else None
        )
        self.revised_fragments = {}
        destinations = defaultdict(list)
        for name, (mnemonic, article) in articles.items():
            if article is not None:
                # A grouped article may serve several encodings. Its links go
                # to the page bearing its own name whenever that page exists.
                matches = PurePosixPath(article.source_path).stem.upper() == mnemonic
                destinations[article.source_path].append((not matches, name))
        self.routes = {path: min(options)[1] for path, options in destinations.items()}
        self.routes.update(chapter_routes or {})
        self.fragments = {}
        self.files = {}
        self.audit = {}
        dependencies = set()
        original_paths = set((chapter_routes or {}).keys()) | {
            a.source_path
            for name, (_, a) in articles.items()
            if a and self.revisions.get(name) is None
        }
        for path, destination in sorted(self.routes.items()):
            if source_text and path not in original_paths:
                continue
            markdown = source_text(path) if source_text else edit_article(path)[0]
            if markdown is None:
                raise ValueError(f"Excluded source in article routes: {path}")
            fragment = render_markdown_text(
                path,
                markdown,
                current_page=destination,
                document_routes=self.routes,
                follow_document=self.follow,
            )
            self.fragments[path] = fragment.html
            dependencies.update(fragment.documents)
            for asset in fragment.assets:
                self.files[support_asset_path(asset)] = tagged_bytes(asset)
        for filename, markdown in self.revisions.items():
            if markdown is None:
                continue
            article = articles[filename][1]
            fragment = render_markdown_text(
                article.source_path,
                markdown,
                current_page=filename,
                document_routes=self.routes,
                follow_document=self.follow,
            )
            self.revised_fragments[filename] = fragment.html
            dependencies.update(fragment.documents)
            for asset in fragment.assets:
                self.files[support_asset_path(asset)] = tagged_bytes(asset)
        support = build_support_bundle(
            sorted(dependencies - self.routes.keys()),
            document_routes=self.routes,
            source_text=source_text,
            follow_document=self.follow,
        )
        self.files.update(support.assets)
        self.support = support.fragments
        self.support_sources = support.source_paths

    def render(self, filename):
        item = self.articles.get(filename)
        if not item or not item[1]:
            return ""
        _, article = item
        path = article.source_path
        original = self.original_source(path)
        revised = self.revisions.get(filename)
        source = (
            revised.encode()
            if revised is not None
            else self.source_text(path).encode()
            if self.source_text
            else original
        )
        fragment = (
            self.revised_fragments[filename]
            if revised is not None
            else self.fragments[path]
        )
        digest = sha256(source).hexdigest()
        raw = f"article-source/{digest}.md"
        self.files[raw] = source
        self.audit[filename] = {
            "source_path": path,
            "source_sha256": sha256(original).hexdigest(),
            "classification": article.classification,
            "reader": "release-revision" if revised is not None else "authored",
            "reader_sha256": digest,
            "rendered_sha256": sha256(fragment.encode()).hexdigest(),
            "source_asset": raw,
        }
        return (
            f'<section class="authored-reader" data-source-path="{escape(path)}">'
            "<!-- authored:start -->" + fragment + "<!-- authored:end --></section>"
            f'<p class="article-source"><a href="{raw}">本页中文稿</a></p>'
        )


def authored_synopsis(article):
    if not article or not article.intro:
        return ""
    # Preserve the source wording. Stop before any pseudocode or figures that
    # happen to share the explanation section on a Tile page.
    # Titles often have an English long name in parentheses, followed by the
    # actual Chinese explanation. Index just the explanation; the complete
    # bilingual heading remains unmodified inside the original article.
    from manual_editorial import EDITS

    text = article.intro.split("。")[0].strip()
    hits = dict(edit_article(article.source_path)[1])
    for rule in EDITS:
        if rule.key in hits:
            text = text.replace(rule.before, rule.after)
    gloss = re.match(
        r"^[^()（）]{1,90}[（(][A-Za-z][A-Za-z0-9 ,/+:._’'–-]+[）)]\s*(.+)$", text
    )
    if gloss and re.search(r"[一-鿿]", gloss[1]):
        text = gloss[1]

    for marker in ("实现伪代码", "实现示意图", "![", "```", " { width="):
        text = text.split(marker, 1)[0].strip()
    return text + "。" if text else ""
