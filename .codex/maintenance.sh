#!/usr/bin/env bash
# Refresh a Codex Cloud environment after a cached container resumes.
# Add the following maintenance command to the Codex Cloud Environment configuration:
#   bash .codex/maintenance.sh
set -euo pipefail

# Refresh the Python project and/or its development dependency group.
python -m pip install --upgrade pip
python -m pip install --group dev

# Authentication and glab are persisted in the cached environment by setup.sh.
readonly GITLAB_HOST="gitlab.com"
glab auth status --hostname "$GITLAB_HOST" >/dev/null
