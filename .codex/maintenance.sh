#!/usr/bin/env bash
# Refresh GitLab access after Codex Cloud resumes a cached container.
set -euo pipefail

readonly GITLAB_HOST="gitlab.com"

repo_root="$(git rev-parse --show-toplevel)"
origin="$(git remote get-url origin 2>/dev/null || true)"
gitlab_repo="${GITLAB_REPO:-$origin}"
[[ "$gitlab_repo" =~ ^https://gitlab\.com/[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)+/?$ ]]

python -m pip install --requirement "$repo_root/env/dev/requirements.txt"

# The task branch may have been created after setup.sh configured existing branches.
branch="$(git symbolic-ref --quiet --short HEAD || true)"
if [[ -n "$branch" ]]; then
    git config --local "branch.${branch}.remote" origin
    git config --local "branch.${branch}.pushRemote" origin
fi

# Authentication and glab are persisted in the cached environment by setup.sh.
[[ "$origin" == "$gitlab_repo" ]]
glab auth status --hostname "$GITLAB_HOST" >/dev/null
git ls-remote --exit-code origin HEAD >/dev/null
