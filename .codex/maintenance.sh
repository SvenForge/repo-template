#!/usr/bin/env bash
# Refresh GitLab access after Codex Cloud resumes a cached container.
# Add the following maintenance command to the Codex Cloud Environment configuration:
#   bash .codex/maintenance.sh
set -euo pipefail

readonly GITLAB_HOST="gitlab.com"

# Restore the GitLab origin removed by Codex bootstrap after setup.
gitlab_repo="$(git config --local --get codex.gitlabRepo)"
if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$gitlab_repo"
else
    git remote add origin "$gitlab_repo"
fi

# Install Python dependencies when needed.
repo_root="$(git rev-parse --show-toplevel)"
python -m pip install --requirement "$repo_root/env/dev/requirements.txt"

# The task branch may have been created after setup.sh configured existing branches.
branch="$(git symbolic-ref --quiet --short HEAD || true)"
if [[ -n "$branch" ]]; then
    git config --local "branch.${branch}.remote" origin
    git config --local "branch.${branch}.pushRemote" origin
fi

# Authentication and glab are persisted in the cached environment by setup.sh.
glab auth status --hostname "$GITLAB_HOST" >/dev/null
git ls-remote --exit-code origin HEAD >/dev/null
