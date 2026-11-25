#!/bin/bash
# Publish a release to the AUR (kde-webapp-manager-git).
# Usage: packaging/aur/publish.sh [VERSION]   (defaults to APP_VERSION in constants.py)
# Needs: git SSH access to aur.archlinux.org. The git tag VERSION must already be pushed to GitHub.
set -euo pipefail

ROOT="$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)"
VERSION="${1:-$(sed -n 's/^APP_VERSION: str = "\(.*\)"/\1/p' "$ROOT/webapp_manager/constants.py")}"
AUR_REMOTE="${AUR_REMOTE:-ssh://aur@aur.archlinux.org/kde-webapp-manager-git.git}"

[ -n "$VERSION" ] || { echo "ERROR: could not detect version." >&2; exit 1; }

# The PKGBUILD builds from the git tag, so it has to exist upstream.
git -C "$ROOT" ls-remote --exit-code --tags origin "refs/tags/$VERSION" >/dev/null \
  || { echo "ERROR: tag $VERSION is not on GitHub yet. Push it first." >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

git clone "$AUR_REMOTE" "$WORK/aur"
sed "s/@VERSION@/$VERSION/" "$ROOT/packaging/aur/PKGBUILD.in" > "$WORK/aur/PKGBUILD"
(cd "$WORK/aur" && makepkg --printsrcinfo > .SRCINFO)

cd "$WORK/aur"
if git diff --quiet && [ -z "$(git status --porcelain)" ]; then
  echo "AUR already at $VERSION, nothing to do."
  exit 0
fi
git add PKGBUILD .SRCINFO
git commit -m "Update to $VERSION"
git push origin HEAD:master
echo "=== AUR updated to $VERSION ==="
