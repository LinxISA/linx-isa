#!/usr/bin/env python3
"""Independently check reader-visible instruction semantics in the HTML manual.

This checker deliberately reads the finished HTML.  It does not call the
manual body generators or compare their hashes, so a generator and its audit
cannot agree with each other while still displaying one of the known stale
contracts checked here.
"""

from __future__ import annotations

import argparse
from html import unescape
from pathlib import Path
import re


START = "<!-- authored:start -->"
END = "<!-- authored:end -->"


def _visible(value: str) -> str:
    value = re.sub(r"<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>", " ", value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _reader(page: Path) -> tuple[str, str]:
    html = page.read_text(encoding="utf-8")
    if html.count(START) != 1 or html.count(END) != 1:
        raise ValueError("expected one reviewed Chinese reader")
    fragment = html.split(START, 1)[1].split(END, 1)[0]
    return _visible(fragment), fragment


def _require(errors: list[str], page: str, text: str, *needles: str) -> None:
    for needle in needles:
        if needle not in text:
            errors.append(f"{page}: missing current semantic fact {needle!r}")


def _reject(errors: list[str], page: str, text: str, *needles: str) -> None:
    for needle in needles:
        if needle in text:
            errors.append(f"{page}: stale or contradictory text {needle!r}")


def _check_modifier_tables(site: Path, errors: list[str]) -> None:
    arithmetic = ("add", "addw", "sub", "subw")
    logical = ("and", "andw", "or", "orw", "xor", "xorw")
    for slug in arithmetic + logical:
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        modifier = ".neg" if slug in arithmetic else ".not"
        for code, spelling in (("00", ".sw"), ("01", ".uw"), ("10", modifier)):
            if not re.search(rf"{code}.{{0,55}}{re.escape(spelling)}", text, re.I):
                errors.append(
                    f"{page}: SrcRType {code} does not visibly select {spelling}"
                )
        if not re.search(r"11.{0,55}(无修饰|直接使用原值|No operation)", text, re.I):
            errors.append(f"{page}: SrcRType 11 does not visibly select no modifier")
        for bad in (
            r"00.{0,30}无格式",
            r"01.{0,30}\.sw",
            r"10.{0,30}\.uw",
            rf"11.{{0,30}}{re.escape(modifier)}",
        ):
            if re.search(bad, text, re.I):
                errors.append(f"{page}: retains the pre-0.59.1 SrcRType table")
                break


def _check_scalar_results(site: Path, errors: list[str]) -> None:
    for slug in (
        "div",
        "divu",
        "divw",
        "divuw",
        "hl-div",
        "hl-divu",
        "hl-divw",
        "hl-divuw",
    ):
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "除数为零", "商为零")
        _reject(errors, page, text, "除数为零时，商为 -1", "除数为 0 时商为 -1")
    for slug in (
        "rem",
        "remu",
        "remw",
        "remuw",
        "hl-rem",
        "hl-remu",
        "hl-remw",
        "hl-remuw",
    ):
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "除数为零", "余数为被除数")
    text, _ = _reader(site / "op-muluw.html")
    _require(errors, "op-muluw.html", text, "低 32 位", "符号扩展")
    _reject(errors, "op-muluw.html", text, "无符号扩展后写")
    for slug in ("swapw", "hl-casw"):
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "符号扩展")


def _check_ccat(site: Path, errors: list[str]) -> None:
    text, _ = _reader(site / "op-hl-ccat.html")
    _require(
        errors,
        "op-hl-ccat.html",
        text,
        "逻辑右移",
        "低 64 位",
        "Dst0",
        "高 64 位",
        "Dst1",
    )
    _reject(errors, "op-hl-ccat.html", text, "循环左移")
    text, _ = _reader(site / "op-hl-ccatw.html")
    _require(
        errors,
        "op-hl-ccatw.html",
        text,
        "逻辑右移",
        "低 32 位",
        "符号扩展",
        "64 至 127",
        "零",
    )
    _reject(errors, "op-hl-ccatw.html", text, "循环左移")


def _check_scalar_fp(site: Path, errors: list[str]) -> None:
    conversions = {
        "fcvt",
        "fcvta",
        "fcvtm",
        "fcvtn",
        "fcvtp",
        "fcvtz",
        "scvtf",
        "ucvtf",
    }
    all_fsu = {
        "fabs",
        "fadd",
        "fdiv",
        "fexp",
        "fmadd",
        "fmax",
        "fmin",
        "fmsub",
        "fmul",
        "fnmadd",
        "fnmsub",
        "frecip",
        "fsqrt",
        "fsub",
        "feq",
        "feqs",
        "fge",
        "fges",
        "flt",
        "flts",
        "fne",
        "fnes",
    }
    for slug in all_fsu:
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "FP64", "FP32", "编码 2 和 3 保留")
        _reject(errors, page, text, "FP16", "E4M3", "半精度", "低精度")
    for slug in conversions:
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "FP64", "FP32", "FP16", "E4M3")


