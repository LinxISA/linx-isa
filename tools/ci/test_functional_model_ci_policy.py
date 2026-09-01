#!/usr/bin/env python3
from __future__ import annotations

import unittest

from tools.ci.check_functional_model_ci_policy import policy_errors


class FunctionalModelCiPolicyTests(unittest.TestCase):
    def evaluate(
        self,
        *,
        event_name: str = "pull_request",
        repository: str = "LinxISA/linx-isa",
        head_repository: str = "LinxISA/linx-isa",
        draft: bool = True,
        functional_result: str = "success",
    ) -> list[str]:
        return policy_errors(
            event_name=event_name,
            repository=repository,
            head_repository=head_repository,
            pull_request_draft=draft,
            functional_result=functional_result,
            required_results=["success"] * 5,
        )

    def test_same_repository_draft_pr_runs_self_hosted_gate(self) -> None:
        self.assertEqual(self.evaluate(draft=True), [])

    def test_same_repository_ready_pr_runs_self_hosted_gate(self) -> None:
        self.assertEqual(self.evaluate(draft=False), [])

    def test_main_push_runs_self_hosted_gate(self) -> None:
        self.assertEqual(
            self.evaluate(event_name="push", head_repository="", draft=False), []
        )

    def test_fork_pr_is_explicitly_blocked_when_self_hosted_job_is_skipped(self) -> None:
        errors = self.evaluate(
            head_repository="contributor/linx-isa",
            functional_result="skipped",
        )
        self.assertTrue(any("fork pull requests cannot execute" in error for error in errors))

    def test_authorized_job_failure_blocks_aggregate_guard(self) -> None:
        errors = self.evaluate(functional_result="failure")
        self.assertTrue(any("must succeed" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
