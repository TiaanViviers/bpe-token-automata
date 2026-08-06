#!/usr/bin/env bash
# Create a normal fast-forward publication commit for a protected GitLab main.
set -euo pipefail

SUBMISSION_REF="${1:-submission}"
REMOTE_MAIN_REF="${2:-refs/remotes/gitlab/main}"
OUTPUT_BRANCH="${3:-gitlab-publication}"

if [[ $# -gt 3 ]]; then
  echo "Usage: create_gitlab_publication_commit.sh [submission-ref] [remote-main-ref] [output-branch]" >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: not inside a Git repository." >&2
  exit 1
fi

if [[ "${OUTPUT_BRANCH}" == "main" || "${OUTPUT_BRANCH}" == "submission" ]]; then
  echo "Error: refusing to overwrite protected/generated branch '${OUTPUT_BRANCH}'." >&2
  exit 1
fi
git check-ref-format --branch "${OUTPUT_BRANCH}" >/dev/null

SUBMISSION_COMMIT="$(git rev-parse --verify "${SUBMISSION_REF}^{commit}")"
REMOTE_MAIN_COMMIT="$(git rev-parse --verify "${REMOTE_MAIN_REF}^{commit}")"
SUBMISSION_TREE="$(git rev-parse "${SUBMISSION_COMMIT}^{tree}")"
REMOTE_MAIN_TREE="$(git rev-parse "${REMOTE_MAIN_COMMIT}^{tree}")"
SOURCE_COMMIT="${GITHUB_SOURCE_COMMIT:-$(git rev-parse HEAD)}"

if [[ ! "${SOURCE_COMMIT}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Error: GitHub source commit is not a full SHA: '${SOURCE_COMMIT}'." >&2
  exit 1
fi

PUBLICATION_COMMIT=""

# An empty/directly initialised GitLab history needs no wrapper when it is
# already an ancestor of the verified subtree history.
if git merge-base --is-ancestor "${REMOTE_MAIN_COMMIT}" "${SUBMISSION_COMMIT}"; then
  PUBLICATION_COMMIT="${SUBMISSION_COMMIT}"
  echo "GitLab main is already an ancestor of submission; publishing submission directly." >&2
else
  LAST_PUBLICATION="$(
    git log --first-parent \
      --extended-regexp \
      --grep='^CS345-Submission-Commit: [0-9a-f]{40}$' \
      --format='%H' \
      -1 \
      "${REMOTE_MAIN_COMMIT}"
  )"

  if [[ -n "${LAST_PUBLICATION}" ]]; then
    PREVIOUS_SUBMISSION="$(
      git show -s --format='%B' "${LAST_PUBLICATION}" |
        sed -n 's/^CS345-Submission-Commit: \([0-9a-f]\{40\}\)$/\1/p' |
        tail -n 1
    )"

    if [[ -z "${PREVIOUS_SUBMISSION}" ]] || ! git cat-file -e "${PREVIOUS_SUBMISSION}^{commit}" 2>/dev/null; then
      echo "Error: previous publication has an invalid submission marker." >&2
      exit 1
    fi

    PREVIOUS_SUBMISSION_TREE="$(git rev-parse "${PREVIOUS_SUBMISSION}^{tree}")"
    if [[ "${REMOTE_MAIN_TREE}" != "${PREVIOUS_SUBMISSION_TREE}" ]]; then
      echo "Error: GitLab contents changed outside the controlled publication workflow." >&2
      echo "Refusing to overwrite that drift." >&2
      exit 1
    fi

    if ! git merge-base --is-ancestor "${PREVIOUS_SUBMISSION}" "${SUBMISSION_COMMIT}"; then
      echo "Error: new submission history does not descend from the previous submission." >&2
      exit 1
    fi

    if [[ "${PREVIOUS_SUBMISSION}" == "${SUBMISSION_COMMIT}" ]]; then
      PUBLICATION_COMMIT="${REMOTE_MAIN_COMMIT}"
      echo "GitLab already contains this verified submission; nothing to publish." >&2
    fi
  else
    mapfile -t INITIAL_FILES < <(git ls-tree -r --name-only "${REMOTE_MAIN_COMMIT}")
    if [[ "${#INITIAL_FILES[@]}" -ne 1 || "${INITIAL_FILES[0]}" != "README.md" ]]; then
      echo "Error: GitLab has unmanaged history with unexpected files." >&2
      echo "Only the known one-file README initialisation can be bridged automatically." >&2
      exit 1
    fi
    echo "Bridging the known initial GitLab README commit without force-pushing." >&2
  fi

  if [[ -z "${PUBLICATION_COMMIT}" ]]; then
    PUBLICATION_COMMIT="$(
      git commit-tree "${SUBMISSION_TREE}" \
        -p "${REMOTE_MAIN_COMMIT}" \
        -p "${SUBMISSION_COMMIT}" <<EOF
Publish verified project subtree

GitHub-Source-Commit: ${SOURCE_COMMIT}
CS345-Submission-Commit: ${SUBMISSION_COMMIT}
EOF
    )"
  fi
fi

if [[ "$(git rev-parse "${PUBLICATION_COMMIT}^{tree}")" != "${SUBMISSION_TREE}" ]]; then
  echo "Error: publication tree differs from the verified submission tree." >&2
  exit 1
fi

git branch -f "${OUTPUT_BRANCH}" "${PUBLICATION_COMMIT}" >/dev/null
echo "Created/updated generated branch '${OUTPUT_BRANCH}' at ${PUBLICATION_COMMIT}." >&2
printf '%s\n' "${PUBLICATION_COMMIT}"