def _check_vector(site: Path, errors: list[str]) -> None:
    for slug in ("v-sh-brg", "v-sw-brg", "v-sd-brg"):
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "发布 Sail", "目录汇编", "shamt", "裁决")
        if not re.search(r"SrcR(?:\[0\])?.{0,25}shamt", text):
            errors.append(f"{page}: missing Sail address expression")
        if not re.search(r"[123]\s*\+\s*shamt", text):
            errors.append(f"{page}: missing catalog address expression")
    for slug in ("v-bcnt", "v-bic", "v-bis", "v-bxs", "v-bxu", "v-clz", "v-ctz"):
        page = f"op-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "32 位", "钳制到 32 位", "bit 31", "bit 0")
        _reject(
            errors,
            page,
            text,
            "N == 64",
            "M+N > 64",
            "循环左移",
            "循环右移",
            "XLEN(即64)",
        )


def _check_bstart_examples(site: Path, errors: list[str]) -> None:
    cases = {
        "op-hl-bstart-fp.html": "hl.bstart.fp",
        "op-hl-bstart-std.html": "hl.bstart.std",
        "op-hl-bstart-sys.html": "hl.bstart.sys",
        "op-l-bstart-fp.html": "l.bstart.fp",
        "op-l-bstart-std.html": "l.bstart.std",
        "op-l-bstart-sys.html": "l.bstart.sys",
    }
    for page, own in cases.items():
        text, fragment = _reader(site / page)
        _require(errors, page, text.lower(), own)
        for block in re.findall(
            r"<pre><code[^>]*>([\s\S]*?)</code></pre>", fragment, re.I
        ):
            for token in re.findall(
                r"(?im)^\s*((?:hl|l)\.bstart\.[a-z]+)", unescape(block)
            ):
                if token.lower() != own:
                    errors.append(f"{page}: example for another mnemonic {token}")


def _check_tile_accumulators(site: Path, errors: list[str]) -> None:
    for slug in ("tmatmul-acc", "tmatmul-mx-acc", "tgemv-acc", "tgemv-mx-acc"):
        page = f"tile-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "C", "累加源", "D", "输出")
        _reject(errors, page, text, "ACC寄存器", "隐式 ACC")
    for slug in (
        "tmatmul-mx",
        "tmatmul-mx-acc",
        "tmatmul-mx-bias",
        "tgemv-mx",
        "tgemv-mx-acc",
        "tgemv-mx-bias",
    ):
        page = f"tile-{slug}.html"
        text, _ = _reader(site / page)
        _require(errors, page, text, "E8M0", "32 个元素", "HiF4X2", "64 个元素", "U32")


def _check_scopes(site: Path, errors: list[str]) -> None:
    pages = sorted(
        {
            *site.glob("op-*-private.html"),
            *site.glob("op-*-intra.html"),
            *site.glob("op-*-inter.html"),
        }
    )
    if len(pages) != 705:
        errors.append(f"scoped page inventory {len(pages)} != 705")
    labels = {
        "-private.html": "私有属性",
        "-intra.html": "核内共享属性",
        "-inter.html": "跨核共享属性",
    }
    for page in pages:
        text, _ = _reader(page)
        label = next(
            value for suffix, value in labels.items() if page.name.endswith(suffix)
        )
        if label not in text:
            errors.append(f"{page.name}: missing {label}")


def check_site(site: Path) -> list[str]:
    site = site.resolve()
    errors: list[str] = []
    for page in (*site.glob("op-*.html"), *site.glob("tile-*.html")):
        html = page.read_text(encoding="utf-8")
        if "historical-article" in html or "0.59.1 版本差异" in html:
            errors.append(f"{page.name}: conflicting historical body is still packaged")
    for check in (
        _check_modifier_tables,
        _check_scalar_results,
        _check_ccat,
        _check_scalar_fp,
        _check_vector,
        _check_bstart_examples,
        _check_tile_accumulators,
        _check_scopes,
    ):
        try:
            check(site, errors)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(f"{check.__name__}: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args(argv)
    errors = check_site(args.site)
    if errors:
        for error in errors:
            print("ERROR:", error)
        print(f"manual detail semantic validation failed: {len(errors)} error(s)")
        return 1
    print("OK: independent reader-visible detail semantics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
