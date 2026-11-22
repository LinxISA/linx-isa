#!/usr/bin/env python3
"""Build the offline LinxISA 0.59.1 reference from the published Git tag."""

from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from html import escape
from itertools import groupby
import json
from pathlib import Path
import re
import zipfile

from manual_tag import (
    RELEASE_TAG as TAG,
    tagged_bytes,
    tagged_json,
    verified_tag_commit,
)
from manual_encoding import render_encoding, validate_catalog
from manual_linx_sail import sail_detail
from manual_reader import operation_detail, reader_summary, reader_detail
from manual_scoped import scoped_detail, tile_detail, tile_summary
from manual_semantics import detail, summary

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
                f'<option value="{escape(k)}">{escape(k)}</option>'
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


def page(title, body, commit):
    nav = (
        ("index.html", "助记符"),
        ("encoding.html", "编码索引"),
        ("tile.html", "Tile 操作"),
        ("sources.html", "版本与来源"),
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · LinxISA 0.59.1</title><link rel="stylesheet" href="manual.css">
<script defer src="index-filter.js"></script></head><body>
<a class="skip" href="#content">跳至正文</a><header>
<a class="brand" href="index.html">LinxISA</a><span class="edition">0.59.1 · 指令集参考手册</span>
<nav aria-label="手册目录">{"".join(link(*item) for item in nav)}</nav></header>
<main id="content"><h1>{escape(title)}</h1>{body}</main>
<footer>{link("sources.html", TAG)} · 规范提交 <code>{escape(commit[:12])}</code> · {link("#content", "回到页首")}</footer></body></html>
"""


def brief(asl_path, fallback):
    # Keep one complete sentence in the alphabetic index. The instruction page
    # carries the complete purpose paragraph and the normative source text.
    paragraph = reader_summary(asl_path) if asl_path else ""
    if paragraph:
        first, mark, _ = paragraph.partition("。")
        return first + mark if len(first) <= 180 else fallback
    return fallback


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
    block = "\n".join(owner["block"])
    return (
        "<h2>命令编码</h2><p>承载指令 "
        + link(op_page(row["mnemonic"]), row["mnemonic"])
        + "　"
        + escape(" · ".join(labels))
        + f"</p><pre><code>(word &amp; 0x{mask:0{fmt}x}) == 0x{match:0{fmt}x}</code></pre>"
        + '<p class="meta">上式匹配指令和操作选择器。数据类型、绑定命令及布局仍须满足本操作的合法性条件。</p>'
        + "<h3>Block 组成</h3><pre><code>"
        + escape(block)
        + "</code></pre>"
    )


def encoding_index(instructions):
    sections = []
    kinds = {r["encoding_kind"] for r in instructions}
    intro = (
        "<p>按指令长度和固定比特的 Match 排序。表中数值按逻辑位编号书写，"
        "先取出的 Part 0 占低位。硬件匹配条件为 <code>(word &amp; mask) == match</code>。"
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
            "<th>汇编形式</th><th>Match</th><th>Mask</th><th>格式</th></tr></thead>"
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
        "<h2>如何使用编码图</h2><p>按 Part 编号从小到大取指。每个 Part 内左侧为高位，"
        "格顶标出本 Part 内的位号。固定的 0、1 进入 Mask/Match，其余位承载字段。"
        "分散在多个格子里的同名字段按标出的值位组合；字段域和形式约束决定合法取值。</p>"
        "<h2>语义与实现状态</h2><p>公共与 scoped 形式对照本版锁定的 PTO 定义。"
        "Linx 专有形式单列其依据和已知语义缺口。芯片实现还需检查操作数合法性、异常及提交时机。"
        "整机验证进度见发行说明。</p>"
    )
    body += link(repo + "docs/zh/releases/v0.59.1.md", "0.59.1 发行说明")
    body += '<h2>离线规范文件</h2><div class="table-scroll"><table><tr><th>文件</th><th>SHA-256</th></tr>'
    for path, data in inputs.items():
        body += f"<tr><td>{link('spec/' + Path(path).name, Path(path).name)}</td><td><code>{sha256(data).hexdigest()}</code></td></tr>"
    return (
        body
        + "</table></div><p>"
        + link("audit.json", "逐形式核对记录（JSON）")
        + "</p>"
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
    common_paths = {}
    for path in paths[4:]:
        doc = json.loads(inputs[path])
        for form in doc["forms"] + doc.get("scoped_forms", []):
            common_paths[form["form_id"]] = path
    direct_ops = tiles["operations"]
    tile_refs = json.loads((ASSETS / "data/pto-v0591-tile-manual.json").read_text())
    tile_owners = {r["mnemonic"]: r for r in tile_refs["operations"]}
    asl_owners = json.loads((ASSETS / "pto-v0591-semantics.json").read_text())["forms"]
    carrier_ops = defaultdict(list)
    bodies, entries, tile_list, audit = {}, [], [], []
    for op in direct_ops:
        name, carrier = op["name"], op["command_mnemonic"]
        if carrier not in forms:
            raise ValueError(f"{name} has no carrier {carrier}")
        carrier_ops[carrier].append(op)
        tile_path = tile_owners[name]["source_path"]
        desc = brief(tile_path, tile_summary(op, catalog))
        tile_list.append((name, tile_page(name), desc, op["engine"], carrier))
        bodies[tile_page(name)] = (
            name,
            reader_detail(tile_path)
            + tile_header(op, forms[carrier][0], tile_owners[name])
            + tile_detail(op, catalog)
            + operation_detail(tile_path),
        )
    families = defaultdict(list)
    for name, variants in forms.items():
        families[variants[0]["mnemonic"]].append(name)
    for name, variants in forms.items():
        first = variants[0]
        base = first["mnemonic"]
        related = sorted(n for n in families[base] if n != name)
        if "pto_scope" in first:
            short = f"{first['pto_scope']} · " + summary(forms[base][0], catalog)
        else:
            short = summary(first, catalog)
        primary_id = first.get("pto_base_form_id") or first.get("pto_source_form_id")
        primary_owner = asl_owners.get(primary_id, {}).get("source_path", "")
        if primary_owner:
            short = brief(primary_owner, short)
            if "pto_scope" in first:
                short = f"{first['pto_scope']} GM 作用域。" + short
        terms = " ".join([*(r["asm"] for r in variants), *(r["id"] for r in variants)])
        entries.append((name, op_page(name), short, first["uop_big_kind"], terms))
        if "pto_scope" not in first:
            written = first["asm"].split()[0].upper()
            if (
                written != name
                and re.fullmatch(r"[A-Z0-9.]+", written)
                and written not in forms
            ):
                entries.append(
                    (
                        written,
                        op_page(name) + "#" + first["id"],
                        f"规范汇编拼写。目录名为 {name}。",
                        first["uop_big_kind"],
                        name,
                    )
                )
        body = (
            f'<p class="meta">{escape(first["group"])} · {len(variants)} 个编码形式</p>'
        )
        if related:
            body += (
                "<p>关联形式　"
                + " · ".join(link(op_page(n), n) for n in related)
                + "</p>"
            )
        if len(variants) > 1:
            body += (
                '<ol class="form-links">'
                + "".join(f"<li>{link('#' + r['id'], r['asm'])}</li>" for r in variants)
                + "</ol>"
            )
        if carrier_ops[name]:
            body += (
                "<p>Tile 操作　"
                + " · ".join(
                    link(tile_page(o["name"]), o["name"]) for o in carrier_ops[name]
                )
                + "</p>"
            )
        for row in variants:
            text = "" if "pto_scope" in row else detail(row, catalog)
            if "pto_scope" in row:
                base_form = next(
                    r
                    for r in forms[base]
                    if r.get("pto_source_form_id") == row["pto_base_form_id"]
                )
                text = (
                    f"<p>基础操作 {link(op_page(base) + '#' + base_form['id'], base_form['asm'])}</p>"
                    + scoped_detail(row, catalog)
                    + "<details><summary>未封装基础形式的操作契约</summary>"
                    + detail(base_form, catalog)
                    + "</details>"
                )
            source_id = row.get("pto_base_form_id") or row.get("pto_source_form_id")
            owner = asl_owners.get(source_id, {}).get("source_path", "")
            explanation = reader_detail(owner) if owner else ""
            if row.get("pto_scope"):
                explanation = (
                    f"<p><strong>{escape(row['pto_scope'])}</strong> GM 作用域。"
                    "本形式为 64 位封装，成功提交后 TPC 增加 8 字节。以下中文导读与 ASL 摘录描述基础操作。</p>"
                    + explanation
                )
            form_id = escape(row["id"])
            body += (
                f'<article class="form" id="{form_id}"><h2>汇编形式</h2><pre><code>{escape(row["asm"])}</code></pre>'
                + explanation
                + "<h3>编码</h3>"
                + render_encoding(row, catalog)
                + "<h3>操作</h3>"
                + text
                + (operation_detail(owner) if owner else sail_detail(row))
                + form_provenance(row, commit, common_paths)
                + "</article>"
            )
            mask, match = fixed_bits(row)
            audit.append(
                {
                    "id": row["id"],
                    "mnemonic": base,
                    "asm": row["asm"],
                    "page": op_page(name) + "#" + row["id"],
                    "bits": row["length_bits"],
                    "mask": hex(mask),
                    "match": hex(match),
                    "source_id": row.get("pto_source_form_id") or row["id"],
                    "semantic_owner": asl_owners.get(
                        row.get("pto_base_form_id") or row.get("pto_source_form_id"), {}
                    ).get("source_path", row["source"]["file"]),
                    "scope": row.get("pto_scope"),
                }
            )
        bodies[op_page(name)] = (name, body)
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
    bodies["index.html"] = (
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
    bodies["encoding.html"] = ("按编码查找", encoding_index(rows))
    bodies["sources.html"] = (
        "版本与来源",
        sources(commit, inputs, manifest, lock)
        + "<h2>许可</h2><p>"
        + link("LICENSE.txt", "LinxISA")
        + " · "
        + link("PTO-SPEC-LICENSE.txt", "PTO-SPEC（含中文导读）")
        + "</p>",
    )
    files = {
        name: page(title, body, commit).encode()
        for name, (title, body) in bodies.items()
    }
    files["PTO-SPEC-LICENSE.txt"] = (ASSETS / "data/PTO-SPEC-LICENSE.txt").read_bytes()
    files["LICENSE.txt"] = tagged_bytes("LICENSE")
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
