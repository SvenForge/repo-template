#!/usr/bin/env bash
# Refresh GitLab access after Codex Cloud resumes a cached container.
set -euo pipefail

: "${GITLAB_REPO:?GITLAB_REPO is required}"

readonly GITLAB_HOST="gitlab.com"

repo_root="$(git rev-parse --show-toplevel)"
python -m pip install --requirement "$repo_root/env/dev/requirements.txt"

# The task branch may have been created after setup.sh configured existing branches.
branch="$(git symbolic-ref --quiet --short HEAD || true)"
if [[ -n "$branch" ]]; then
    git config --local "branch.${branch}.remote" origin
    git config --local "branch.${branch}.pushRemote" origin
fi

# Authentication and glab are persisted in the cached environment by setup.sh.
[[ "$(git remote get-url origin)" == "$GITLAB_REPO" ]]
glab auth status --hostname "$GITLAB_HOST" >/dev/null
git ls-remote --exit-code origin HEAD >/dev/null
