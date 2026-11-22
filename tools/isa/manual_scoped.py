#!/usr/bin/env python3
"""Precise manual fragments for PTO 0.59.1 scoped Scalar and Tile operations."""

from __future__ import annotations
from functools import lru_cache
from html import escape
import json
from pathlib import Path
from typing import Any
from manual_tag import tagged_json

ROOT = Path(__file__).resolve().parents[2]
MANUAL_PATH = (
    ROOT / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
)
SCOPED_SAIL = "isa/sail/model/execute/scoped_scalar.sail"

SCOPE_TEXT = {
    "Private": "Private GM shareability request",
    "IntraCore": "IntraCore GM shareability request",
    "InterCore": "InterCore GM shareability request",
}


@lru_cache(maxsize=None)
def _load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _scoped_index() -> dict[str, dict[str, Any]]:
    return {
        r["form_id"]: r
        for r in tagged_json("isa/v0.59/state/pto_scalar_forms.json")["scoped_forms"]
    }


def _base_index() -> dict[str, dict[str, Any]]:
    return {
        r["form_id"]: r
        for r in tagged_json("isa/v0.59/state/pto_scalar_forms.json")["forms"]
    }


def _tile_index() -> dict[str, dict[str, Any]]:
    return {r["mnemonic"]: r for r in _load(str(MANUAL_PATH))["operations"]}


def _source_row(row: dict[str, Any]) -> dict[str, Any]:
    form_id = row.get("pto_source_form_id") or row.get("form_id")
    try:
        return _scoped_index()[str(form_id)]
    except KeyError as exc:
        raise ValueError(f"unresolved scoped form: {form_id}") from exc


def scoped_summary(row: dict[str, Any], catalog: Any = None) -> str:
    source = _source_row(row)
    scope = SCOPE_TEXT[source["scope"]]
    return f"{source['semantic_summary']} Encoded scope is a {scope}; platform visibility and ordering follow the GM memory model."


def scoped_detail(row: dict[str, Any], catalog: Any = None) -> str:
    source = _source_row(row)
    base = _base_index()[source["base_form_id"]]
    agu = base.get("agu")
    agu_detail = ""
    if isinstance(agu, dict):
        signed = (
            "sign-extends"
            if agu.get("signed_load")
            else "zero-extends or writes the complete width"
        )
        result_rule = (
            f"; a load {signed} its {agu['size_bytes']}-byte result"
            if "Load" in str(agu.get("action"))
            else ""
        )
        agu_detail = (
            f"<li>AGU contract: {escape(str(agu['action']))}, {escape(str(agu['address_kind']))} address, "
            f"{agu['size_bytes']}-byte access, offset scale 2^{agu['offset_scale']}, update mode "
            f"{escape(str(agu['update_mode']))}{escape(result_rule)}.</li>"
        )
    operands = "".join(
        f"<tr><td><code>{escape(o['field'])}</code></td><td>{escape(o['role'])}</td></tr>"
        for o in source["operands"]
    )
    return (
        '<section class="scoped-contract"><h2>Scoped Scalar contract</h2>'
        f"<p>{escape(source['semantic_summary'])}</p><dl>"
        f"<dt>Assembly</dt><dd><code>{escape(source['asm'])}</code></dd>"
        f"<dt>Scope</dt><dd><code>{escape(source['scope'])}</code> (code {source['scope_code']}) — {escape(SCOPE_TEXT[source['scope']])}. "
        "This is a shareability request, not a standalone visibility prohibition.</dd>"
        f"<dt>Semantic handler</dt><dd><code>{escape(source['semantic_handler'])}</code></dd>"
        f"<dt>Base form</dt><dd><code>{escape(source['base_form_id'])}</code></dd>"
        f"<dt>Contract status</dt><dd><code>{escape(source['status'])}</code></dd></dl>"
        "<h3>Lifetime and faults</h3><ul>"
        "<li>The wrapper is exactly 8 bytes. Source operands, ACR identity, source TPC, address, scope, and store/atomic data are captured before issue.</li>"
        "<li>The issuing execution context is held until completion. A blocked completion performs no access and makes the captured request reissuable.</li>"
        "<li>Only committed completion writes destinations or address writeback and advances TPC to captured source TPC + 8.</li>"
        "<li>Alignment and page faults report the first or second access address as applicable. PCR forms use the 4-byte-aligned carrier-start TPC as their base.</li>"
        "<li>Reg5 queue sources are snapshotted without consuming an entry. Queue destinations push only on committed completion; binding is exact in core, agent, invocation, and ACR and cannot be replaced while a request is pending.</li>"
        f"{agu_detail}"
        f"</ul><h3>Wrapper fields</h3><table><tbody>{operands}</tbody></table>"
        f'<p class="source">Source: <code>{SCOPED_SAIL}</code>; form <code>{escape(source["form_id"])}</code>.</p></section>'
    )


