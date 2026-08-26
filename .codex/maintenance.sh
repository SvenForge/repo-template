#!/usr/bin/env bash
# Refresh GitLab access after Codex Cloud resumes a cached container.
# Add the following maintenance command to the Codex Cloud Environment configuration:
#   bash .codex/maintenance.sh
set -euo pipefail

readonly GITLAB_HOST="gitlab.com"

# Install Python dependencies (if not already available).
repo_root="$(git rev-parse --show-toplevel)"
python -m pip install --requirement "$repo_root/env/dev/requirements.txt"

# Authentication and glab are persisted in the cached environment by setup.sh.
glab auth status --hostname "$GITLAB_HOST" >/dev/null
git ls-remote --exit-code origin HEAD >/dev/null
