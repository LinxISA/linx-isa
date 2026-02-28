#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_ROOT="${ROOT_DIR}/skills/linx-skills"
GUARD_SCRIPT="${SKILLS_ROOT}/scripts/check_skill_change_scope.py"
VALIDATOR="${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py"

BASE_REF="origin/main"
SUMMARY_OUT=""
COMMIT_MSG=""
PUSH_AFTER_COMMIT=0
MAX_CHANGED_SKILLS=8

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE_REF="$2"
      shift 2
      ;;
    --summary-out)
      SUMMARY_OUT="$2"
      shift 2
      ;;
    --commit-message)
      COMMIT_MSG="$2"
      shift 2
      ;;
    --push)
      PUSH_AFTER_COMMIT=1
      shift
      ;;
    --max-changed-skills)
      MAX_CHANGED_SKILLS="$2"
      shift 2
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      echo "usage: $0 [--base <ref>] [--summary-out <path>] [--commit-message <msg>] [--push] [--max-changed-skills <n>]" >&2
      exit 2
      ;;
  esac
done

if [[ -z "${SUMMARY_OUT}" ]]; then
  stamp="$(date -u '+%Y%m%dT%H%M%SZ')"
  SUMMARY_OUT="${ROOT_DIR}/docs/bringup/agent_runs/skills_evolution/summary-${stamp}.md"
fi

if [[ ! -d "${SKILLS_ROOT}" ]]; then
  echo "error: missing skills submodule checkout at ${SKILLS_ROOT}" >&2
  exit 1
fi

if [[ ! -x "${GUARD_SCRIPT}" ]]; then
  echo "error: missing scope guard script at ${GUARD_SCRIPT}" >&2
  exit 1
fi

if [[ ! -f "${VALIDATOR}" ]]; then
  echo "error: missing quick validator at ${VALIDATOR}" >&2
  exit 1
fi

python3 "${GUARD_SCRIPT}" --repo-root "${SKILLS_ROOT}" --base "${BASE_REF}" --max-changed-skills "${MAX_CHANGED_SKILLS}"

touched_skills="$(
  python3 - "${SKILLS_ROOT}" <<'PY'
import os
import subprocess
import sys

repo = sys.argv[1]
out = subprocess.check_output(["git", "-C", repo, "status", "--porcelain"], text=True)
touched = set()
for line in out.splitlines():
    if len(line) < 4:
        continue
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1].strip()
    top = path.split("/", 1)[0]
    if top.startswith("linx-"):
        touched.add(top)
for item in sorted(touched):
    print(item)
PY
)"

if [[ -n "${touched_skills}" ]]; then
  while IFS= read -r skill; do
    [[ -z "${skill}" ]] && continue
    if [[ -d "${SKILLS_ROOT}/${skill}" ]]; then
      python3 "${VALIDATOR}" "${SKILLS_ROOT}/${skill}"
    fi
  done <<< "${touched_skills}"
fi

skills_sha="$(git -C "${SKILLS_ROOT}" rev-parse HEAD)"
skills_branch="$(git -C "${SKILLS_ROOT}" rev-parse --abbrev-ref HEAD || true)"
status_short="$(git -C "${SKILLS_ROOT}" status --short || true)"
generated_utc="$(date -u '+%Y-%m-%d %H:%M:%SZ')"

mkdir -p "$(dirname "${SUMMARY_OUT}")"
{
  echo "# Skills Evolution Summary"
  echo
  echo "- Generated (UTC): ${generated_utc}"
  echo "- Base ref: ${BASE_REF}"
  echo "- Submodule SHA: ${skills_sha}"
  echo "- Submodule branch: ${skills_branch}"
  echo
  echo "## Touched skills"
  if [[ -n "${touched_skills}" ]]; then
    while IFS= read -r skill; do
      [[ -z "${skill}" ]] && continue
      echo "- ${skill}"
    done <<< "${touched_skills}"
  else
    echo "- none"
  fi
  echo
  echo "## Submodule status"
  if [[ -n "${status_short}" ]]; then
    echo '```'
    echo "${status_short}"
    echo '```'
  else
    echo "- clean"
  fi
} > "${SUMMARY_OUT}"

echo "wrote summary: ${SUMMARY_OUT}"

if [[ -n "${COMMIT_MSG}" ]]; then
  git -C "${SKILLS_ROOT}" add -A
  if git -C "${SKILLS_ROOT}" diff --cached --quiet; then
    echo "no staged skill changes to commit"
  else
    git -C "${SKILLS_ROOT}" commit -m "${COMMIT_MSG}"
    if [[ "${PUSH_AFTER_COMMIT}" -eq 1 ]]; then
      git -C "${SKILLS_ROOT}" push
    fi
    new_sha="$(git -C "${SKILLS_ROOT}" rev-parse HEAD)"
    echo "committed skills submodule changes: ${new_sha}"
    echo "next: commit submodule repin in superproject"
  fi
fi