def _manual_op(op: dict[str, Any]) -> dict[str, Any]:
    name = str(op.get("name") or op.get("mnemonic"))
    try:
        manual = _tile_index()[name]
    except KeyError as exc:
        raise ValueError(f"unresolved PTO 0.59.1 Tile operation: {name}") from exc
    normative = {
        r["name"]: r
        for r in tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
    }[name]
    for field in (
        "engine",
        "family",
        "function",
        "semantic_handler",
        "legality_handler",
    ):
        if op.get(field) != normative.get(field):
            raise ValueError(f"non-normative Tile record for {name}: {field}")
    return manual


def tile_summary(op: dict[str, Any], catalog: Any = None) -> str:
    return str(_manual_op(op)["summary"])


def _items(title: str, values: list[str]) -> str:
    if not values:
        return ""
    return (
        f"<h3>{escape(title)}</h3><ul>"
        + "".join(f"<li>{escape(v)}</li>" for v in values)
        + "</ul>"
    )


def tile_detail(op: dict[str, Any], catalog: Any = None) -> str:
    manual = _manual_op(op)
    contract = manual["contract"]
    operands = "".join(
        f"<tr><td><code>{escape(o['field'])}</code></td><td>{escape(o['role'])}</td></tr>"
        for o in contract.get("operands", [])
    )
    selector = op.get("selector") or f"Function={op['function']}"
    return (
        '<section class="tile-contract"><h2>Tile operation contract</h2>'
        f"<p>{escape(manual['summary'])}</p><dl><dt>Engine</dt><dd><code>{escape(manual['engine'])}</code></dd>"
        f"<dt>Carrier</dt><dd><code>{escape(op['command_mnemonic'])}</code></dd>"
        f"<dt>Selector</dt><dd><code>{escape(str(selector))}</code></dd>"
        f"<dt>Semantic handler</dt><dd><code>{escape(op['semantic_handler'])}</code></dd>"
        f'<dt>ASL source</dt><dd><a href="{escape(manual["source_url"])}"><code>{escape(manual["source_path"])}</code></a></dd></dl>'
        f"<h3>Operands</h3><table><tbody>{operands}</tbody></table>"
        + _items("Legality", contract.get("legality", []))
        + _items("Defaults", contract.get("defaults", []))
        + _items("State effects", contract.get("state_effects", []))
        + _items("Memory effects", contract.get("memory_effects", []))
        + _items("Ordering", contract.get("ordering", []))
        + _items("Exceptions", contract.get("exceptions", []))
        + "</section>"
    )


def validate_coverage() -> list[str]:
    errors = []
    scoped = tagged_json("isa/v0.59/state/pto_scalar_forms.json")["scoped_forms"]
    ops = tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
    if len(scoped) != 705:
        errors.append(f"scoped count: {len(scoped)}")
    if len(ops) != 119:
        errors.append(f"Tile count: {len(ops)}")
    for row in scoped:
        try:
            _source_row(row)
        except ValueError as exc:
            errors.append(str(exc))
    for op in ops:
        try:
            _manual_op(op)
        except ValueError as exc:
            errors.append(str(exc))
    return errors
