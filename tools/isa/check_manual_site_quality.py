#!/usr/bin/env python3
"""Independent architecture, editorial, SSR, supplement and figure site audit."""

from __future__ import annotations

import argparse
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_manual_authored import _normalize_local_targets, extract_authored
from manual_architecture import (
    architecture_pages,
    architecture_routes,
    register_catalog_records,
    render_architecture_page,
)
from manual_editorial import SKILL_COMMIT, SKILL_SHA256, SKILL_URL, edit_article
from manual_markdown import render_tagged_markdown
from manual_supplements import supplement_mapping, validate_supplements
from manual_tag import tagged_bytes


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class _SSRTable(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = {}
        self.key = None
        self.cells = []
        self.in_cell = False
        self.buf = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "tr" and "data-register-key" in values:
            self.key = values["data-register-key"]
            self.cells = []
        elif self.key and tag == "td":
            self.in_cell = True
            self.buf = []

    def handle_endtag(self, tag):
        if tag == "td" and self.in_cell:
            self.cells.append(re.sub(r"\s+", " ", "".join(self.buf)).strip())
            self.in_cell = False
        elif tag == "tr" and self.key:
            self.rows[self.key] = tuple(self.cells)
            self.key = None

    def handle_data(self, data):
        if self.in_cell:
            self.buf.append(data)


class _Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        for key in ("href", "src"):
            if values.get(key):
                self.refs.append(values[key])


def _code_blocks(html: str) -> tuple[str, ...]:
    return tuple(
        re.findall(
            r"<pre[^>]*>.*?<code[^>]*>(.*?)</code>.*?</pre>", html, flags=re.DOTALL
        )
    )


def _check_architecture(site: Path, errors: list[str]):
    audit_path = site / "architecture-audit.json"
    if not audit_path.is_file():
        errors.append("architecture-audit.json: missing")
        return
    audit = _json(audit_path)
    routes = architecture_routes()
    expected_routes = set(routes.values())
    if set(audit) != expected_routes:
        errors.append(
            f"architecture routes differ: audit={len(audit)} expected={len(routes)}"
        )
    pages = {page.route: page for page in architecture_pages() if page.source_path}
    for route, actual_route in sorted(routes.items()):
        record = audit.get(actual_route)
        page = pages.get(actual_route)
        path = site / actual_route
        if record is None or page is None or not path.is_file():
            errors.append(f"{actual_route}: architecture page/audit missing")
            continue
        source_bytes = tagged_bytes(route)
        if (
            record.get("source_path") != route
            or record.get("source_sha256") != sha256(source_bytes).hexdigest()
        ):
            errors.append(f"{actual_route}: architecture source provenance differs")
        text = path.read_text(encoding="utf-8")
        try:
            embedded_path, fragment = extract_authored(text)
        except ValueError as exc:
            errors.append(f"{actual_route}: {exc}")
            continue
        if (
            embedded_path != route
            or record.get("rendered_sha256") != sha256(fragment.encode()).hexdigest()
        ):
            errors.append(f"{actual_route}: architecture rendered provenance differs")
        rendered = render_architecture_page(page)
        if rendered is None or _normalize_local_targets(
            fragment
        ) != _normalize_local_targets(rendered.html):
            errors.append(
                f"{actual_route}: architecture original differs from tag re-render"
            )
        links = _Links()
        links.feed(text)
        for ref in links.refs:
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc or ref.startswith("#"):
                continue
            target = site / unquote(parsed.path)
            if not target.exists():
                errors.append(f"{actual_route}: broken relative reference {ref}")
    warning_facts = {
        "arch-tile-registers.html": (
            "edition-difference",
            "SizeCode 1–10",
            "S0–S63",
            "旧模型",
            "historical-article",
        ),
        "arch-core-state.html": (
            "edition-difference",
            "历史实现示例",
            "VEC、SFU、TLSU 和 CUBE",
            "旧式",
            "historical-article",
        ),
        "arch-constraints.html": (
            "edition-difference",
            "隐式 ACC",
            "显式本地 Tile",
            "historical-article",
        ),
        "arch-predicate.html": (
            "edition-difference",
            "谓词位 2×i",
            "非活动通道",
            "authored-reader",
        ),
    }
    for route, facts in warning_facts.items():
        text = (
            (site / route).read_text(encoding="utf-8")
            if (site / route).is_file()
            else ""
        )
        for fact in facts:
            if fact not in text:
                errors.append(f"{route}: missing version/source-range warning {fact!r}")


def _check_ssr(site: Path, errors: list[str]):
    path = site / "arch-ssr.html"
    if not path.is_file():
        errors.append("arch-ssr.html: missing")
        return
    parser = _SSRTable()
    parser.feed(path.read_text(encoding="utf-8"))
    expected = register_catalog_records()
    if len(parser.rows) != 100 or len(expected) != 100:
        errors.append(
            f"SSR count differs: html={len(parser.rows)} source={len(expected)}"
        )
    for item in expected:
        cells = parser.rows.get(item.key)
        wanted = (item.name, item.address, item.access, item.scope)
        if cells is None or cells[:4] != wanted:
            errors.append(f"SSR {item.key}: {cells[:4] if cells else None} != {wanted}")


def _check_supplements(site: Path, errors: list[str], pto_root: Path | None):
    manifest = site / "supplements.json"
    if not manifest.is_file():
        errors.append("supplements.json: missing")
        return
    records = _json(manifest)
    expected_paths = {
        str(Path(path).relative_to(Path(__file__).resolve().parents[2]))
        for path in supplement_mapping().values()
    }
    if len(records) != 22 or set(records.values()) != expected_paths:
        errors.append("supplement manifest does not cover the exact 22 sources")
    errors.extend("supplements: " + error for error in validate_supplements(pto_root))
    required = ("用途", "输入与输出", "执行结果", "示例", "合法性与异常", "0.59.1 来源")
    for filename, source in records.items():
        path = site / filename
        if not path.is_file():
            errors.append(f"{filename}: supplement page missing")
            continue
        text = path.read_text(encoding="utf-8")
        if f'data-source-path="{source}"' not in text or "0.59.1 增补" not in text:
            errors.append(f"{filename}: supplement source/label missing")
        for heading in required:
            if f">{heading}<" not in text:
                errors.append(f"{filename}: supplement content area {heading} missing")
        local = Path(__file__).resolve().parents[2] / source
        meta = json.loads(
            re.match(r"<!-- LINXISA-SUPPLEMENT: (\{.*\}) -->", local.read_text()).group(
                1
            )
        )
        for literal in (
            meta["identity"],
            meta["pto_source_path"],
            meta["pto_source_commit"],
        ):
            if literal not in text:
                errors.append(
                    f"{filename}: supplement source identity {literal} missing"
                )
        pto_url = f"https://github.com/PTO-ISA/pto-spec/blob/{meta['pto_source_commit']}/{meta['pto_source_path']}"
        if pto_url not in text:
            errors.append(f"{filename}: linked PTO source missing")
        example = re.search(r">示例<.*?(?=>合法性与异常<)", text, flags=re.DOTALL)
        if example is None or not re.search(r"[\u4e00-\u9fff]|<code", example.group(0)):
            errors.append(f"{filename}: supplement example is empty")


def _check_mgather(site: Path, errors: list[str]):
    from html import unescape

    def reader(name):
        filename = "tile-" + name.lower().replace("_", "-") + ".html"
        _, body = extract_authored((site / filename).read_text(encoding="utf-8"))
        return unescape(re.sub(r"<[^>]+>", "", body))

    base = reader("MGATHER")
    for fact in ("S32", "U32", "S64", "U64", "字节", "MinIndex", "MaxIndex"):
        if fact not in base:
            errors.append(f"tile-mgather.html: missing indexed-transfer rule {fact!r}")
    atomic = ("ADD", "AND", "CAS", "DEC", "EXCH", "INC", "MAX", "MIN", "OR", "XOR")
    for suffix in atomic:
        name = "MGATHER_" + suffix
        body = reader(name)
        if name not in body or "原子" not in body or "旧值" not in body:
            errors.append(
                f"{name}: missing atomic read/modify/write and returned old value"
            )
    for name in ("MGATHER_MASK", "MSCATTER_MASK"):
        body = reader(name)
        if name not in body or "掩码" not in body or "地址" not in body:
            errors.append(f"{name}: missing masked address behavior")


def _check_editorial(site: Path, errors: list[str]):
    path = site / "editorial-audit.json"
    if not path.is_file():
        errors.append("editorial-audit.json: missing")
        return
    audit = _json(path)
    if (audit.get("skill"), audit.get("skill_commit"), audit.get("skill_sha256")) != (
        SKILL_URL,
        SKILL_COMMIT,
        SKILL_SHA256,
    ):
        errors.append("editorial audit skill provenance differs")
    pages = audit.get("pages", {})
    html_files = {
        str(path.relative_to(site)).replace("\\", "/") for path in site.rglob("*.html")
    }
    if set(pages) != html_files:
        errors.append(
            f"editorial audit HTML inventory differs: audit={len(pages)} site={len(html_files)}"
        )
    for filename, record in pages.items():
        target = site / filename
        if (
            not target.is_file()
            or record.get("html_sha256") != sha256(target.read_bytes()).hexdigest()
        ):
            errors.append(f"{filename}: editorial page hash differs")
            continue
        source = record.get("source_path")
        if source and record.get("origin") == "tagged-chinese-source":
            if record.get("applied_source_edits") != dict(edit_article(source)[1]):
                errors.append(f"{filename}: editorial edit record differs")
            try:
                rendered = render_tagged_markdown(
                    source,
                    current_page=filename,
                    document_routes=architecture_routes(),
                    omit_title=filename.startswith("op-")
                    or filename.startswith("tile-")
                    or filename.startswith("arch-"),
                ).html
                page = target.read_text(encoding="utf-8")
                if _normalize_local_targets(rendered) not in _normalize_local_targets(
                    page
                ):
                    errors.append(
                        f"{filename}: editorial prose differs from reviewed source render"
                    )
                expected_codes = _code_blocks(rendered)
                actual_codes = _code_blocks(page)
                cursor = 0
                for code in expected_codes:
                    try:
                        cursor = actual_codes.index(code, cursor) + 1
                    except ValueError:
                        errors.append(
                            f"{filename}: original code block changed or missing"
                        )
                        break
            except Exception as exc:
                errors.append(f"{filename}: editorial source re-render failed: {exc}")


def _check_canvas(site: Path, errors: list[str]):
    path = site / "canvas-audit.json"
    if not path.is_file():
        errors.append("canvas-audit.json: missing")
        return
    audit = _json(path)
    figures = audit.get("figures", [])
    if not figures:
        errors.append("canvas-audit.json: no figures")
    for figure in figures:
        fid = str(figure.get("id", ""))
        image = site / str(figure.get("image", ""))
        image_digest = sha256(image.read_bytes()).hexdigest() if image.is_file() else ""
        if not image_digest or figure.get("sha256") != image_digest:
            errors.append(f"canvas {fid}: image/hash differs")
        sources = figure.get("source_files", [])
        if not sources or any(not (site / str(source)).is_file() for source in sources):
            errors.append(f"canvas {fid}: local figure source records missing")
        manifest_action = figure.get("review_decision")
        if manifest_action not in {"accept", "stop"}:
            errors.append(
                f"canvas {fid}: manifest review decision is not a terminal success"
            )
        if figure.get("accepted_image_sha256") != image_digest:
            errors.append(f"canvas {fid}: accepted image hash differs")

        review_path = site / str(figure.get("review_file", ""))
        review = None
        if not review_path.is_file():
            errors.append(f"canvas {fid}: packaged review missing")
        else:
            review_bytes = review_path.read_bytes()
            if figure.get("review_sha256") != sha256(review_bytes).hexdigest():
                errors.append(f"canvas {fid}: packaged review hash differs")
            try:
                review = json.loads(review_bytes)
            except (UnicodeDecodeError, json.JSONDecodeError):
                errors.append(f"canvas {fid}: packaged review is not valid JSON")
        if isinstance(review, dict):
            decision = review.get("decision")
            official_action = (
                decision.get("action") if isinstance(decision, dict) else None
            )
            if official_action not in {"accept", "stop"}:
                errors.append(
                    f"canvas {fid}: official decision.action is not a terminal success"
                )
            elif official_action != manifest_action:
                errors.append(f"canvas {fid}: manifest and official decisions differ")
            if review.get("blocking_findings") != []:
                errors.append(f"canvas {fid}: accepted review has blocking findings")
            if review.get("artifact_id") != fid:
                errors.append(f"canvas {fid}: review artifact id differs")
            if review.get("image_sha256") != image_digest:
                errors.append(f"canvas {fid}: reviewed PNG hash differs")

            decision_ref = review.get("decision_ref")
            raw_decision = review.get("raw_decision")
            if not isinstance(decision_ref, str) or not decision_ref.strip():
                errors.append(f"canvas {fid}: original decision reference missing")
            raw_action = (
                raw_decision.get("decision") if isinstance(raw_decision, dict) else None
            )
            raw_action = (
                raw_action.get("action") if isinstance(raw_action, dict) else None
            )
            if raw_action != official_action:
                errors.append(f"canvas {fid}: original and packaged decisions differ")

            if official_action == "stop":
                reviewed_attempt = review.get("reviewed_attempt")
                best_attempt = (
                    raw_decision.get("best_attempt")
                    if isinstance(raw_decision, dict)
                    else None
                )
                if (
                    type(reviewed_attempt) is not int
                    or reviewed_attempt < 1
                    or not isinstance(best_attempt, dict)
                    or best_attempt.get("attempt") != reviewed_attempt
                ):
                    errors.append(
                        f"canvas {fid}: stopped review does not bind the reviewed best attempt"
                    )
                stop_snapshot = review.get("provenance_snapshot")
                image_path = (
                    best_attempt.get("image_path")
                    if isinstance(best_attempt, dict)
                    else None
                )
                if (
                    not isinstance(stop_snapshot, dict)
                    or stop_snapshot.get("best_attempt_image_sha256") != image_digest
                    or not isinstance(image_path, str)
                    or stop_snapshot.get("best_attempt_file") != Path(image_path).name
                ):
                    errors.append(
                        f"canvas {fid}: stopped best attempt provenance differs"
                    )
                if review.get("best_attempt_technically_correct") is not True:
                    errors.append(
                        f"canvas {fid}: stopped best attempt is not marked technically correct"
                    )

                technical = review.get("independent_technical_review")
                if not isinstance(technical, dict):
                    errors.append(
                        f"canvas {fid}: stopped review lacks independent technical signoff"
                    )
                else:
                    if technical.get("verdict") != "approve":
                        errors.append(
                            f"canvas {fid}: stopped technical review is not approved"
                        )
                    if technical.get("image_sha256") != image_digest:
                        errors.append(
                            f"canvas {fid}: stopped technical review PNG hash differs"
                        )
                    if technical.get("blocking_findings") != []:
                        errors.append(
                            f"canvas {fid}: stopped technical review has blocking findings"
                        )
                    limitations = technical.get("limitations")
                    if not isinstance(limitations, list) or not any(
                        isinstance(note, str) and note.strip() for note in limitations
                    ):
                        errors.append(
                            f"canvas {fid}: stopped review lacks an explicit limitation"
                        )

            snapshot = review.get("provenance_snapshot")
            if not isinstance(snapshot, dict):
                errors.append(f"canvas {fid}: provenance snapshot missing")
            else:
                if snapshot.get("artifact_id") != fid:
                    errors.append(f"canvas {fid}: provenance artifact id differs")
                if snapshot.get("image_sha256") != image_digest:
                    errors.append(f"canvas {fid}: provenance PNG hash differs")
                if snapshot.get("decision_ref") != decision_ref:
                    errors.append(
                        f"canvas {fid}: provenance decision reference differs"
                    )
        elif review is not None:
            errors.append(f"canvas {fid}: packaged review must be a JSON object")
        pages = figure.get("pages", [])
        if not pages:
            errors.append(f"canvas {fid}: no consuming pages")
        for page_name in pages:
            page = site / str(page_name)
            text = page.read_text(encoding="utf-8") if page.is_file() else ""
            pattern = rf'<img[^>]*class="[^"]*canvas-figure-image[^"]*"[^>]*(?:src="{re.escape(str(figure.get("image", "")))}"|src="[^"]*{re.escape(image.name)}")[^>]*>'
            match = re.search(pattern, text)
            if match is None or not re.search(
                r'\b(?:alt|title)="[^"]+"', match.group(0)
            ):
                errors.append(
                    f"canvas {fid}: image not accessibly referenced by {page_name}"
                )
    all_pages = " ".join(
        str(page) for figure in figures for page in figure.get("pages", [])
    )
    for required in ("tile-mgather.html", "op-c-movr.html"):
        if required not in all_pages:
            errors.append(f"canvas figures: required consumer {required} missing")
    if not any(
        str(page).startswith("arch-")
        for figure in figures
        for page in figure.get("pages", [])
    ):
        errors.append("canvas figures: no architecture page consumer")


def check_site(site: Path, pto_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    _check_architecture(site, errors)
    _check_ssr(site, errors)
    _check_supplements(site, errors, pto_root)
    _check_mgather(site, errors)
    _check_editorial(site, errors)
    _check_canvas(site, errors)
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--pto-root", type=Path)
    args = parser.parse_args(argv)
    errors = check_site(args.site.resolve(), args.pto_root)
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        print(f"manual site quality failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print("OK: architecture, SSR, supplements, editorial, MGATHER and Canvas quality")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
