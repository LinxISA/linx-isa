#!/usr/bin/env python3
"""Fail-closed PR aggregate policy for the push-only functional-model gate."""

from __future__ import annotations

import argparse


def policy_errors(
    *,
    event_name: str,
    repository: str,
    head_repository: str,
    pull_request_draft: bool,
    required_results: list[str],
) -> list[str]:
    del pull_request_draft  # Draft state changes pin readiness, not runner trust.
    errors: list[str] = []
    if event_name == "pull_request" and head_repository != repository:
        errors.append(
            "fork pull requests cannot trigger the base repository's push-only "
            "PTO functional-model required check; a maintainer must mirror the exact "
            "head to a trusted base-repository branch or use a separately authorized "
            "ephemeral lane"
        )
    elif event_name not in {"pull_request", "push"}:
        errors.append(f"unsupported static CI event: {event_name!r}")
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
    parser.add_argument("--required-result", action="append", default=[])
    arguments = parser.parse_args()
    errors = policy_errors(
        event_name=arguments.event_name,
        repository=arguments.repository,
        head_repository=arguments.head_repository,
        pull_request_draft=arguments.pull_request_draft == "true",
        required_results=arguments.required_result,
    )
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("OK: static aggregate and push-only functional-model policy passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
