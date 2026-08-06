#!/usr/bin/env bash
# Supply GitLab HTTPS credentials to Git without embedding secrets in URLs.
set -euo pipefail

if [[ -z "${GITLAB_HTTPS_TOKEN:-}" ]]; then
  echo "Error: GITLAB_HTTPS_TOKEN is not configured." >&2
  exit 1
fi

case "${1:-}" in
  *sername*)
    printf '%s\n' 'oauth2'
    ;;
  *assword*)
    printf '%s\n' "${GITLAB_HTTPS_TOKEN}"
    ;;
  *)
    echo "Error: unsupported Git credential prompt." >&2
    exit 1
    ;;
esac
