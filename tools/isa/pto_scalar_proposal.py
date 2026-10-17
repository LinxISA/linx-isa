"""Verify the scalar projection against its sole PTO development golden."""

import hashlib
import json
from pathlib import Path


def apply_proposal(profile: Path, catalog: dict) -> dict:
    lock = json.loads((profile / "pto-scalar-proposal.lock.json").read_text())
    if lock.get("status") != "development-not-published" or lock.get("published_identity_compatible") is not False:
        raise ValueError("development golden cannot claim a published compatible identity")
    source = {key: value for key, value in catalog.items() if key != "source_lock"}
    encoded = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    if hashlib.sha256(encoded).hexdigest() != lock["catalogs"]["scalar_forms"]["sha256"]:
        raise ValueError("scalar projection differs from PTO golden")
    if source.get("form_count") != 473 or len(source.get("forms", [])) != 473:
        raise ValueError("PTO golden scalar inventory must contain 473 forms")
    return catalog
