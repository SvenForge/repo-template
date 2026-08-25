#!/usr/bin/env bash
# Set up GitLab access for a Codex Cloud environment.
set -euo pipefail

: "${GITLAB_TOKEN:?GITLAB_TOKEN is required}"
: "${GITLAB_REPO:?GITLAB_REPO is required}"

readonly GLAB_VERSION="1.113.0"
readonly GITLAB_HOST="gitlab.com"

die() {
    printf 'setup: %s\n' "$*" >&2
    exit 1
}

glab_version() {
    glab --version 2>/dev/null |
        sed -nE '1s/^glab( version)? ([^[:space:]]+).*/\2/p'
}

# Validate the repository before changing anything.
[[ "$GITLAB_REPO" =~ ^https://gitlab\.com/[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)+/?$ ]] ||
    die "GITLAB_REPO must be an HTTPS GitLab.com repository URL"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
    die "the setup script must run inside a Git worktree"
repo_root="$(git rev-parse --show-toplevel)"

python -m pip install --requirement "$repo_root/env/dev/requirements.txt"

origin="$(git remote get-url origin 2>/dev/null || true)"
mirror="$(git remote get-url mirror 2>/dev/null || true)"
if [[ -n "$origin" && "$origin" != "$GITLAB_REPO" &&
    -n "$mirror" && "$mirror" != "$origin" ]]; then
    die "remote 'mirror' already exists with a different URL"
fi

# Install the pinned glab release when needed.
if [[ "$(glab_version)" != "$GLAB_VERSION" ]]; then
    architecture="$(dpkg --print-architecture)"
    case "$architecture" in
        amd64 | arm64) ;;
        *) die "unsupported Debian architecture for glab: $architecture" ;;
    esac

    package="glab_${GLAB_VERSION}_linux_${architecture}.deb"
    release_url="https://gitlab.com/gitlab-org/cli/-/releases/v${GLAB_VERSION}/downloads"
    tmpdir="$(mktemp -d /tmp/codex-glab.XXXXXX)"
    trap '[[ -z "${tmpdir:-}" ]] || rm -rf -- "$tmpdir"' EXIT

    printf 'Installing glab %s...\n' "$GLAB_VERSION"
    curl -fsSL -o "$tmpdir/$package" "$release_url/$package"
    curl -fsSL -o "$tmpdir/checksums.txt" "$release_url/checksums.txt"
    awk -v package="$package" \
        '$2 == package || $2 == "*" package { print }' \
        "$tmpdir/checksums.txt" |
        (cd "$tmpdir" && sha256sum --check -)
    sudo apt-get install --yes "$tmpdir/$package"

    [[ "$(glab_version)" == "$GLAB_VERSION" ]] ||
        die "glab ${GLAB_VERSION} was not installed successfully"
    rm -rf -- "$tmpdir"
    tmpdir=""
fi

# DEPRECATED: Preserve a different origin as "mirror" for compatibility with legacy GitHub clones. Remove this fallback once those clones are retired.
if [[ -n "$origin" && "$origin" != "$GITLAB_REPO" && -z "$mirror" ]]; then
    git remote rename origin mirror
fi
if git remote get-url origin >/dev/null 2>&1; then
    git config --local --replace-all remote.origin.url "$GITLAB_REPO"
else
    git remote add origin "$GITLAB_REPO"
fi
git config --local --unset-all remote.origin.pushurl >/dev/null 2>&1 || true
git config --local remote.pushDefault origin
git config --local checkout.defaultRemote origin

while IFS= read -r branch; do
    git config --local "branch.${branch}.remote" origin
    git config --local "branch.${branch}.pushRemote" origin
done < <(git for-each-ref --format='%(refname:short)' refs/heads/)

# Persist the PAT, then use glab as this repository's HTTPS credential helper.
without_token=(
    env
    -u GITLAB_TOKEN
    -u GITLAB_ACCESS_TOKEN
    -u OAUTH_TOKEN
    GLAB_NO_PROMPT=1
)
original_umask="$(umask)"
umask 077
printf '%s' "$GITLAB_TOKEN" | "${without_token[@]}" glab auth login \
    --hostname "$GITLAB_HOST" \
    --api-protocol https \
    --git-protocol https \
    --stdin
umask "$original_umask"

"${without_token[@]}" glab config set remote_alias origin

# Headless containers have no OS keyring, so restrict glab's fallback file.
glab_config_dir="${GLAB_CONFIG_DIR:-${XDG_CONFIG_HOME:-"$HOME/.config"}/glab-cli}"
glab_config_file="$glab_config_dir/config.yml"
[[ -f "$glab_config_file" ]] || die "glab did not persist its credentials"
chmod 700 "$glab_config_dir"
chmod 600 "$glab_config_file"

credential_key="credential.https://${GITLAB_HOST}.helper"
git config --local --unset-all "$credential_key" >/dev/null 2>&1 || true
git config --local --add "$credential_key" ""
git config --local --add "$credential_key" \
    "!$(command -v glab) auth git-credential"

# Verify persisted authentication and read access without performing a push.
[[ "$(git remote get-url origin)" == "$GITLAB_REPO" ]]
[[ "$(git remote get-url --push origin)" == "$GITLAB_REPO" ]]
"${without_token[@]}" glab auth status --hostname "$GITLAB_HOST" >/dev/null
"${without_token[@]}" git ls-remote --exit-code origin HEAD >/dev/null

printf 'Verified glab %s, GitLab authentication, and origin %s.\n' \
    "$GLAB_VERSION" "$GITLAB_REPO"
