#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from tools.ci.check_functional_model_ci_policy import policy_errors


ROOT = Path(__file__).resolve().parents[2]


class FunctionalModelCiPolicyTests(unittest.TestCase):
    def evaluate(
        self,
        *,
        event_name: str = "pull_request",
        repository: str = "LinxISA/linx-isa",
        head_repository: str = "LinxISA/linx-isa",
        draft: bool = True,
    ) -> list[str]:
        return policy_errors(
            event_name=event_name,
            repository=repository,
            head_repository=head_repository,
            pull_request_draft=draft,
            required_results=["success"] * 5,
        )

    def test_same_repository_draft_pr_passes_static_guard(self) -> None:
        self.assertEqual(self.evaluate(draft=True), [])

    def test_same_repository_ready_pr_passes_static_guard(self) -> None:
        self.assertEqual(self.evaluate(draft=False), [])

    def test_main_push_passes_static_guard(self) -> None:
        self.assertEqual(
            self.evaluate(event_name="push", head_repository="", draft=False), []
        )

    def test_fork_pr_is_explicitly_blocked_pending_trusted_push(self) -> None:
        errors = self.evaluate(head_repository="contributor/linx-isa")
        self.assertTrue(any("push-only" in error for error in errors))

    def test_pull_request_workflows_have_no_self_hosted_runner(self) -> None:
        for workflow in (ROOT / ".github/workflows").glob("*.yml"):
            text = workflow.read_text(encoding="utf-8")
            if "pull_request:" in text or "pull_request_target:" in text:
                self.assertNotIn("self-hosted", text, workflow)

    def test_functional_workflow_is_push_only_and_checks_out_current_sha(self) -> None:
        workflow = (
            ROOT / ".github/workflows/functional-model.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("name: PTO Functional Model Trusted Push", workflow)
        self.assertIn('branches: ["**"]', workflow)
        self.assertIn(
            "github.repository == 'LinxISA/linx-isa' && github.event_name == 'push'",
            workflow,
        )
        self.assertNotIn("pull_request:", workflow)
        self.assertNotIn("pull_request_target:", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)
        root_checkout = workflow.split("- uses: actions/checkout@v7", 1)[1].split(
            "- uses:", 1
        )[0]
        self.assertIn("ref: ${{ github.sha }}", root_checkout)
        self.assertIn("persist-credentials: false", root_checkout)
        self.assertNotIn("repository:", root_checkout)

    def test_required_check_contract_names_ruleset_identity_and_fork_path(self) -> None:
        contract = (
            ROOT / "docs/bringup/FUNCTIONAL_MODEL_CI_SECURITY.md"
        ).read_text(encoding="utf-8")
        for token in (
            ".github/workflows/functional-model.yml",
            "PTO Functional Model Trusted Push",
            "PTO functional-model execution (trusted push)",
            "rulesets",
            "mirror the exact",
            "ephemeral runner lane",
        ):
            self.assertIn(token, contract)


if __name__ == "__main__":
    unittest.main()
