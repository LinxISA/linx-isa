#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILLS_ROOT="${ROOT_DIR}/skills/linx-skills"
INSTALLER="${SKILLS_ROOT}/scripts/install_canonical_skills.sh"
TARGET_DIR="${1:-${CODEX_HOME:-$HOME/.codex}/skills}"

if [[ ! -x "${INSTALLER}" ]]; then
  echo "error: canonical installer missing or not executable: ${INSTALLER}" >&2
  echo "hint: run 'git submodule update --init --recursive skills/linx-skills' first." >&2
  exit 1
fi

bash "${INSTALLER}" "${TARGET_DIR}"

echo "canonical skill sync complete: ${TARGET_DIR}"
