#!/usr/bin/env bash
# Configure the local university GitLab remote with project-only push guards.
set -euo pipefail

REMOTE_NAME='gitlab'
GITLAB_URL='git@git.cs.sun.ac.za:Computer-Science/cs345/2026/cs345/26455900-CS345.git'
SAFE_PUSH_REFSPEC='refs/heads/gitlab-publication:refs/heads/main'
LEGACY_PUSH_REFSPEC='refs/heads/submission:refs/heads/main'

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a Git repository." >&2
  exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

if [[ ! -x .githooks/pre-push ]]; then
  echo "Error: expected executable hook .githooks/pre-push is missing." >&2
  exit 1
fi

if git remote get-url "${REMOTE_NAME}" >/dev/null 2>&1; then
  current_url="$(git remote get-url "${REMOTE_NAME}")"
  if [[ "${current_url}" != "${GITLAB_URL}" ]]; then
    echo "Error: remote '${REMOTE_NAME}' already has an unexpected URL:" >&2
    echo "  ${current_url}" >&2
    echo "Expected:" >&2
    echo "  ${GITLAB_URL}" >&2
    echo "Refusing to overwrite it automatically." >&2
    exit 1
  fi
else
  git remote add "${REMOTE_NAME}" "${GITLAB_URL}"
fi

current_push_refspec="$(git config --local --get-all "remote.${REMOTE_NAME}.push" || true)"
if [[ -n "${current_push_refspec}" &&
      "${current_push_refspec}" != "${SAFE_PUSH_REFSPEC}" &&
      "${current_push_refspec}" != "${LEGACY_PUSH_REFSPEC}" ]]; then
  echo "Error: remote '${REMOTE_NAME}' already has an unexpected push refspec:" >&2
  echo "  ${current_push_refspec}" >&2
  echo "Refusing to overwrite it automatically." >&2
  exit 1
fi

current_hooks_path="$(git config --get core.hooksPath || true)"
if [[ -n "${current_hooks_path}" && "${current_hooks_path}" != ".githooks" ]]; then
  echo "Error: this clone already uses a different Git hooks path:" >&2
  echo "  ${current_hooks_path}" >&2
  echo "Refusing to overwrite it automatically; integrate the pre-push guard manually." >&2
  exit 1
fi

# A plain `git push gitlab` can now publish only the guarded publication branch.
git config --local --replace-all "remote.${REMOTE_NAME}.push" "${SAFE_PUSH_REFSPEC}"

# The hook additionally verifies the publication tree and rejects unsafe
# refspecs such as main:main.
git config --local core.hooksPath .githooks

echo "Configured guarded GitLab publication:"
echo "  remote:       ${REMOTE_NAME} (${GITLAB_URL})"
echo "  push mapping: gitlab-publication -> main"
echo "  hooks path:   .githooks"
echo
echo "No data was pushed. Before an approved publication, run:"
echo "  ./scripts/build_submission.sh"
echo "  ./scripts/verify_submission.sh"
echo "  git fetch gitlab main"
echo "  ./scripts/create_gitlab_publication_commit.sh submission refs/remotes/gitlab/main"
echo "  git push gitlab"
