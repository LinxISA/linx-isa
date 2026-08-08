#!/usr/bin/env python3
"""Validate active agent and contributor entry points."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ENTRYPOINTS = (
    Path("README.md"),
    Path("AGENTS.md"),
    Path("docs/README.md"),
    Path("docs/bringup/GETTING_STARTED.md"),
    Path("docs/zh/bringup/GETTING_STARTED.md"),
    Path("docs/zh/index.md"),
    Path("docs/bringup/phases/02_isa_spec.md"),
    Path("docs/zh/bringup/phases/02_isa_spec.md"),
    Path("docs/bringup/phases/04_rtl.md"),
    Path("docs/zh/bringup/phases/04_rtl.md"),
    Path("docs/zh/architecture/isa-manual/README.md"),
    Path("docs/project/repository-flow.md"),
    Path("docs/zh/project/repository-flow.md"),
    Path("docs/project/navigation.md"),
    Path("docs/project/new-agent-sop.md"),
    Path("skills/linx-omx/SKILL.md"),
)
ROUTE_ONLY_ENTRYPOINTS = (Path("docs/zh/assets/lang-map.json"),)
COMPATIBILITY_ENTRYPOINTS = {
    Path("docs/bringup/AVS_CONTRACT.md"): ("v0.57", "do not transfer"),
    Path("docs/zh/bringup/AVS_CONTRACT.md"): ("v0.57", "不得转移"),
}
CURRENT_CONTRACT = "isa/v0.58/linxisa-v0.58.json"
HISTORICAL_ROUTES = (
    "isa/v0.57/",
    "docs/archive/",
    "docs/reference/examples/v0.57/",
    "architecture/v0.57-",
)
UNPINNED_SUBMODULE_ROUTE = "git submodule update --remote"
UNPINNED_ROUTE_ROOTS = (Path("docs/project"), Path("docs/zh/project"))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in (*ENTRYPOINTS, *ROUTE_ONLY_ENTRYPOINTS):
        path = root / relative
        if not path.is_file():
            errors.append(f"missing active agent entrypoint: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if relative in ENTRYPOINTS and CURRENT_CONTRACT not in text:
            errors.append(
                f"active agent entrypoint does not name {CURRENT_CONTRACT}: {relative}"
            )
        for route in HISTORICAL_ROUTES:
            if route in text:
                errors.append(f"historical route in active agent entrypoint: {relative}: {route}")
        if UNPINNED_SUBMODULE_ROUTE in text:
            errors.append(f"unpinned submodule route in active agent entrypoint: {relative}")
    for relative, required_tokens in COMPATIBILITY_ENTRYPOINTS.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing compatibility entrypoint: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if CURRENT_CONTRACT not in text:
            errors.append(
                f"compatibility entrypoint does not name {CURRENT_CONTRACT}: {relative}"
            )
        for token in required_tokens:
            if token not in text:
                errors.append(
                    f"compatibility entrypoint lacks non-transfer contract: {relative}: {token}"
                )
        if UNPINNED_SUBMODULE_ROUTE in text:
            errors.append(f"unpinned submodule route in compatibility entrypoint: {relative}")
    for relative_root in UNPINNED_ROUTE_ROOTS:
        directory = root / relative_root
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".tex"}:
                continue
            if UNPINNED_SUBMODULE_ROUTE in path.read_text(encoding="utf-8"):
                errors.append(
                    "unpinned submodule route in active project guidance: "
                    f"{path.relative_to(root)}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args()
    errors = validate(arguments.root.resolve())
    if errors:
        print("\n".join(f"error: {error}" for error in errors), file=sys.stderr)
        return 1
    print("agent navigation closure passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
