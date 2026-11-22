#!/usr/bin/env python3
"""Build the offline LinxISA 0.59.1 reference from the published Git tag."""

from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from html import escape
from itertools import groupby
import json
from importlib.metadata import version
from pathlib import Path
import re
import subprocess
from urllib.parse import quote
import zipfile

from manual_tag import (
    RELEASE_TAG as TAG,
    tagged_bytes,
    tagged_json,
    verified_tag_commit,
)
from manual_block_zh import translate_block
from manual_terms_zh import FILTER, group_name
from manual_encoding import render_encoding, validate_catalog
from manual_linx_sail import sail_detail
from manual_reader import operation_detail
from manual_architecture import architecture_routes
from manual_architecture_view import architecture_bodies
from manual_canvas_site import include_canvas
from manual_editorial import (
    SKILL_COMMIT,
    SKILL_SHA256,
    SKILL_URL,
    edit_article,
    edit_markdown,
)
from manual_supplements import instruction_supplement, tile_supplement
from manual_markdown import render_markdown_text
from manual_version_notes import indexed_transfer_note, release_constraints
from manual_authored import authored_for, authored_tile
from manual_reader_site import ArticleLibrary, authored_synopsis
from manual_navigation import BY_KEY, cat_file, category_links, index_pages
from manual_diagrams import make_diagrams


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "docs/architecture/isa-manual/reference"
DEFAULT_OUT = ASSETS.parent / "build/instruction-reference"
CATALOG = "isa/v0.59/linxisa-v0.59.json"
TILES = "isa/v0.59/state/pto_tile_operations.json"
MANIFEST = "isa/v0.59/release_manifest.json"
LOCK = "isa/v0.59/pto-spec.lock.json"
SCOPE_SUFFIX = {"Private": "PRIVATE", "IntraCore": "INTRA", "InterCore": "INTER"}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def op_page(name):
    return f"op-{slug(name)}.html"


def tile_page(name):
    return f"tile-{slug(name)}.html"


def spelling(row):
    name = row["mnemonic"]
    if "pto_scope" in row:
        return name + "." + SCOPE_SUFFIX[row["pto_scope"]]
    return name


def link(href, label):
    return f'<a href="{escape(href)}">{escape(label)}</a>'


def jump(groups):
    return (
        '<div class="jump">'
        + "".join(link("#" + key, label) for key, label in groups)
        + "</div>"
    )


def search(prompt, classes=()):
    options = ""
    if classes:
        options = (
            '<label>分类 <select><option value="">全部</option>'
            + "".join(
                f'<option value="{escape(k)}">{escape(FILTER[k])}（{escape(k)}）</option>'
                for k in sorted(classes)
            )
            + "</select></label>"
        )
    return (
        '<div class="search" hidden><label>查找 '
        f'<input type="search" placeholder="{escape(prompt)}"></label>'
        + options
        + '<output aria-live="polite"></output></div>'
    )


