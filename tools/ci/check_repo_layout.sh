#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

fail=0

allowed_top_level_dirs=(
  ".cursor"
  ".github"
  "avs"
  "compiler"
  "docs"
  "emulator"
  "isa"
  "kernel"
  "lib"
  "rtl"
  "skills"
  "tools"
  "workloads"
)

while IFS= read -r tracked_dir; do
  tracked_dir="${tracked_dir%/}"
  allowed=0
  for expected in "${allowed_top_level_dirs[@]}"; do
    if [[ "$tracked_dir" == "$expected" ]]; then
      allowed=1
      break
    fi
  done
  if [[ "$allowed" -eq 0 ]]; then
    echo "error: unexpected tracked top-level directory: $tracked_dir" >&2
    fail=1
  fi
done < <(git ls-files | awk -F/ 'NF > 1 {print $1}' | LC_ALL=C sort -u)

must_not_exist=(
  "spec"
  "compiler/linx-llvm"
  "emulator/linx-qemu"
  "examples"
  "models"
  "toolchain"
  "tests"
  "docs/validation/avs"
  "tools/ctuning"
  "tools/libc"
  "tools/glibc"
  "tools/pto"
  "lib/pto"
  "workloads/benchmarks"
  "workloads/examples"
  "~"
)

for p in "${must_not_exist[@]}"; do
  if [[ -e "$p" ]]; then
    echo "error: removed path still exists: $p" >&2
    fail=1
  fi
done

if [[ ! -d avs || -L avs ]]; then
  echo "error: avs must be a real directory (not symlink)" >&2
  fail=1
fi

if [[ ! -d isa || -L isa ]]; then
  echo "error: isa must be a real directory (not symlink)" >&2
  fail=1
fi

# Domain-submodule-only checks
if [[ -d compiler ]]; then
  extra="$(find compiler -mindepth 1 -maxdepth 1 -not -name llvm -not -name ptoas -not -name .omx -print -quit)"
  if [[ -n "$extra" ]]; then
    echo "error: compiler/ contains unexpected entries (allowed: compiler/llvm, compiler/ptoas; found: $extra)" >&2
    fail=1
  fi
fi

if [[ -d emulator ]]; then
  extra="$(find emulator -mindepth 1 -maxdepth 1 -not -name qemu -not -name .omx -print -quit)"
  if [[ -n "$extra" ]]; then
    echo "error: emulator/ must contain only emulator/qemu (found: $extra)" >&2
    fail=1
  fi
fi

if [[ -d rtl ]]; then
  extra="$(find rtl -mindepth 1 -maxdepth 1 -not -name LinxCore -not -name README.md -not -name .omx -print -quit)"
  if [[ -n "$extra" ]]; then
    echo "error: rtl/ contains unexpected entries: $extra" >&2
    fail=1
  fi
  if [[ ! -d rtl/LinxCore ]]; then
    echo "error: missing rtl/LinxCore submodule" >&2
    fail=1
  fi
fi

expected_submodules=(
  "compiler/llvm"
  "compiler/ptoas"
  "emulator/qemu"
  "kernel/linux"
  "lib/glibc"
  "lib/mesa3d"
  "lib/musl"
  "rtl/LinxCore"
  "skills/linx-skills"
  "tools/LinxCoreModel"
  "tools/Linx-TileOP-API"
  "tools/model"
  "tools/pyCircuit"
  "workloads/pto_kernels"
)

configured_submodules="$({
  git config -f .gitmodules --get-regexp '^submodule\..*\.path$' \
    | awk '{print $2}' | LC_ALL=C sort
} || true)"
canonical_submodules="$(printf '%s\n' "${expected_submodules[@]}" | LC_ALL=C sort)"
if ! diff -u \
  <(printf '%s\n' "$canonical_submodules") \
  <(printf '%s\n' "$configured_submodules") >&2; then
  echo "error: .gitmodules paths do not match the canonical topology" >&2
  fail=1
fi

tracked_gitlinks="$(git ls-files -s | awk '$1 == "160000" {print $4}' | LC_ALL=C sort)"
if ! diff -u \
  <(printf '%s\n' "$canonical_submodules") \
  <(printf '%s\n' "$tracked_gitlinks") >&2; then
  echo "error: tracked gitlinks do not match the documented submodule topology" >&2
  fail=1
