#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_SUBMODULE="skills/linx-skills"
SKILLS_ROOT="${ROOT_DIR}/${SKILLS_SUBMODULE}"
INSTALLER="${SKILLS_ROOT}/scripts/install_canonical_skills.sh"

TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
PULL_LATEST=0
SUMMARY_OUT="${ROOT_DIR}/docs/bringup/agent_runs/skills_evolution/latest.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pull-latest)
      PULL_LATEST=1
      shift
      ;;
    --target-dir)
      TARGET_DIR="$2"
      shift 2
      ;;
    --summary-out)
      SUMMARY_OUT="$2"
      shift 2
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      echo "usage: $0 [--pull-latest] [--target-dir <dir>] [--summary-out <path>]" >&2
      exit 2
      ;;
  esac
done

if [[ "${PULL_LATEST}" -eq 1 ]]; then
  git -C "${ROOT_DIR}" submodule update --init --recursive "${SKILLS_SUBMODULE}"
  git -C "${SKILLS_ROOT}" fetch origin main
  git -C "${SKILLS_ROOT}" checkout origin/main
fi

if [[ ! -x "${INSTALLER}" ]]; then
  echo "error: canonical installer missing or not executable: ${INSTALLER}" >&2
  echo "hint: run 'git submodule update --init --recursive ${SKILLS_SUBMODULE}' first." >&2
  exit 1
fi

bash "${INSTALLER}" "${TARGET_DIR}"

skills_sha="$(git -C "${SKILLS_ROOT}" rev-parse HEAD)"
skills_branch="$(git -C "${SKILLS_ROOT}" rev-parse --abbrev-ref HEAD || true)"
status_short="$(git -C "${SKILLS_ROOT}" status --short || true)"
generated_utc="$(date -u '+%Y-%m-%d %H:%M:%SZ')"

mkdir -p "$(dirname "${SUMMARY_OUT}")"
LINX_GEN_UTC="${generated_utc}" \
LINX_SKILLS_SHA="${skills_sha}" \
LINX_SKILLS_BRANCH="${skills_branch}" \
LINX_TARGET_DIR="${TARGET_DIR}" \
LINX_STATUS_SHORT="${status_short}" \
python3 - "${SUMMARY_OUT}" <<'PY'
import json
import os
import sys

out_path = sys.argv[1]
payload = {
    "generated_utc": os.environ["LINX_GEN_UTC"],
    "skills_submodule": "skills/linx-skills",
    "skills_sha": os.environ["LINX_SKILLS_SHA"],
    "skills_branch": os.environ["LINX_SKILLS_BRANCH"],
    "target_dir": os.environ["LINX_TARGET_DIR"],
    "status_short": os.environ["LINX_STATUS_SHORT"].splitlines(),
}
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
    f.write("\n")
PY

echo "canonical skill sync complete: ${TARGET_DIR}"
echo "skills summary written: ${SUMMARY_OUT}"
