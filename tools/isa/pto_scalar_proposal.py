"""Apply the explicit scalar proposal without rewriting the published PTO input."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


def apply_proposal(profile: Path, catalog: dict) -> dict:
    baseline = {key: value for key, value in catalog.items() if key != "source_lock"}
    baseline_hash = hashlib.sha256(
        (json.dumps(baseline, indent=2, sort_keys=True) + "\n").encode()
    ).hexdigest()
    if baseline_hash != "2767dc6302e8d777b517c198d3ead8a5acb62602c26f517eb9ee581bc4afd4da":
        raise ValueError("published PTO 0.58.7 scalar baseline was modified")
    proposal_path = profile / "state/pto_scalar_proposal.json"
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    if proposal.get("status") != "proposal" or proposal.get("baseline_release") != "0.58.7":
        raise ValueError("scalar overlay must be an explicit proposal against PTO 0.58.7")
    result = copy.deepcopy(catalog)
    forms = {form["form_id"]: form for form in result["forms"]}
    replacements = proposal["forms"]
    ids = [form["form_id"] for form in replacements]
    if len(ids) != 44 or len(set(ids)) != 44 or not set(ids) <= forms.keys():
        raise ValueError("scalar proposal must replace exactly 44 existing PTO forms")
    expected = {
        *(f"{prefix}.{size}" for prefix in ("LR", "SC") for size in ("B", "H", "W", "D")),
        *(f"SWAP{size}" for size in ("B", "H", "W", "D")),
        *(f"{prefix}.{op}" for prefix in ("LW", "LD", "SW", "SD")
          for op in ("ADD", "AND", "OR", "XOR", "SMAX", "SMIN", "UMAX", "UMIN")),
    }
    if {form["mnemonic"] for form in replacements} != expected:
        raise ValueError("scalar proposal changes an instruction outside its atomic scope")
    if any(forms[form["form_id"]]["mnemonic"] != form["mnemonic"] for form in replacements):
        raise ValueError("scalar proposal changed a source form's mnemonic identity")
    forms.update({form["form_id"]: form for form in replacements})
    result["forms"] = [forms[form["form_id"]] for form in result["forms"]]
    additions = proposal.get("additional_forms", [])
    if {form["mnemonic"] for form in additions} != {
        "SW.SUB", "SD.SUB", "SB.ADD", "SB.SUB", "SH.ADD", "SH.SUB", "SYNC.CORE"
    } or len(additions) != 7:
        raise ValueError("scalar proposal must add the six store forms and PTO SYNC.CORE")
    if any(form["form_id"] in forms for form in additions):
        raise ValueError("scalar proposal addition duplicates a published form")
    result["forms"].extend(additions)
    result["form_count"] = len(result["forms"])
    lock = json.loads((profile / "pto-scalar-proposal.lock.json").read_text())
    digest = hashlib.sha256(json.dumps(
        result["forms"], sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()
    if lock.get("status") != "proposal-not-published" or lock.get("published_identity_compatible") is not False:
        raise ValueError("scalar proposal cannot claim a published compatible identity")
    if digest != lock.get("effective_forms_sha256"):
        raise ValueError("effective scalar forms differ from the pinned PTO proposal")
    return result
