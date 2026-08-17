#!/usr/bin/env python3
"""Regression tests for active agent/navigation routing."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/isa/check_agent_navigation.py"


class AgentNavigationTest(unittest.TestCase):
    def run_checker(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(CHECKER), "--root", str(root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def write_entrypoints(self, root: Path, body: str) -> None:
        body += (
            "Tile engines: VEC SFU TLSU CUBE. "
            "TEPL is the encoding carrier, not an engine.\n"
        )
        paths = (
            Path("README.md"),
            Path("AGENTS.md"),
            Path("docs/README.md"),
            Path("docs/bringup/README.md"),
            Path("docs/bringup/GETTING_STARTED.md"),
            Path("docs/zh/bringup/README.md"),
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
        for relative in paths:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        lang_map = root / "docs/zh/assets/lang-map.json"
        lang_map.parent.mkdir(parents=True, exist_ok=True)
        lang_map.write_text("{}\n", encoding="utf-8")
        compatibility_pages = {
            Path("docs/bringup/AVS_CONTRACT.md"): (
                "Current ISA: isa/v0.58/linxisa-v0.58.json. "
                "v0.57 PASS results do not transfer.\n"
            ),
            Path("docs/zh/bringup/AVS_CONTRACT.md"): (
                "当前 ISA：isa/v0.58/linxisa-v0.58.json。"
                "v0.57 PASS 结果不得转移。\n"
            ),
        }
        for relative, text in compatibility_pages.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def test_rejects_historical_profile_as_active_agent_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n"
                "Assembly examples: docs/reference/examples/v0.57/\n",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("historical route", result.stderr)

    def test_rejects_historical_profile_from_root_readme(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n",
            )
            (root / "README.md").write_text(
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n"
                "Use isa/v0.57/ for implementation.\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("historical route", result.stderr)

    def test_rejects_chinese_archive_from_active_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n",
            )
            (root / "docs/zh/bringup/README.md").write_text(
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n"
                "Historical checklist: docs/zh/archive/v0.58/checklist.md\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("historical route", result.stderr)

    def test_rejects_v057_described_as_active_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n",
            )
            (root / "docs/bringup/README.md").write_text(
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n"
                "The active v0.57 contract defines the architecture.\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale active profile", result.stderr)

    def test_accepts_only_current_v058_agent_routes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n"
                "Historical material is non-normative and excluded from agent routing.\n",
            )

            result = self.run_checker(root)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unpinned_submodule_update_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n"
                "Run git submodule update --remote compiler/llvm.\n",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unpinned submodule route", result.stderr)

    def test_rejects_unpinned_route_in_project_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n",
            )
            path = root / "docs/project/extra-runbook.md"
            path.write_text(
                "Run git submodule update --remote emulator/qemu.\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("active project guidance", result.stderr)

    def test_rejects_compatibility_page_without_non_transfer_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n",
            )
            (root / "docs/zh/bringup/AVS_CONTRACT.md").write_text(
                "当前 ISA：isa/v0.58/linxisa-v0.58.json。v0.57 仍然有效。\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("lacks non-transfer contract", result.stderr)

    def test_rejects_agent_contract_without_current_tile_engine_taxonomy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_entrypoints(
                root,
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n",
            )
            (root / "AGENTS.md").write_text(
                "Canonical ISA: isa/v0.58/linxisa-v0.58.json\n",
                encoding="utf-8",
            )

            result = self.run_checker(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("tile engine taxonomy", result.stderr)


if __name__ == "__main__":
    unittest.main()
