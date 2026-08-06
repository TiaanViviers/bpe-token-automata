#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
ASKPASS="${REPO_ROOT}/scripts/gitlab_https_askpass.sh"
DUMMY_TOKEN='not-a-real-token'

test "$(GITLAB_HTTPS_TOKEN="${DUMMY_TOKEN}" "${ASKPASS}" 'Username for HTTPS')" = 'oauth2'
test "$(GITLAB_HTTPS_TOKEN="${DUMMY_TOKEN}" "${ASKPASS}" 'Password for HTTPS')" = "${DUMMY_TOKEN}"

if env -u GITLAB_HTTPS_TOKEN "${ASKPASS}" 'Password for HTTPS' >/dev/null 2>&1; then
  echo "Error: askpass accepted a missing token." >&2
  exit 1
fi

if GITLAB_HTTPS_TOKEN="${DUMMY_TOKEN}" "${ASKPASS}" 'Unexpected prompt' >/dev/null 2>&1; then
  echo "Error: askpass accepted an unexpected prompt." >&2
  exit 1
fi

echo "GitLab HTTPS askpass tests passed."
