#!/usr/bin/env python3
"""Fail-closed policy for the persistent functional-model CI runner."""

from __future__ import annotations

import argparse


def self_hosted_authorized(
    event_name: str, repository: str, head_repository: str
) -> bool:
    if event_name == "push":
        return True
    return event_name == "pull_request" and head_repository == repository


def policy_errors(
    *,
    event_name: str,
    repository: str,
    head_repository: str,
    pull_request_draft: bool,
    functional_result: str,
    required_results: list[str],
) -> list[str]:
    del pull_request_draft  # Draft state changes pin readiness, not runner trust.
    errors: list[str] = []
    authorized = self_hosted_authorized(event_name, repository, head_repository)
    if event_name == "pull_request" and not authorized:
        errors.append(
            "fork pull requests cannot execute PR-controlled code on the persistent "
            "self-hosted functional-model runner; a maintainer-authorized isolated "
            "workflow is required"
        )
    elif not authorized:
        errors.append(f"unsupported functional-model CI event: {event_name!r}")
    elif functional_result != "success":
        errors.append(
            "authorized functional-model job must succeed, got "
            f"{functional_result!r}"
        )
    for index, result in enumerate(required_results, start=1):
        if result != "success":
            errors.append(f"required GitHub-hosted/static job {index} is {result!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--head-repository", default="")
    parser.add_argument(
        "--pull-request-draft", choices=("true", "false"), default="false"
    )
    parser.add_argument("--functional-result", required=True)
    parser.add_argument("--required-result", action="append", default=[])
    arguments = parser.parse_args()
    errors = policy_errors(
        event_name=arguments.event_name,
        repository=arguments.repository,
        head_repository=arguments.head_repository,
        pull_request_draft=arguments.pull_request_draft == "true",
        functional_result=arguments.functional_result,
        required_results=arguments.required_result,
    )
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("OK: functional-model CI runner and aggregate guard policy passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
