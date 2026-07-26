#!/usr/bin/env bash
# Verify that an exported submission branch looks like a clean, standalone project/.
set -euo pipefail

BRANCH="${1:-submission}"
FAILED=0

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a Git repository." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

if ! git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  echo "Error: branch '${BRANCH}' does not exist." >&2
  exit 1
fi

echo "Verifying export branch: ${BRANCH}"
echo "Commit: $(git rev-parse "${BRANCH}")"
echo

mapfile -t EXPORT_FILES < <(git ls-tree -r --name-only "${BRANCH}")

path_present() {
  local needle="$1"
  local entry
  for entry in "${EXPORT_FILES[@]}"; do
    if [[ "${entry}" == "${needle}" || "${entry}" == "${needle}/"* ]]; then
      return 0
    fi
  done
  return 1
}

# Required submission paths (present at exported root).
REQUIRED_PATHS=(
  "README.md"
  "pyproject.toml"
  "Makefile"
  "src"
  "tests"
  "tests/test_package_smoke.py"
  "docs"
  "configs"
  "configs/experiments"
  "data"
  "data/dictionaries"
  "data/examples"
  "results"
  "results/raw"
  "results/tables"
  "results/figures"
  "report"
)

echo "== Required paths =="
for path in "${REQUIRED_PATHS[@]}"; do
  if path_present "${path}"; then
    echo "  OK   ${path}"
  else
    echo "  FAIL missing required path: ${path}"
    FAILED=1
  fi
done
echo

# Paths that must never appear in the GitLab export.
FORBIDDEN_PATHS=(
  "agent"
  "team"
  "research"
  ".github"
  "scripts/build_submission.sh"
  "scripts/verify_submission.sh"
)

echo "== Forbidden collaborative paths =="
for path in "${FORBIDDEN_PATHS[@]}"; do
  if path_present "${path}"; then
    echo "  FAIL forbidden path present: ${path}"
    FAILED=1
  else
    echo "  OK   absent: ${path}"
  fi
done
echo

# Likely secrets / sensitive artefacts that must not ship in the export.
SECRET_PATTERNS=(
  '^\.env$'
  '^\.env\.'
  'credentials\.json$'
  'secrets\.json$'
  '\.pem$'
  '\.key$'
)

echo "== Secret / sensitive file scan =="
SECRET_HIT=0
for entry in "${EXPORT_FILES[@]}"; do
  for pattern in "${SECRET_PATTERNS[@]}"; do
    if [[ "${entry}" =~ ${pattern} ]]; then
      echo "  FAIL suspicious path: ${entry}"
      SECRET_HIT=1
      FAILED=1
    fi
  done
done
if [[ "${SECRET_HIT}" -eq 0 ]]; then
  echo "  OK   no likely secret paths found"
fi
echo

echo "== Exported file list =="
printf '  %s\n' "${EXPORT_FILES[@]}"
echo

if [[ "${FAILED}" -ne 0 ]]; then
  echo "Verification FAILED for branch '${BRANCH}'."
  exit 1
fi

echo "Verification PASSED for branch '${BRANCH}'."