def page(title, body, commit, prefix=""):
    nav = (
        ("architecture.html", "架构目录"),
        ("arch-state.html", "架构状态"),
        ("execution-model.html", "执行模型"),
        ("index.html", "指令分类"),
        ("mnemonics.html", "全部助记符"),
        ("encoding.html", "编码索引"),
        ("tile.html", "Tile 操作"),
        ("sources.html", "版本与来源"),
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · LinxISA 0.59.1</title><link rel="stylesheet" href="{prefix}manual.css">
<script defer src="{prefix}index-filter.js"></script></head><body>
<a class="skip" href="#content">跳至正文</a><header>
<a class="brand" href="{prefix}index.html">LinxISA</a><span class="edition">0.59.1 · 指令集参考手册</span>
<nav class="class-nav" aria-label="指令类型">{category_links(prefix)}</nav><nav aria-label="手册目录">{"".join(link(prefix + url, label) for url, label in nav)}</nav></header>
<main id="content"><h1>{escape(title)}</h1>{body}</main>
<footer>{link(prefix + "sources.html", TAG)} · 规范提交 <code>{escape(commit[:12])}</code> · {link("#content", "回到页首")}</footer></body></html>
"""


def listed_item(name, href, text, kind, terms=""):
    needle = escape(" ".join((name, kind, terms, text)).lower())
    return (
        f'<li data-kind="{escape(kind)}" data-search="{needle}">'
        f'<span class="mnemonic">{link(href, name)}</span><span>{escape(text)}</span></li>'
    )


def alphabetic_index(entries, intro, prompt):
    entries.sort(key=lambda e: e[0])
    sections = []
    for letter, group in groupby(entries, key=lambda e: e[0][0]):
        rows = "".join(listed_item(*entry) for entry in group)
        sections.append(
            (
                letter,
                f'<section class="alphabet" data-section id="letter-{letter}">'
                f'<h2>{letter}</h2><ul class="index-list">{rows}</ul></section>',
            )
        )
    return (
        intro
        + search(prompt, {e[3] for e in entries})
        + jump([("letter-" + letter, letter) for letter, _ in sections])
        + "".join(section for _, section in sections)
    )


def fixed_bits(row):
    """Concatenate part values in increasing fetch order, part zero at bit zero."""
    mask = match = offset = 0
    for part in row["encoding"]["parts"]:
        mask |= int(part["mask"], 16) << offset
        match |= int(part["match"], 16) << offset
        offset += part["width_bits"]
    return mask, match


def tile_header(op, row, owner):
    """Specialize the command's fixed bits by the published TEPL selector."""
    mask, match = fixed_bits(row)
    labels = []
    if op["family"] == "TEPL":
        part = row["encoding"]["parts"][0]
        for name in ("Mode", "Function"):
            value = op[name.lower()]
            field = next(f for f in part["fields"] if f["name"] == name)
            for piece in field["pieces"]:
                width = piece["width"]
                bits = (1 << width) - 1
                mask |= bits << piece["insn_lsb"]
                match |= ((value >> piece["value_lsb"]) & bits) << piece["insn_lsb"]
            labels.append(f"{name} = {value}")
    else:
        labels.append(f"Function = {op['function']}")
    fmt = row["length_bits"] // 4
    block = "\n".join(translate_block(owner["block"]))
    original = "\n".join(owner["block"])
    return (
        "<h2>命令编码</h2><p>承载指令 "
        + link(op_page(row["mnemonic"]), row["mnemonic"])
        + "　"
        + escape(" · ".join(labels))
        + f"</p><pre><code>(word &amp; 0x{mask:0{fmt}x}) == 0x{match:0{fmt}x}</code></pre>"
        + '<p class="meta">上式匹配指令和操作选择器。数据类型、绑定命令及布局仍须满足本操作的合法性条件。</p>'
        + "<h3>指令块组成</h3><pre><code>"
        + escape(block)
        + "</code></pre>"
        + '<details class="tile-block-source"><summary>查看规范中的块模板原文</summary>'
        + '<pre lang="en"><code>'
        + escape(original)
        + "</code></pre></details>"
    )


def encoding_index(instructions):
    sections = []
    kinds = {r["encoding_kind"] for r in instructions}
    intro = (
        "<p>本表按指令长度分组，组内按固定比特的匹配值排序。"
        "先取出的片段（Part 0）占低位。译码时先检查 <code>(word &amp; mask) == match</code>。"
        "各形式的字段取值限制见指令页。</p>"
    )
    for width in sorted({r["length_bits"] for r in instructions}):
        rows = []
        forms = sorted(
            (r for r in instructions if r["length_bits"] == width),
            key=lambda r: (*reversed(fixed_bits(r)), r["id"]),
        )
        for r in forms:
            mask, match = (f"0x{v:0{width // 4}x}" for v in fixed_bits(r))
            name = spelling(r)
            kind = r["encoding_kind"]
            needle = escape(
                f"{name} {r['asm']} {kind} {r['id']} {mask} {match}".lower()
            )
            href = op_page(name) + "#" + r["id"]
            rows.append(
                f'<tr data-search="{needle}" data-kind="{kind}">'
                f"<td>{link(href, r['asm'])}</td><td><code>{match}</code></td>"
                f"<td><code>{mask}</code></td><td>{kind}</td></tr>"
            )
        sections.append(
            f'<section data-section id="w{width}"><h2>{width} 位 · {len(rows)} 个形式</h2>'
            '<div class="table-scroll"><table class="lookup bitlookup"><thead><tr>'
            "<th>汇编语法</th><th>匹配值（Match）</th><th>掩码（Mask）</th><th>格式</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div></section>"
        )
    return (
        intro
        + search("助记符、格式、Mask 或 Match", kinds)
        + jump(
            [
                (f"w{n}", f"{n} 位")
                for n in sorted({r["length_bits"] for r in instructions})
            ]
        )
        + "".join(sections)
    )


def unique_names(rows):
    by_name = defaultdict(list)
    for row in rows:
        by_name[spelling(row)].append(row)
    if len(set(map(op_page, by_name))) != len(by_name):
        raise ValueError("instruction page names collide")
    return by_name


def sources(commit, inputs, manifest, lock):
    repo = f"https://github.com/LinxISA/linx-isa/blob/{commit}/"
    facts = [
        ("LinxISA 标签", TAG),
        ("规范提交", commit),
        ("发布范围", "ISA 规范、编码与 Sail 模型"),
        ("PTO 源提交", lock["source"]["commit"]),
        ("ELF 编码 ABI", manifest["identity"]["encoding_abi"]),
        ("ELF 编码投影 SHA-256", manifest["identity"]["encoding_projection_sha256"]),
    ]
    body = (
        '<dl class="contract-grid">'
        + "".join(
            f"<dt>{escape(k)}</dt><dd><code>{escape(v)}</code></dd>" for k, v in facts
        )
        + "</dl>"
    )
    body += (
        "<h2>如何使用编码图</h2><p>从编号最小的片段开始取指，每段内左侧为高位。"
        "格顶标出段内位号。掩码为 1 的位必须与匹配值相同；其余位由操作数字段占用。"
        "分散在多个格子里的同名字段按标出的值位组合；字段域和形式约束决定合法取值。</p>"
        "<h2>语义与实现状态</h2><p>公共指令及带作用域的指令以本版锁定的 PTO 规范为依据。"
        "Linx 专有形式单列其依据和已知语义缺口。芯片实现还需检查操作数合法性、异常及提交时机。"
        "整机验证进度见发行说明。</p>"
    )
    body += (
        "<p>"
        + link(repo + "docs/zh/releases/v0.59.1.md", "0.59.1 发行说明")
        + " · "
        + link("https://linxisa.github.io/", "灵犀指令集架构中文站")
        + "</p>"
    )
    body += "<p>中文站可查阅指令的设计背景和早期版本的示例。编写 0.59.1 汇编或译码器时，请使用本手册列出的操作数和编码。</p>"
    body += '<h2>离线规范文件</h2><div class="table-scroll"><table><tr><th>文件</th><th>SHA-256</th></tr>'
    for path, data in inputs.items():
        body += f"<tr><td>{link('spec/' + Path(path).name, Path(path).name)}</td><td><code>{sha256(data).hexdigest()}</code></td></tr>"
    return (
        body
        + "</table></div><p>"
        + link("audit.json", "逐形式核对记录（JSON）")
        + "</p>"
    )


def scoped_record(row, source):
    fields = [
        ("汇编形式", source["asm"]),
        ("GM 共享属性", f"{source['scope']}（编码 {source['scope_code']}）"),
        ("语义处理器", source["semantic_handler"]),
        ("基础形式", source["base_form_id"]),
        ("契约状态", source["status"]),
    ]
    return (
        '<section class="scoped-contract"><h3>作用域封装</h3><dl>'
        + "".join(
            f"<dt>{k}</dt><dd><code>{escape(str(v))}</code></dd>" for k, v in fields
        )
        + "</dl></section>"
    )


def form_provenance(row, commit, common_paths):
    sid = row.get("pto_source_form_id")
    if sid:
        path = common_paths[sid]
        line = ""
    else:
        path = "isa/v0.58/" + row["source"]["file"]
        line = f"#L{row['source']['line']}"
    url = f"https://github.com/LinxISA/linx-isa/blob/{commit}/{path}{line}"
    return (
        f'<p class="source">目录形式 <code>{escape(row["id"])}</code> · '
        + link(url, sid or (path + line))
        + "</p>"
    )


def supplement_excerpt(path):
    if not path:
        raise ValueError("missing Chinese page for a released operation")
    text = Path(path).read_text().split("## 用途", 1)[1].strip()
    paragraph = " ".join(text.split("\n\n", 1)[0].splitlines())
    return paragraph.split("。", 1)[0].replace("`", "") + "。"


def supplement_reader(path, url, library):
    if not path:
        raise ValueError(f"{url}: missing source and release supplement")
    source = Path(path)
    relative = source.relative_to(ROOT).as_posix()
    data = source.read_bytes()
    raw = "article-source/" + sha256(data).hexdigest() + ".md"
    library.files[raw] = data
    fragment = render_markdown_text(
        relative,
        edit_markdown(relative, data.decode())[0],
        current_page=url,
        document_routes=library.routes,
    )
    if fragment.documents or fragment.assets:
        raise ValueError(f"{relative}: package supplemental dependencies")
    return (
        f'<section class="supplement-reader" data-source-path="{escape(relative)}"><p class="article-source">'
        + link(raw, "本地增补稿")
        + "</p>"
        + fragment.html
        + "</section>"
    )


def build():
    commit = verified_tag_commit()
    paths = (
        CATALOG,
        TILES,
        MANIFEST,
        LOCK,
        "isa/v0.59/state/pto_scalar_forms.json",
        "isa/v0.59/state/pto_command_forms.json",
    )
    inputs = {p: tagged_bytes(p) for p in paths}
    catalog, tiles, manifest, lock = (json.loads(inputs[p]) for p in paths[:4])
    if (
        catalog["version"] != TAG[1:]
        or manifest["publication"]["version"] != TAG[1:]
        or sha256(inputs[CATALOG]).hexdigest() != manifest["catalog"]["sha256"]
    ):
        raise ValueError("tag, release manifest and catalog identity disagree")
    for source in manifest["authoritative_sources"].values():
        path = source["path"]
        data = tagged_bytes(path)
        if sha256(data).hexdigest() != source["sha256"]:
            raise ValueError(f"standalone projection digest mismatch: {path}")
        inputs[path] = data
    reservations = "isa/v0.59/state/extension_encoding_reservations.json"
    inputs[reservations] = tagged_bytes(reservations)
    baseline = tagged_json("isa/v0.58/linxisa-v0.58.json")
    discrepancies = validate_catalog(catalog, baseline)
    if discrepancies:
        raise ValueError("catalog audit failed: " + "\n".join(discrepancies))
    rows = catalog["instructions"]
    forms = unique_names(rows)
    diagram_html, diagram_assets, diagram_audit = make_diagrams(catalog)
    common_paths = {}
    source_forms = {}
    for path in paths[4:]:
        doc = json.loads(inputs[path])
        for form in doc["forms"] + doc.get("scoped_forms", []):
            common_paths[form["form_id"]] = path
            source_forms[form["form_id"]] = form
    direct_ops = tiles["operations"]
    tile_refs = json.loads((ASSETS / "data/pto-v0591-tile-manual.json").read_text())
    tile_owners = {r["mnemonic"]: r for r in tile_refs["operations"]}
    asl_owners = json.loads((ASSETS / "pto-v0591-semantics.json").read_text())["forms"]
    base_by_id = {
        r["pto_source_form_id"]: r
        for r in rows
        if r.get("pto_source_form_id") and not r.get("pto_scope")
    }
    articles = {}
    for name, variants in forms.items():
        first = variants[0]
        base = base_by_id[first["pto_base_form_id"]] if "pto_scope" in first else first
        articles[op_page(name)] = (name, authored_for(base))
    for op in direct_ops:
        articles[tile_page(op["name"])] = (op["name"], authored_tile(op["name"]))
    example = articles[op_page("C.MOVR")][1]
    if not example or example.source_path != "docs/zh/isa/inst/misa_c/C.MOVR.md":
        raise ValueError("the tagged Chinese instruction source tree is missing")
    library = ArticleLibrary(articles, architecture_routes())
    zh_common = json.loads((ASSETS / "data/manual-semantics-zh.json").read_text())[
        "forms"
    ]
    zh_tile = json.loads((ASSETS / "data/manual-tile-semantics-zh.json").read_text())[
        "operations"
    ]
    supplement_audit = {}
    carrier_ops = defaultdict(list)
    bodies, entries, tile_list, audit = {}, [], [], []
    for op in direct_ops:
        name, carrier = op["name"], op["command_mnemonic"]
        if carrier not in forms:
            raise ValueError(f"{name} has no carrier {carrier}")
        carrier_ops[carrier].append(op)
        owner = tile_owners[name]
        url = tile_page(name)
        article = articles[url][1]
        desc = (
            authored_synopsis(article, "")
            if article
            else supplement_excerpt(tile_supplement(op))
        )
        tile_list.append((name, url, desc, op["engine"], carrier))
        family_context = ""
        if article and article.title.upper() != name.upper():
            family_context = (
                f"本地中文站以《{article.title}》介绍该操作族。下文保留这篇原页，"
                f"其中示例使用原页的操作名。{name} 的独立选择器见本页 0.59.1 命令编码。"
            )
        reader = library.render(url, source_context=family_context)
        if not reader:
            supplement = tile_supplement(op)
            reader = supplement_reader(supplement, url, library)
            supplement_audit[url] = Path(supplement).relative_to(ROOT).as_posix()
        # Keep exact machine record available independently of the reader.
        fields = [
            ("引擎", op["engine"]),
            ("承载指令", carrier),
            ("选择器", op.get("selector") or f"Function={op['function']}"),
            ("语义处理器", op["semantic_handler"]),
        ]
        metadata = (
            '<section class="tile-contract"><h3>发布记录</h3><dl>'
            + "".join(
                f"<dt>{k}</dt><dd><code>{escape(str(v))}</code></dd>" for k, v in fields
            )
            + "<dt>ASL 来源</dt><dd>"
            + link(owner["source_url"], owner["source_path"])
            + "</dd></dl></section>"
        )
        bodies[url] = (
            name,
            '<p class="meta">'
            + link(
                "tiles-" + op["engine"].lower() + ".html", op["engine"] + " 操作索引"
            )
            + "</p>"
            + indexed_transfer_note(op, tile_owners)
            + reader
            + '<details class="release-data"'
            + ("" if article else " open")
            + '><summary>0.59.1 命令编码与核对资料</summary><div class="release-data-body">'
            + tile_header(op, forms[carrier][0], owner)
            + metadata
            + release_constraints(zh_tile[name])
            + operation_detail(owner["source_path"])
            + "</div></details>",
        )
    families = defaultdict(list)
    for name, variants in forms.items():
        families[variants[0]["mnemonic"]].append(name)
    for name, variants in forms.items():
        first, url = variants[0], op_page(name)
        base, key = first["mnemonic"], first["uop_big_kind"]
        if any(r["uop_big_kind"] != key for r in variants):
            raise ValueError(f"{name} has more than one main class")
        article = articles[url][1]
        scope = first.get("pto_scope")
        conflict = bool(article and article.classification == "conflicting-current")
        missing = f"{base} 的中文增补说明与发布版编码。"
        short = (
            authored_synopsis(article, missing)
            if article
            else supplement_excerpt(instruction_supplement(first))
        )
        if conflict:
            short = "；".join(article.current_view) or f"当前汇编为 {first['asm']}。"
        if scope:
            short = f"{name} 是 {base} 的 {scope} 作用域形式。" + short
        terms = " ".join([*(r["asm"] for r in variants), *(r["id"] for r in variants)])
        entries.append((name, url, short, key, terms))
        written = first["asm"].split()[0].upper()
        if (
            not scope
            and written != name
            and re.fullmatch(r"[A-Z0-9.]+", written)
            and written not in forms
        ):
            entries.append(
                (written, url + "#" + first["id"], f"目录名为 {name}。", key, name)
            )
        sizes = "、".join(str(n) for n in sorted({r["length_bits"] for r in variants}))
        body = f'<p class="meta">{link(cat_file(key), BY_KEY[key][0] + " · " + BY_KEY[key][1])} · {sizes} 位</p>'
        related = sorted(n for n in families[base] if n != name)
        if related:
            body += (
                '<p class="family-links">关联汇编形式　'
                + " · ".join(link(op_page(n), n) for n in related)
                + "</p>"
            )
        context = ""
        if scope:
            context = f"以下是基础指令 {base} 的中文站原文。{name} 是 64 位封装，原页的基础指令位图不能用于译码此封装。"
        elif article and len(variants) > 1:
            context = f"《{article.title}》按中文站原页展示。本版共有 {len(variants)} 个编码形式，各形式分别列在原文之后。"
        elif article and article.classification == "contextual-original":
            context = f"下文为中文站的《{article.title}》。原文示例与原图按原页版本阅读，0.59.1 的各编码形式另列。"
        elif article and not all(
            p["source"] == "tagged-original-wavedrom-svg"
            for p in diagram_audit["forms"][first["id"]]["parts"]
        ):
            context = "本节沿用中文站原文和原图；本版译码请查阅 0.59.1 的编码位图。"
        if (
            not context
            and article
            and article.classification == "syntax-compatible-original"
        ):
            context = "原页的汇编写法已与本版目录对照；完整编码与使用条件见本页的 0.59.1 记录。"
        reader = library.render(url, source_context=context, conflict=conflict)
        multiple = len(variants) > 1
        if multiple and reader:
            body += reader
        for sequence, row in enumerate(variants, start=1):
            if multiple:
                qualifier = ""
                if sum(v["asm"] == row["asm"] for v in variants) > 1:
                    qualifier = (
                        f" · 匹配值 0x{fixed_bits(row)[1]:0{row['length_bits'] // 4}x}"
                    )
                body += f'<details class="variant"{" open" if sequence == 1 else ""}><summary>形式 {sequence}　<code>{escape(row["asm"])}</code>{qualifier}</summary>'
            form_id = escape(row["id"])
            body += f'<article class="form" id="{form_id}">'
            if not multiple and reader and not conflict:
                body += reader
            if not reader:
                supplement = instruction_supplement(row)
                body += supplement_reader(supplement, url, library)
                supplement_audit[url] = Path(supplement).relative_to(ROOT).as_posix()
            if conflict:
                body += (
                    '<p class="version-context"><strong>0.59.1 版本差异</strong>　'
                    + escape(" ".join(article.reasons + article.current_view))
                    + "</p>"
                )
            source_id = row.get("pto_base_form_id") or row.get("pto_source_form_id")
            owner = asl_owners.get(source_id, {}).get("source_path", "")
            expand = " open" if conflict or not reader or multiple or scope else ""
            note = (
                "编码保留；执行必须在读取操作数或产生架构效果之前拒绝。"
                if "NOT IMPLEMENTED" in row.get("note", "")
                else ""
            )
            body += (
                f'<details class="release-data"{expand}><summary>0.59.1 汇编、位图与精确编码</summary><div class="form-spec">'
                + (f'<p class="version-context">{note}</p>' if note else "")
                + f"<h3>汇编语法</h3><pre><code>{escape(row['asm'])}</code></pre>"
                + "<h3>编码格式</h3>"
                + diagram_html[row["id"]]
                + render_encoding(row, catalog)
            )
            if source_id in zh_common:
                body += release_constraints(zh_common[source_id], base=bool(scope))
            if scope:
                base_row = base_by_id[source_id]
                body += (
                    "<p>基础形式　"
                    + link(op_page(base) + "#" + base_row["id"], base_row["asm"])
                    + "</p>"
                )
                body += scoped_record(row, source_forms[row["pto_source_form_id"]])
            body += (
                (operation_detail(owner) if owner else sail_detail(row))
                + form_provenance(row, commit, common_paths)
                + "</div></details>"
            )
            if conflict and not multiple:
                body += reader
            body += "</article>"
            if multiple:
                body += "</details>"
            mask, match = fixed_bits(row)
            audit.append(
                {
                    "id": row["id"],
                    "mnemonic": base,
                    "asm": row["asm"],
                    "page": url + "#" + row["id"],
                    "bits": row["length_bits"],
                    "mask": hex(mask),
                    "match": hex(match),
                    "source_id": row.get("pto_source_form_id") or row["id"],
                    "semantic_owner": owner or row["source"]["file"],
                    "scope": scope,
                }
            )
        if carrier_ops[name]:
            body += (
                "<h2>此编码选择的 Tile 操作</h2><p>"
                + " · ".join(
                    link(tile_page(o["name"]), o["name"]) for o in carrier_ops[name]
                )
                + "</p>"
            )
        bodies[url] = (name, body)
    commands = json.loads(inputs[paths[5]])["forms"]
    carrier_form = next(f for f in commands if f["mnemonic"] == "BSTART.TEPL")
    for engine, alias in carrier_form["canonical_assembly_by_engine"].items():
        selected = [
            o for o in direct_ops if o["family"] == "TEPL" and o["engine"] == engine
        ]
        title = f"{engine} 操作的 BSTART.TEPL 汇编别名"
        entries.append((alias, op_page(alias), title, "CMD", "TEPL"))
        bodies[op_page(alias)] = (
            alias,
            f"<p>{title}。编码见 {link(op_page('BSTART.TEPL'), 'BSTART.TEPL')}。"
            "下列操作页给出各自的 Mode、Function 和操作数。</p><ul>"
            + "".join(
                f"<li>{link(tile_page(o['name']), o['name'])}</li>" for o in selected
            )
            + "</ul>",
        )
    intro = (
        f"<p>{len({r['mnemonic'] for r in rows})} 个目录助记符，{len(rows):,} 个编码形式。"
        "带作用域的拼写可直接检索。Tile 的 Mode / Function 选择见 "
        + link("tile.html", "Tile 操作索引")
        + "。</p>"
    )
    bodies.update(index_pages(rows, entries, alphabetic_index, len(direct_ops)))
    bodies["mnemonics.html"] = (
        "指令索引",
        alphabetic_index(entries, intro, "例如 ADD、C.LDI.INTER、B.IOT"),
    )
    bodies["tile.html"] = (
        "Tile 操作索引",
        alphabetic_index(
            tile_list,
            f"<p>{len(direct_ops)} 个直接操作，按名称排列。VEC 和 SFU 使用 TEPL 编码载体。</p>",
            "例如 TADD、TIMG2COL",
        ),
    )
    tile_links = [
        (f"tiles-{engine.lower()}.html", engine)
        for engine in ("VEC", "SFU", "TLSU", "CUBE")
    ]
    tile_nav = (
        '<div class="jump" aria-label="Tile 引擎">'
        + " · ".join(link(url, engine) for url, engine in tile_links)
        + "</div>"
    )
    title, listing = bodies["tile.html"]
    bodies["tile.html"] = (title, tile_nav + listing)
    for url, engine in tile_links:
        members = [entry for entry in tile_list if entry[3] == engine]
        bodies[url] = (
            f"{engine} · Tile 操作索引",
            tile_nav
            + alphabetic_index(
                members,
                f"<p>{engine} 引擎共 {len(members)} 个操作。</p>",
                "搜索本引擎的操作",
            ),
        )
    bodies["encoding.html"] = ("按编码查找", encoding_index(rows))
    bodies["sources.html"] = (
        "版本与来源",
        sources(commit, inputs, manifest, lock)
        + '<p><a href="arm64-reference-organization.md">Arm 参考站结构与 LinxISA 分类说明</a> · <a href="reader-quality-review.md">独立审阅记录</a></p>'
        + "<h2>许可</h2><p>"
        + link("LICENSE.txt", "LinxISA")
        + " · "
        + link("BITFIELD-LICENSE.txt", "位图工具")
        + " · "
        + link("PTO-SPEC-LICENSE.txt", "PTO-SPEC")
        + "</p>",
    )
    lacking = [
        (filename, name)
        for filename, (name, article) in articles.items()
        if article is None
    ]
    title, source_body = bodies["sources.html"]
    bodies["sources.html"] = (
        title,
        "<h2>中文站原文</h2><p>指令说明、汇编示例与原图读取自发布标签中的 "
        "<code>docs/zh/isa</code> 和 <code>docs/zh/figs</code>。关联原文按原页展示；有版本差异时，"
        "本版编码单独列出。原始 Markdown 可从文章上方的“中文站原文”链接打开。</p>"
        + "<details><summary>另有 0.59.1 中文增补页的条目</summary><ul>"
        + "".join(
            "<li>" + link(filename, name) + "</li>"
            for filename, name in sorted(lacking)
        )
        + "</ul></details>"
        + source_body,
    )
    chapters, chapter_audit = architecture_bodies(library)
    bodies.update(chapters)
    _, home_body = bodies["index.html"]
    bodies["index.html"] = (
        "LinxISA 0.59.1 芯片开发手册",
        '<p class="architecture-links">'
        + link("arch-state.html", "架构状态")
        + " · "
        + link("execution-model.html", "执行模型")
        + " · "
        + link("arch-ssr.html#system-registers", "系统寄存器表")
        + "</p>"
        + "<h2>按指令类型查找</h2>"
        + home_body,
    )
    canvas_files = include_canvas(bodies, ASSETS / "figures")
    files = {
        name: page(title, body, commit).encode()
        for name, (title, body) in bodies.items()
    }
    for path, fragment in library.support.items():
        files[path] = page(
            "中文站参考资料",
            '<div class="authored-reader">' + fragment + "</div>",
            commit,
            prefix="../",
        ).encode()
    analysis_path = "docs/zh/architecture/isa-manual/arm64-reference-organization.md"
    files["arm64-reference-organization.md"] = (ROOT / analysis_path).read_bytes()
    review_path = "docs/zh/architecture/isa-manual/reader-quality-review.md"
    files["reader-quality-review.md"] = (ROOT / review_path).read_bytes()
    files.update(library.files)
    files.update(diagram_assets)
    files.update(canvas_files)
    reviewed_pages = {}
    for filename, data in sorted(files.items()):
        if not filename.endswith(".html"):
            continue
        source = (
            library.audit.get(filename, {}).get("source_path")
            or chapter_audit.get(filename, {}).get("source_path")
            or library.support_sources.get(filename)
        )
        if source:
            edits = dict(edit_article(source)[1])
            origin = "tagged-chinese-source"
        elif filename in supplement_audit:
            source = supplement_audit[filename]
            edits = dict(edit_markdown(source, (ROOT / source).read_text())[1])
            origin = "release-specific-supplement"
        else:
            edits = {}
            origin = "navigation-and-reference"
        reviewed_pages[filename] = {
            "html_sha256": sha256(data).hexdigest(),
            "origin": origin,
            "source_path": source,
            "applied_source_edits": edits,
        }
    files["editorial-audit.json"] = json.dumps(
        {
            "skill": SKILL_URL,
            "skill_commit": SKILL_COMMIT,
            "skill_sha256": SKILL_SHA256,
            "renderer_versions": {
                name: version(name)
                for name in (
                    "MkDocs",
                    "mkdocs-material",
                    "Markdown",
                    "pymdown-extensions",
                    "Pygments",
                )
            },
            "scope": "正文采用原作者的表述，按上下文校读；代码、链接、表格数值和标题保持原样。空编辑记录表示保留源文字。",
            "pages": reviewed_pages,
        },
        ensure_ascii=False,
        indent=2,
    ).encode()
    files["supplements.json"] = json.dumps(
        supplement_audit, ensure_ascii=False, indent=2
    ).encode()
    files["architecture-audit.json"] = json.dumps(
        chapter_audit, ensure_ascii=False, indent=2
    ).encode()
    files["diagram-audit.json"] = json.dumps(
        diagram_audit, ensure_ascii=False, indent=2
    ).encode()
    files["authored-audit.json"] = json.dumps(
        library.audit, ensure_ascii=False, indent=2
    ).encode()
    files["PTO-SPEC-LICENSE.txt"] = (ASSETS / "data/PTO-SPEC-LICENSE.txt").read_bytes()
    files["LICENSE.txt"] = tagged_bytes("LICENSE")
    files["BITFIELD-LICENSE.txt"] = tagged_bytes("docs/figs/bitfield/LICENSE")
    files.update({"spec/" + Path(path).name: data for path, data in inputs.items()})
    for name in ("manual.css", "index-filter.js"):
        files[name] = (ASSETS / name).read_bytes()
    if len(audit) != catalog["instruction_count"] or len(
        {a["id"] for a in audit}
    ) != len(audit):
        raise ValueError("form ID coverage mismatch")
    files["audit.json"] = (
        json.dumps(
            {
                "tag": TAG,
                "commit": commit,
                "forms": audit,
                "tile_operations": [
                    {
                        "name": o["name"],
                        "page": tile_page(o["name"]),
                        "carrier": o["command_mnemonic"],
                    }
                    for o in direct_ops
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    ).encode()
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--zip", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = build()
    for name, data in files.items():
        target = args.out / name
        if args.check:
            if not target.is_file() or target.read_bytes() != data:
                raise SystemExit(f"out of date: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    if args.zip and not args.check:
        args.zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.zip, "w") as bundle:
            for name in sorted(files):
                info = zipfile.ZipInfo(name)
                info.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(info, files[name])
    print(
        f"{sum(n.endswith('.html') for n in files)} HTML pages: {args.out / 'index.html'}"
    )


if __name__ == "__main__":
    main()
