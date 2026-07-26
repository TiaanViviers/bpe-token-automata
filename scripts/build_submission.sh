#!/usr/bin/env bash
# Build a local `submission` branch containing only the project/ subtree.
# Does not push anywhere. Use --allow-dirty to proceed with uncommitted changes.
set -euo pipefail

ALLOW_DIRTY=0

usage() {
  cat <<'EOF'
Usage: build_submission.sh [--allow-dirty]

Create or recreate a local `submission` branch via:
  git subtree split --prefix=project

Options:
  --allow-dirty   Proceed even if the working tree has uncommitted changes
  -h, --help      Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --allow-dirty)
      ALLOW_DIRTY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a Git repository." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

if [[ ! -d project ]]; then
  echo "Error: project/ directory not found at repository root." >&2
  exit 1
fi

if [[ "${ALLOW_DIRTY}" -eq 0 ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Error: working tree has uncommitted changes." >&2
    echo "Commit your changes first, or re-run with --allow-dirty." >&2
    exit 1
  fi
fi

echo "Splitting project/ into a submission commit via git subtree..."
SPLIT_ERR_FILE="$(mktemp)"
set +e
SPLIT_COMMIT="$(git subtree split --prefix=project 2>"${SPLIT_ERR_FILE}")"
SPLIT_STATUS=$?
set -e
SPLIT_ERR="$(cat "${SPLIT_ERR_FILE}" || true)"
rm -f "${SPLIT_ERR_FILE}"

if [[ "${SPLIT_STATUS}" -ne 0 ]]; then
  echo "Error: git subtree split failed:" >&2
  [[ -n "${SPLIT_ERR}" ]] && echo "${SPLIT_ERR}" >&2
  echo >&2
  echo "Ensure 'project/' exists in at least one commit on the current branch." >&2
  echo "Subtree split only sees committed history, not unstaged or staged-only files." >&2
  exit 1
fi

if [[ ! "${SPLIT_COMMIT}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Error: unexpected subtree split output: '${SPLIT_COMMIT}'" >&2
  [[ -n "${SPLIT_ERR}" ]] && echo "${SPLIT_ERR}" >&2
  exit 1
fi

git branch -f submission "${SPLIT_COMMIT}"

echo "Created/updated local branch 'submission' at commit:"
echo "${SPLIT_COMMIT}"