fi

duplicate_urls="$(git config -f .gitmodules --get-regexp '^submodule\..*\.url$' \
  | awk '{count[$2]++; names[$2] = names[$2] " " $1} END {for (url in count) if (count[url] > 1) print url names[url]}')"
if [[ -n "$duplicate_urls" ]]; then
  echo "error: duplicate submodule URL(s):" >&2
  printf '%s\n' "$duplicate_urls" >&2
  fail=1
fi

while IFS= read -r p; do
  [[ -n "$p" ]] || continue
  section="$(git config -f .gitmodules --get-regexp '^submodule\..*\.path$' \
    | awk -v path="$p" '$2 == path { sub(/^submodule\./, "", $1); sub(/\.path$/, "", $1); print $1 }')"
  url="$(git config -f .gitmodules --get "submodule.$section.url" || true)"
  branch="$(git config -f .gitmodules --get "submodule.$section.branch" || true)"
  update="$(git config -f .gitmodules --get "submodule.$section.update" || true)"
  ignore="$(git config -f .gitmodules --get "submodule.$section.ignore" || true)"

  if [[ -z "$url" || -z "$branch" || "$update" != "checkout" ]]; then
    echo "error: incomplete submodule policy for $p (url/branch/update=checkout required)" >&2
    fail=1
  fi
  if [[ -n "$ignore" ]]; then
    echo "error: submodule ignore policy hides state for $p: $ignore" >&2
    fail=1
  fi
  mode="$(git ls-files -s -- "$p" | awk 'NR == 1 {print $1}')"
  gitlink_sha="$(git ls-files -s -- "$p" | awk 'NR == 1 {print $2}')"
  if [[ "$mode" != "160000" ]]; then
    echo "error: submodule path is not a tracked gitlink: $p" >&2
    fail=1
  elif [[ -e "$p/.git" ]] && ! git -C "$p" cat-file -e "${gitlink_sha}^{commit}" 2>/dev/null; then
    echo "error: submodule gitlink commit is unreachable in the initialized leaf: $p@$gitlink_sha" >&2
    fail=1
  fi
  if [[ -e "$p/.git" ]]; then
    dirty_state="$(git -C "$p" status --porcelain --untracked-files=all 2>/dev/null || true)"
    if [[ -n "$dirty_state" ]]; then
      echo "error: submodule worktree is dirty: $p" >&2
      printf '%s\n' "$dirty_state" | sed 's/^/  /' >&2
      fail=1
    fi
    if [[ "${LINX_LAYOUT_VERIFY_REMOTE:-0}" == "1" ]] &&
       ! git -C "$p" fetch --quiet --no-tags --no-write-fetch-head origin "$gitlink_sha"; then
      echo "error: submodule gitlink is not fetchable from origin: $p@$gitlink_sha" >&2
      fail=1
    fi
  fi
done < <(printf '%s\n' "$configured_submodules")

while IFS= read -r status_line; do
  [[ -n "$status_line" ]] || continue
  marker="${status_line:0:1}"
  path="$(printf '%s\n' "$status_line" | awk '{print $2}')"
  if [[ "$marker" == "+" || "$marker" == "U" ]]; then
    echo "error: submodule checkout does not match the recorded gitlink: $path ($status_line)" >&2
    fail=1
  fi
done < <(git submodule status --recursive 2>/dev/null || true)

# Topology rule: only the superproject root may define LinxISA repo links.
while IFS= read -r gm; do
  rel="${gm#./}"
  if [[ "$rel" == ".gitmodules" ]]; then
    continue
  fi
  if rg -n -e 'github\.com/LinxISA/' -e 'git@github\.com:LinxISA/' "$gm" >/dev/null 2>&1; then
    echo "error: non-root .gitmodules references LinxISA repo links: $rel" >&2
    rg -n -e 'github\.com/LinxISA/' -e 'git@github\.com:LinxISA/' "$gm" >&2 || true
    fail=1
  fi
done < <(find . -path './.git' -prune -o -name .gitmodules -print)

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "OK: repository layout policy passed"

python3 tools/ci/check_component_lock.py --root .
