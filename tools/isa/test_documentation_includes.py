#!/usr/bin/env python3
"""Regression tests for AsciiDoc include closure."""

from __future__ import annotations

import importlib.util
import io
import tempfile
from contextlib import redirect_stderr
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "docs" / "check_documentation.py"

spec = importlib.util.spec_from_file_location("check_documentation", CHECKER_PATH)
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

assert hasattr(checker, "_check_asciidoc_includes"), "documentation checker must validate AsciiDoc include closure"

with tempfile.TemporaryDirectory(prefix="linxisa-adoc-includes-") as temp_dir:
    root = Path(temp_dir)
    chapter = root / "docs" / "architecture" / "isa-manual" / "src" / "chapters" / "sample.adoc"
    chapter.parent.mkdir(parents=True)
    chapter.write_text("include::../generated/instructions/missing.adoc[]\n", encoding="utf-8")

    errors: list[str] = []
    with redirect_stderr(io.StringIO()):
        checker._check_asciidoc_includes(root, errors)
    assert errors == [
        "broken AsciiDoc include in docs/architecture/isa-manual/src/chapters/sample.adoc: "
        "../generated/instructions/missing.adoc"
    ]

    target = root / "docs" / "architecture" / "isa-manual" / "src" / "generated" / "instructions" / "missing.adoc"
    target.parent.mkdir(parents=True)
    target.write_text("= Present\n", encoding="utf-8")

    errors = []
    checker._check_asciidoc_includes(root, errors)
    assert not errors

print("ok: AsciiDoc include closure regression")
