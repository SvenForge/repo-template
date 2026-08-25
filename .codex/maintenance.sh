#!/usr/bin/env bash
# Refresh GitLab access after Codex Cloud resumes a cached container.
# Add the following maintenance command to the Codex Cloud Environment configuration:
#   bash .codex/maintenance.sh
set -euo pipefail

readonly GITLAB_HOST="gitlab.com"

# Restore the origin removed by Codex bootstrap after setup.
origin="$(git remote get-url origin 2>/dev/null || true)"
saved_repo="$(git config --local --get codex.gitlabRepo 2>/dev/null || true)"
gitlab_repo="${GITLAB_REPO:-${saved_repo:-$origin}}"
[[ "$gitlab_repo" =~ ^https://gitlab\.com/[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)+/?$ ]] || {
    printf 'maintenance: setup did not preserve an HTTPS GitLab.com repository URL\n' >&2
    exit 1
}
if [[ -n "$origin" && "$origin" != "$gitlab_repo" ]]; then
    printf 'maintenance: origin does not match the repository preserved by setup\n' >&2
    exit 1
fi
if [[ -z "$origin" ]]; then
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
