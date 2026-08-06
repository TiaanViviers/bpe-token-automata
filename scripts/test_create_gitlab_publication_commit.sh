#!/usr/bin/env bash
# Isolated commit-graph tests for protected-branch GitLab publication.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HELPER="${REPO_ROOT}/scripts/create_gitlab_publication_commit.sh"
TEST_REPO="$(mktemp -d)"
trap 'rm -rf "${TEST_REPO}"' EXIT

git init -q "${TEST_REPO}"
cd "${TEST_REPO}"
git config user.name "Publication Test"
git config user.email "publication-test@example.invalid"

make_tree() {
  local content="$1"
  local filename="${2:-README.md}"
  local blob
  blob="$(printf '%s\n' "${content}" | git hash-object -w --stdin)"
  printf '100644 blob %s\t%s\n' "${blob}" "${filename}" | git mktree
}

INITIAL_TREE="$(make_tree 'initial GitLab README')"
INITIAL_COMMIT="$(printf 'add README\n' | git commit-tree "${INITIAL_TREE}")"
SUBMISSION_TREE_1="$(make_tree 'verified project v1')"
SUBMISSION_1="$(printf 'project v1\n' | git commit-tree "${SUBMISSION_TREE_1}")"
git branch submission "${SUBMISSION_1}"
git branch remote-main "${INITIAL_COMMIT}"

PUBLICATION_1="$(GITHUB_SOURCE_COMMIT="${SUBMISSION_1}" "${HELPER}" submission remote-main gitlab-publication)"
test "$(git rev-parse "${PUBLICATION_1}^1")" = "${INITIAL_COMMIT}"
test "$(git rev-parse "${PUBLICATION_1}^2")" = "${SUBMISSION_1}"
test "$(git rev-parse "${PUBLICATION_1}^{tree}")" = "${SUBMISSION_TREE_1}"

git branch -f remote-main "${PUBLICATION_1}"
NO_OP="$(GITHUB_SOURCE_COMMIT="${SUBMISSION_1}" "${HELPER}" submission remote-main gitlab-publication)"
test "${NO_OP}" = "${PUBLICATION_1}"

SUBMISSION_TREE_2="$(make_tree 'verified project v2')"
SUBMISSION_2="$(printf 'project v2\n' | git commit-tree "${SUBMISSION_TREE_2}" -p "${SUBMISSION_1}")"
git branch -f submission "${SUBMISSION_2}"
PUBLICATION_2="$(GITHUB_SOURCE_COMMIT="${SUBMISSION_2}" "${HELPER}" submission remote-main gitlab-publication)"
test "$(git rev-parse "${PUBLICATION_2}^1")" = "${PUBLICATION_1}"
test "$(git rev-parse "${PUBLICATION_2}^2")" = "${SUBMISSION_2}"
test "$(git rev-parse "${PUBLICATION_2}^{tree}")" = "${SUBMISSION_TREE_2}"

# A GitLab ref that is directly in subtree history needs no wrapper commit.
git branch -f remote-main "${SUBMISSION_1}"
DIRECT_PUBLICATION="$(GITHUB_SOURCE_COMMIT="${SUBMISSION_2}" "${HELPER}" submission remote-main gitlab-publication)"
test "${DIRECT_PUBLICATION}" = "${SUBMISSION_2}"

# Rewritten/non-descendant subtree history must not be attached silently.
git branch -f remote-main "${PUBLICATION_1}"
UNRELATED_SUBMISSION="$(printf 'unrelated project v2\n' | git commit-tree "${SUBMISSION_TREE_2}")"
git branch -f submission "${UNRELATED_SUBMISSION}"
if GITHUB_SOURCE_COMMIT="${UNRELATED_SUBMISSION}" "${HELPER}" submission remote-main gitlab-publication >/dev/null 2>&1; then
  echo "Error: helper accepted non-descendant submission history." >&2
  exit 1
fi
git branch -f submission "${SUBMISSION_2}"

DRIFT_TREE="$(make_tree 'uncontrolled GitLab edit')"
DRIFT_COMMIT="$(printf 'uncontrolled edit\n' | git commit-tree "${DRIFT_TREE}" -p "${PUBLICATION_1}")"
git branch -f remote-main "${DRIFT_COMMIT}"
if GITHUB_SOURCE_COMMIT="${SUBMISSION_2}" "${HELPER}" submission remote-main gitlab-publication >/dev/null 2>&1; then
  echo "Error: helper accepted uncontrolled GitLab drift." >&2
  exit 1
fi

UNMANAGED_TREE="$(make_tree 'unexpected initial file' 'NOTES.md')"
UNMANAGED_COMMIT="$(printf 'unmanaged history\n' | git commit-tree "${UNMANAGED_TREE}")"
git branch -f remote-main "${UNMANAGED_COMMIT}"
if GITHUB_SOURCE_COMMIT="${SUBMISSION_2}" "${HELPER}" submission remote-main gitlab-publication >/dev/null 2>&1; then
  echo "Error: helper accepted unexpected unmanaged history." >&2
  exit 1
fi

echo "Protected GitLab publication commit tests passed."
