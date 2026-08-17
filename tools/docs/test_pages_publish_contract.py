#!/usr/bin/env python3
"""Lock the GitHub Pages workflow to the Chinese documentation artifact."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/pages.yml"


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")

    required = (
        "uses: actions/checkout@v7",
        "uses: actions/setup-python@v7",
        "python3 docs/check_documentation.py --root .",
        'mkdocs build --strict --site-dir "${RUNNER_TEMP}/site-en"',
        "mkdocs build --strict --config-file mkdocs.zh.yml --site-dir site",
        "uses: actions/upload-pages-artifact@v5",
        "path: site/",
    )
    for token in required:
        assert token in text, f"Pages workflow is missing: {token}"

    assert "run: mkdocs build --strict\n" not in text
    assert text.index("docs/check_documentation.py") < text.index("site-en")
    assert text.index("site-en") < text.index("mkdocs.zh.yml")
    print("ok: GitHub Pages publishes the strict Chinese documentation build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
